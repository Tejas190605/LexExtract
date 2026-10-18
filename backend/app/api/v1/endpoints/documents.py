import os
import json
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request, status, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.core.roles import Role
from app.core.audit_actions import AuditAction
from app.core.deps import get_current_user, check_document_access, get_client_ip
from app.models.document import Document
from app.models.user import User
from app.schemas.document import (
    DocumentResponse,
    DocumentUploadResponse,
    DocumentTextResponse,
    PageContent,
)
from app.schemas.insights import (
    DocumentSearchResponse,
    DocumentCompareRequest,
    DocumentCompareResponse,
)
from app.models.analysis import AnalysisRun
from app.services.clause_obligation_service import search_document_text, compare_two_documents
from app.services.document_processing_service import process_uploaded_document
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and process legal document (.pdf, .docx)"
)
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ingests and extracts text from a PDF or DOCX document.
    Enforces authentication and attributes document ownership to current_user.
    Records DOCUMENT_UPLOAD in audit ledger.
    """
    ip = get_client_ip(request)

    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Filename missing.")

    try:
        file_bytes = await file.read()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read uploaded stream: {exc}"
        )

    try:
        doc_record, summary = process_uploaded_document(
            filename=file.filename,
            content_type=file.content_type,
            file_bytes=file_bytes,
            db=db,
            user_id=current_user.id
        )

        AuditService.record_audit_event(
            db=db,
            action=AuditAction.DOCUMENT_UPLOAD,
            user_id=current_user.id,
            resource_type="DOCUMENT",
            resource_id=doc_record.id,
            status="SUCCESS",
            details=f"Uploaded '{doc_record.filename}' ({doc_record.file_type}, {doc_record.word_count} words)",
            ip_address=ip
        )

        return DocumentUploadResponse(
            id=doc_record.id,
            filename=doc_record.filename,
            file_type=doc_record.file_type,
            file_size=doc_record.file_size,
            page_count=doc_record.page_count,
            word_count=doc_record.word_count,
            status=doc_record.status,
            message=summary.get("message", "Document processed successfully.")
        )
    except ValueError as val_err:
        err_msg = str(val_err)
        AuditService.record_audit_event(
            db=db,
            action=AuditAction.DOCUMENT_UPLOAD,
            user_id=current_user.id,
            resource_type="DOCUMENT",
            status="FAILURE",
            details=f"Upload rejected: {err_msg}",
            ip_address=ip
        )
        if "exceeds" in err_msg.lower():
            raise HTTPException(status_code=413, detail=err_msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_msg)
    except Exception as exc:
        logger.error(f"Internal ingestion error: {exc}", exc_info=True)
        AuditService.record_audit_event(
            db=db,
            action=AuditAction.DOCUMENT_UPLOAD,
            user_id=current_user.id,
            resource_type="DOCUMENT",
            status="FAILURE",
            details=f"Internal processing failure: {exc}",
            ip_address=ip
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document processing failed: {exc}"
        )


@router.get("/", response_model=List[DocumentResponse], summary="List ingested documents")
def list_documents(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns list of documents.
    Enforces isolation: Non-admin users see only their own documents; Admins see all documents.
    """
    if Role.normalize(current_user.role) == Role.ADMIN.value:
        documents = db.query(Document).offset(skip).limit(limit).all()
    else:
        documents = db.query(Document).filter(
            (Document.user_id == current_user.id) | (Document.owner_id == current_user.id)
        ).offset(skip).limit(limit).all()
    return documents


