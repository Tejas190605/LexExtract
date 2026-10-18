"""
LexExtract Services Package.
"""

from app.services.document_validator import validate_file
from app.services.file_storage import save_uploaded_file, get_stored_file_path, compute_sha256
from app.services.pdf_extractor import extract_pdf_text
from app.services.docx_extractor import extract_docx_text
from app.services.document_extractor import extract_document
from app.services.text_preprocessor import (
    normalize_legal_text,
    tokenize_legal_text,
    calculate_word_count,
    preprocess_document_text,
)
from app.services.document_processing_service import (
    process_uploaded_document,
    get_default_demo_user,
)

__all__ = [
    "validate_file",
    "save_uploaded_file",
    "get_stored_file_path",
    "compute_sha256",
    "extract_pdf_text",
    "extract_docx_text",
    "extract_document",
    "normalize_legal_text",
    "tokenize_legal_text",
    "calculate_word_count",
    "preprocess_document_text",
    "process_uploaded_document",
    "get_default_demo_user",
]
