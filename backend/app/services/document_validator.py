import os
from typing import Tuple, Optional
from app.core.config import settings

ALLOWED_EXTENSIONS = {".pdf", ".docx"}

ALLOWED_MIME_TYPES = {
    # PDF MIME types
    "application/pdf",
    "application/x-pdf",
    # DOCX MIME types
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
    "application/x-docx",
    # Fallback MIME types commonly reported by browsers for binary formats
    "application/octet-stream",
    "application/zip",
}


def validate_file(
    filename: Optional[str],
    content_type: Optional[str],
    file_size: int
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validates an uploaded file by extension, MIME type, emptiness, and file size limit.
    Returns: (is_valid, error_message, normalized_file_type)
    """
    if not filename:
        return False, "Filename cannot be empty.", None

    # Check file emptiness
    if file_size <= 0:
        return False, "Uploaded file is empty.", None

    # Check maximum allowed file size
    if file_size > settings.MAX_UPLOAD_SIZE_BYTES:
        max_mb = settings.MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)
        return False, f"File exceeds the maximum allowed size of {max_mb} MB.", None

    # Validate extension
    _, ext = os.path.splitext(filename)
    ext_lower = ext.lower()

    if ext_lower not in ALLOWED_EXTENSIONS:
        return (
            False,
            "Unsupported file type. Only PDF and DOCX files are allowed.",
            None,
        )

    normalized_type = "pdf" if ext_lower == ".pdf" else "docx"

    # Validate MIME/content type if provided
    if content_type:
        clean_content_type = content_type.split(";")[0].strip().lower()
        if clean_content_type not in ALLOWED_MIME_TYPES:
            return (
                False,
                f"Unsupported content type ({content_type}). Only PDF and DOCX documents are accepted.",
                None,
            )

    return True, None, normalized_type
