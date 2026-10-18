import os
import uuid
import hashlib
from typing import Tuple
from app.core.config import settings


def compute_sha256(content: bytes) -> str:
    """Calculates SHA-256 hex digest for document integrity and deduplication."""
    return hashlib.sha256(content).hexdigest()


def save_uploaded_file(filename: str, content: bytes) -> Tuple[str, str, str]:
    """
    Saves file bytes to backend/storage/uploads/ using a secure randomized UUID filename.
    Guarantees path traversal prevention.
    Returns: (stored_filename, absolute_file_path, sha256_hash)
    """
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    # Extract extension safely
    _, ext = os.path.splitext(filename)
    safe_ext = ext.lower() if ext.lower() in [".pdf", ".docx"] else ".bin"

    # Generate unique stored filename
    unique_id = uuid.uuid4().hex
    stored_filename = f"{unique_id}{safe_ext}"

    # Target path inside storage directory
    dest_path = os.path.abspath(os.path.join(settings.UPLOAD_DIR, stored_filename))

    # Security check: Ensure resolved destination path stays strictly inside UPLOAD_DIR
    upload_dir_abs = os.path.abspath(settings.UPLOAD_DIR)
    if not dest_path.startswith(upload_dir_abs):
        raise ValueError("Invalid storage path: Path traversal detected.")

    # Write file content
    with open(dest_path, "wb") as f:
        f.write(content)

    # Compute hash
    file_hash = compute_sha256(content)

    return stored_filename, dest_path, file_hash


def get_stored_file_path(stored_filename: str) -> str:
    """Returns absolute path to a stored file, verifying boundary safety."""
    path = os.path.abspath(os.path.join(settings.UPLOAD_DIR, stored_filename))
    upload_dir_abs = os.path.abspath(settings.UPLOAD_DIR)
    if not path.startswith(upload_dir_abs):
        raise ValueError("Path traversal violation.")
    return path
