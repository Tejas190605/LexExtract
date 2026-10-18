import json
import logging
from typing import Tuple, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.document import Document
from app.models.user import User
from app.services.document_validator import validate_file
from app.services.file_storage import save_uploaded_file
from app.services.document_extractor import extract_document
from app.services.text_preprocessor import preprocess_document_text

logger = logging.getLogger(__name__)


def get_default_demo_user(db: Session) -> User:
    """
    Retrieves or creates the development demonstration user.
    Used for document ownership prior to Phase 6 authentication implementation.
    """
    user = db.query(User).filter(User.email == "demo@lexextract.local").first()
    if not user:
        user = User(
            name="Demo User",
            email="demo@lexextract.local",
            password_hash="placeholder_hash_phase3",
            role="user",
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def process_uploaded_document(
    filename: str,
    content_type: Optional[str],
    file_bytes: bytes,
    db: Session,
    user_id: Optional[int] = None
) -> Tuple[Document, Dict[str, Any]]:
    """
    Complete orchestrated pipeline:
    1. Validation (extension, MIME, size, emptiness)
    2. Secure file persistence & SHA-256 calculation
    3. Text stream extraction (PyMuPDF / python-docx)
    4. Legal text normalization & word count calculation
    5. Database record creation & status management
    """
    file_size = len(file_bytes)

    # 1. Validation
    is_valid, error_msg, file_type = validate_file(filename, content_type, file_size)
    if not is_valid:
        raise ValueError(error_msg)

    # Resolve document owner (Demo user if unauthenticated in Phase 3)
    if not user_id:
        demo_user = get_default_demo_user(db)
        user_id = demo_user.id

    # 2. File Storage & Hash
    stored_filename, file_path, file_hash = save_uploaded_file(filename, file_bytes)

    # Initial Document DB Record with status 'processing'
    doc_record = Document(
        user_id=user_id,
        filename=filename,
        stored_filename=stored_filename,
        file_type=file_type,
        file_size=file_size,
        file_hash=file_hash,
        page_count=None,
        word_count=0,
        status="processing",
    )
    db.add(doc_record)
    db.commit()
    db.refresh(doc_record)

    # 3. Extraction & 4. Preprocessing
    try:
        raw_extraction = extract_document(file_path, file_type)
        preprocessing_result = preprocess_document_text(
            raw_extraction.get("raw_text", ""),
            raw_extraction.get("pages", [])
        )

        cleaned_text = preprocessing_result["cleaned_text"]
        word_count = preprocessing_result["word_count"]
        page_count = raw_extraction.get("page_count")  # Int for PDF, None for DOCX
        pages_json = json.dumps(preprocessing_result["cleaned_pages"])

        # Update Document record to 'completed'
        doc_record.page_count = page_count
        doc_record.word_count = word_count
        doc_record.extracted_text = cleaned_text
        doc_record.pages_json = pages_json
        doc_record.status = "completed"

        db.commit()
        db.refresh(doc_record)

        summary = {
            "message": "Document processed successfully.",
            "warning": raw_extraction.get("warning"),
            "sample_tokens": preprocessing_result["sample_tokens"]
        }
        return doc_record, summary

    except Exception as exc:
        logger.error(f"Processing failed for document {doc_record.id}: {exc}", exc_info=True)
        doc_record.status = "failed"
        db.commit()
        db.refresh(doc_record)
        raise exc
