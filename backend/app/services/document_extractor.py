from typing import Dict, Any
from app.services.pdf_extractor import extract_pdf_text
from app.services.docx_extractor import extract_docx_text


def extract_document(file_path: str, file_type: str) -> Dict[str, Any]:
    """
    Unified entry point for document extraction.
    Delegates to PDF or DOCX extractor based on normalized file_type.
    """
    normalized_type = file_type.lower().strip()

    if normalized_type == "pdf":
        return extract_pdf_text(file_path)
    elif normalized_type == "docx":
        return extract_docx_text(file_path)
    else:
        raise ValueError(f"Unsupported file type for extraction: {file_type}")