@router.post("/compare", response_model=DocumentCompareResponse, summary="Compare two documents side-by-side")
def compare_documents_endpoint(
    payload: DocumentCompareRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Compares two documents:
    1. Validates ownership access to both doc A and doc B (403 if unauthorized)
    2. Computes ASTMA TF-IDF Cosine Similarity
    3. Compares metadata, keywords, entities, clauses, dates, money, and obligations
    4. Records DOCUMENT_COMPARE in audit log
    """
    ip = get_client_ip(request)
    doc_a = db.query(Document).filter(Document.id == payload.doc_a_id).first()
    if not doc_a:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document {payload.doc_a_id} not found")
    
    doc_b = db.query(Document).filter(Document.id == payload.doc_b_id).first()
    if not doc_b:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document {payload.doc_b_id} not found")

    # Enforce access control for both documents
    check_document_access(doc_a, current_user, db, ip_address=ip)
    check_document_access(doc_b, current_user, db, ip_address=ip)

    # Fetch latest completed analysis runs if available
    analysis_a = db.query(AnalysisRun).filter(
        AnalysisRun.document_id == doc_a.id,
        AnalysisRun.status == "completed"
    ).order_by(AnalysisRun.created_at.desc()).first()

    analysis_b = db.query(AnalysisRun).filter(
        AnalysisRun.document_id == doc_b.id,
        AnalysisRun.status == "completed"
    ).order_by(AnalysisRun.created_at.desc()).first()

    comparison_result = compare_two_documents(doc_a, analysis_a, doc_b, analysis_b)

    AuditService.record_audit_event(
        db=db,
        action=AuditAction.DOCUMENT_COMPARE,
        user_id=current_user.id,
        resource_type="DOCUMENT",
        resource_id=doc_a.id,
        status="SUCCESS",
        details=f"Compared '{doc_a.filename}' with '{doc_b.filename}' (similarity: {comparison_result['similarity_percentage']}%)",
        ip_address=ip
    )

    return comparison_result


@router.get("/{document_id}", response_model=DocumentResponse, summary="Get document metadata by ID")
def get_document(
    document_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves document metadata by ID.
    Enforces document ownership check (403 on cross-user access).
    """
    ip = get_client_ip(request)
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    check_document_access(doc, current_user, db, ip_address=ip)

    AuditService.record_audit_event(
        db=db,
        action=AuditAction.DOCUMENT_VIEW,
        user_id=current_user.id,
        resource_type="DOCUMENT",
        resource_id=doc.id,
        status="SUCCESS",
        details=f"Viewed metadata for '{doc.filename}'",
        ip_address=ip
    )

    return doc


@router.get("/{document_id}/text", response_model=DocumentTextResponse, summary="Get extracted document text")
def get_document_text(
    document_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves full normalized text and page-by-page structured segments.
    Enforces document ownership check (403 on cross-user access).
    """
    ip = get_client_ip(request)
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    check_document_access(doc, current_user, db, ip_address=ip)

    AuditService.record_audit_event(
        db=db,
        action=AuditAction.DOCUMENT_VIEW,
        user_id=current_user.id,
        resource_type="DOCUMENT",
        resource_id=doc.id,
        status="SUCCESS",
        details=f"Extracted text requested for '{doc.filename}'",
        ip_address=ip
    )

    pages: List[PageContent] = []
    if doc.pages_json:
        try:
            raw_pages = json.loads(doc.pages_json)
            for p in raw_pages:
                pages.append(PageContent(
                    page_number=p.get("page_number", 1),
                    text=p.get("text", "")
                ))
        except Exception:
            pass

    if not pages and doc.extracted_text:
        pages.append(PageContent(page_number=1, text=doc.extracted_text))

    return DocumentTextResponse(
        document_id=doc.id,
        filename=doc.filename,
        page_count=doc.page_count,
        word_count=doc.word_count,
        text=doc.extracted_text or "",
        pages=pages
    )


@router.get("/{document_id}/search", response_model=DocumentSearchResponse, summary="Search within document text with ASTMA relevance scoring")
def search_document_endpoint(
    document_id: int,
    request: Request,
    q: str = Query(..., min_length=1, max_length=200, description="Search term or phrase"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    In-document search operating across document pages and sections:
    1. Validates document ownership (403 on unauthorized access)
    2. Performs case-insensitive matching across text segments
    3. Computes ASTMA TF-IDF passage relevance ranking
    4. Records DOCUMENT_SEARCH in audit log
    """
    ip = get_client_ip(request)
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    check_document_access(doc, current_user, db, ip_address=ip)

    search_result = search_document_text(doc, q)

    AuditService.record_audit_event(
        db=db,
        action=AuditAction.DOCUMENT_SEARCH,
        user_id=current_user.id,
        resource_type="DOCUMENT",
        resource_id=doc.id,
        status="SUCCESS",
        details=f"Searched '{q}' in '{doc.filename}' ({search_result['total_matches']} matches)",
        ip_address=ip
    )

    return search_result


@router.get("/{document_id}/file", summary="Stream or download original document file (.pdf, .docx)")
def get_document_file(
    document_id: int,
    request: Request,
    download: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Streams the original uploaded document for inline viewing or download.
    Enforces document ownership check (403 on cross-user access).
    """
    ip = get_client_ip(request)
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    check_document_access(doc, current_user, db, ip_address=ip)

    file_path = os.path.join(settings.UPLOAD_DIR, doc.stored_filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stored document file not found on disk")

    AuditService.record_audit_event(
        db=db,
        action=AuditAction.DOCUMENT_VIEW,
        user_id=current_user.id,
        resource_type="DOCUMENT",
        resource_id=doc.id,
        status="SUCCESS",
        details=f"{'Downloaded' if download else 'Previewed'} file '{doc.filename}'",
        ip_address=ip
    )

    media_type = "application/pdf" if doc.file_type.lower() == "pdf" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    content_disposition = f"{'attachment' if download else 'inline'}; filename=\"{doc.filename}\""

    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=doc.filename,
        headers={"Content-Disposition": content_disposition}
    )

