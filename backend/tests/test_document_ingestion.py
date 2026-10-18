import os
import io
import json
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.core.database import Base, get_db
from app.models.user import User
from app.models.document import Document
from app.services.text_preprocessor import normalize_legal_text, tokenize_legal_text, calculate_word_count
from app.services.document_validator import validate_file
from app.services.file_storage import compute_sha256
from app.services.pdf_extractor import extract_pdf_text
from app.services.docx_extractor import extract_docx_text
from main import app

# Test SQLite in-memory engine with StaticPool
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    """Create fresh database tables for each test and tear down after."""
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        # Seed demo user required for document ownership
        demo_user = User(
            name="Demo User",
            email="demo@lexextract.local",
            password_hash="test_hash",
            role="user"
        )
        session.add(demo_user)
        session.commit()
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    """TestClient that overrides get_db dependency with test database session."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    def override_get_current_user():
        from app.core.deps import get_current_user
        user = db_session.query(User).first()
        if not user:
            user = User(username="demo", email="demo@lexextract.local", full_name="Demo User", password_hash="h", role="USER")
            db_session.add(user)
            db_session.commit()
        return user

    from app.core.deps import get_current_user
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()


# Unit Tests: Preprocessing & Legal Preservation

def test_legal_text_normalization_preserves_citations():
    """Verify Section 10(2), Article 14, and currency values survive normalization."""
    raw = "Pursuant to  Section 10(2)   of the Act and   Article 14,  the sum of  Rs. 50,000  is due.\n\n\n\nNext clause."
    cleaned = normalize_legal_text(raw)
    assert "Section 10(2)" in cleaned
    assert "Article 14" in cleaned
    assert "Rs. 50,000" in cleaned
    assert "\n\n\n" not in cleaned


def test_legal_tokenizer():
    """Verify tokenizer identifies legal citation constructs."""
    text = "Under Section 302 of IPC and Article 226, fine is Rs. 10,000 on 15/08/2025."
    tokens = tokenize_legal_text(text)
    assert any("Section 302" in t for t in tokens)
    assert any("Article 226" in t for t in tokens)
    assert any("Rs. 10,000" in t for t in tokens)


def test_word_count_calculation():
    """Verify word count logic accurately counts words."""
    assert calculate_word_count("One two three four five.") == 5
    assert calculate_word_count("") == 0


def test_file_validator_rules():
    """Verify file validation logic for extensions, size, and emptiness."""
    # Empty file
    valid, msg, _ = validate_file("doc.pdf", "application/pdf", 0)
    assert not valid and "empty" in msg.lower()

    # Unsupported extension
    valid, msg, _ = validate_file("malicious.exe", "application/octet-stream", 100)
    assert not valid and "unsupported" in msg.lower()

    # Oversized file (>10MB)
    valid, msg, _ = validate_file("huge.pdf", "application/pdf", 11 * 1024 * 1024)
    assert not valid and "exceeds" in msg.lower()

    # Valid PDF
    valid, msg, ftype = validate_file("contract.pdf", "application/pdf", 2048)
    assert valid and ftype == "pdf"


# Integration API Tests

def test_upload_valid_pdf(client):
    """Verify uploading a valid PDF document extracts text, calculates word count, and persists."""
    sample_pdf_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", "..", "sample_documents", "sample_contract.pdf"
    ))
    assert os.path.exists(sample_pdf_path), "sample_contract.pdf missing"

    with open(sample_pdf_path, "rb") as f:
        file_bytes = f.read()

    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("sample_contract.pdf", io.BytesIO(file_bytes), "application/pdf")}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "sample_contract.pdf"
    assert data["file_type"] == "pdf"
    assert data["status"] == "completed"
    assert data["page_count"] == 2
    assert data["word_count"] > 100
    assert "id" in data


def test_upload_valid_docx(client):
    """Verify uploading a valid DOCX document extracts text and leaves page_count as null."""
    sample_docx_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", "..", "sample_documents", "sample_legal_notice.docx"
    ))
    assert os.path.exists(sample_docx_path), "sample_legal_notice.docx missing"

    with open(sample_docx_path, "rb") as f:
        file_bytes = f.read()

    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("sample_legal_notice.docx", io.BytesIO(file_bytes), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "sample_legal_notice.docx"
    assert data["file_type"] == "docx"
    assert data["status"] == "completed"
    assert data["page_count"] is None  # DOCX must not fabricate page count
    assert data["word_count"] > 50


def test_upload_unsupported_extension(client):
    """Verify uploading .txt file returns HTTP 400 Bad Request."""
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("notes.txt", io.BytesIO(b"Legal notes"), "text/plain")}
    )
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


def test_upload_empty_file(client):
    """Verify uploading empty file returns HTTP 400 Bad Request."""
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("empty.pdf", io.BytesIO(b""), "application/pdf")}
    )
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_upload_oversized_file(client):
    """Verify uploading file >10MB returns HTTP 413 Payload Too Large."""
    oversized_bytes = b"0" * (10 * 1024 * 1024 + 1)
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("huge.pdf", io.BytesIO(oversized_bytes), "application/pdf")}
    )
    assert response.status_code == 413
    assert "exceeds" in response.json()["detail"].lower()


def test_get_document_metadata_and_text_endpoints(client):
    """Verify document metadata and extracted text retrieval endpoints."""
    sample_pdf_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", "..", "sample_documents", "sample_contract.pdf"
    ))
    with open(sample_pdf_path, "rb") as f:
        file_bytes = f.read()

    upload_res = client.post(
        "/api/v1/documents/upload",
        files={"file": ("sample_contract.pdf", io.BytesIO(file_bytes), "application/pdf")}
    )
    doc_id = upload_res.json()["id"]

    # Test metadata endpoint: GET /api/v1/documents/{id}
    meta_res = client.get(f"/api/v1/documents/{doc_id}")
    assert meta_res.status_code == 200
    meta = meta_res.json()
    assert meta["id"] == doc_id
    assert meta["filename"] == "sample_contract.pdf"
    # Ensure physical absolute path is NOT leaked in response schema
    assert "file_path" not in meta
    assert "dest_path" not in meta

    # Test text endpoint: GET /api/v1/documents/{id}/text
    text_res = client.get(f"/api/v1/documents/{doc_id}/text")
    assert text_res.status_code == 200
    text_data = text_res.json()
    assert text_data["document_id"] == doc_id
    assert "COMMERCIAL LEASE AGREEMENT" in text_data["text"]
    assert len(text_data["pages"]) == 2
    assert text_data["pages"][0]["page_number"] == 1


def test_corrupt_pdf_handled_gracefully(client):
    """Verify corrupt PDF content raises HTTP 400/422 without server crash."""
    corrupt_bytes = b"%PDF-1.4 Corrupt binary garbage that is not a valid PDF stream"
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("corrupt.pdf", io.BytesIO(corrupt_bytes), "application/pdf")}
    )
    assert response.status_code in (400, 422)
    assert "corrupt" in response.json()["detail"].lower()


def test_corrupt_docx_handled_gracefully(client):
    """Verify corrupt DOCX content raises HTTP 400 without server crash."""
    corrupt_bytes = b"Not a zip file or docx archive"
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("corrupt.docx", io.BytesIO(corrupt_bytes), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    )
    assert response.status_code in (400, 422)
    assert "corrupt" in response.json()["detail"].lower()


def test_nonexistent_document_text_returns_404(client):
    """Verify querying text for nonexistent document ID returns HTTP 404."""
    response = client.get("/api/v1/documents/999999/text")
    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found"
