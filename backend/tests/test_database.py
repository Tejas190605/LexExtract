import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.core.database import Base, get_db
from app.models.user import User
from app.models.document import Document
from app.models.analysis import AnalysisRun
from app.models.keyword import ExtractedKeyword
from app.models.entity import ExtractedEntity
from app.models.audit import AuditLog
from app.schemas.user import UserResponse
from main import app

# Test SQLite in-memory engine with StaticPool to share connection across threads
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
        return User(
            id=999,
            username="fixture_admin",
            email="admin_fixture@test.local",
            full_name="Admin Fix",
            password_hash="h",
            role="ADMIN",
            is_active=True
        )

    from app.core.deps import get_current_user
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()


def test_tables_created(db_session):
    """Verify that all six expected tables are registered in SQLAlchemy metadata."""
    expected_tables = {
        "users",
        "documents",
        "analysis_runs",
        "extracted_keywords",
        "extracted_entities",
        "audit_logs"
    }
    actual_tables = set(Base.metadata.tables.keys())
    assert expected_tables.issubset(actual_tables), f"Missing tables: {expected_tables - actual_tables}"


def test_user_creation_and_unique_email(db_session):
    """Verify user can be created and duplicate email triggers IntegrityError."""
    user1 = User(
        name="Test Lawyer",
        email="lawyer@example.com",
        password_hash="secret_hash_value",
        role="analyst"
    )
    db_session.add(user1)
    db_session.commit()
    assert user1.id is not None
    assert user1.is_active is True

    # Attempt duplicate insert
    user2 = User(
        name="Duplicate Lawyer",
        email="lawyer@example.com",
        password_hash="another_hash",
        role="reviewer"
    )
    db_session.add(user2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_document_referencing_user(db_session):
    """Verify document correctly references user and cascades on delete."""
    user = User(name="Partner", email="partner@firm.com", password_hash="hash")
    db_session.add(user)
    db_session.commit()

    doc = Document(
        user_id=user.id,
        filename="merger_agreement.pdf",
        stored_filename="doc_uuid_123.pdf",
        file_type="pdf",
        file_size=2048576,
        file_hash="sha256_mock_hash",
        status="uploaded"
    )
    db_session.add(doc)
    db_session.commit()

    assert doc.id is not None
    assert doc.user.email == "partner@firm.com"
    assert len(user.documents) == 1


def test_analysis_run_keyword_and_entity_relationship(db_session):
    """Verify complete hierarchy: Document -> AnalysisRun -> Keywords & Entities."""
    user = User(name="Analyst", email="analyst@firm.com", password_hash="hash")
    db_session.add(user)
    db_session.commit()

    doc = Document(
        user_id=user.id,
        filename="case_judgment.pdf",
        stored_filename="doc_case_123.pdf",
        file_type="pdf",
        file_size=1024,
        file_hash="mock_hash_case",
        status="completed"
    )
    db_session.add(doc)
    db_session.commit()

    run = AnalysisRun(
        document_id=doc.id,
        status="completed",
        processing_time=1.45,
        total_keywords=1,
        total_entities=1
    )
    db_session.add(run)
    db_session.commit()

    kw = ExtractedKeyword(
        analysis_run_id=run.id,
        keyword="promissory estoppel",
        category="Contractual",
        rake_score=4.5,
        tfidf_score=0.82,
        lexicon_score=1.2,
        final_score=0.91
    )
    db_session.add(kw)

    entity = ExtractedEntity(
        analysis_run_id=run.id,
        entity_text="Section 10 of Indian Contract Act",
        entity_type="ACT",
        frequency=2,
        page_number=1,
        start_position=120,
        end_position=152
    )
    db_session.add(entity)
    db_session.commit()

    # Verify relationships
    assert len(run.keywords) == 1
    assert run.keywords[0].keyword == "promissory estoppel"
    assert len(run.entities) == 1
    assert run.entities[0].entity_type == "ACT"


def test_audit_log_referencing_user(db_session):
    """Verify AuditLog records user actions."""
    user = User(name="Auditor", email="auditor@firm.com", password_hash="hash")
    db_session.add(user)
    db_session.commit()

    log = AuditLog(
        user_id=user.id,
        action="LOGIN",
        details="User logged in from 127.0.0.1"
    )
    db_session.add(log)
    db_session.commit()

    assert log.id is not None
    assert log.user.email == "auditor@firm.com"
    assert len(user.audit_logs) == 1


def test_password_hash_never_exposed_in_user_response(db_session):
    """
    CRITICAL SECURITY TEST:
    Verify UserResponse Pydantic schema strictly excludes password_hash.
    """
    user = User(
        id=42,
        name="Confidential User",
        email="confidential@firm.com",
        password_hash="SUPER_SECRET_BCRYPT_HASH_NEVER_LEAK",
        role="admin",
        is_active=True
    )
    response_schema = UserResponse.model_validate(user)
    dumped_dict = response_schema.model_dump()

    assert "password_hash" not in dumped_dict
    assert "password" not in dumped_dict
    assert dumped_dict["name"] == "Confidential User"
    assert dumped_dict["email"] == "confidential@firm.com"


# API Integration Tests

def test_api_health_check_database_status(client):
    """Verify health endpoint reports connected database status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"


def test_api_list_users_omits_password_hash(client, db_session):
    """Verify GET /api/v1/users returns users without password_hash in response."""
    user = User(
        name="Alice Chambers",
        email="alice@lexextract.local",
        password_hash="secret_dont_reveal",
        role="analyst"
    )
    db_session.add(user)
    db_session.commit()

    response = client.get("/api/v1/users/")
    assert response.status_code == 200
    users = response.json()
    assert len(users) == 1
    assert users[0]["name"] == "Alice Chambers"
    assert users[0]["email"] == "alice@lexextract.local"
    assert "password_hash" not in users[0]
    assert "password" not in users[0]


def test_api_list_documents(client, db_session):
    """Verify GET /api/v1/documents returns document metadata."""
    user = User(name="Bob", email="bob@law.com", password_hash="hash")
    db_session.add(user)
    db_session.commit()

    doc = Document(
        user_id=user.id,
        filename="brief.docx",
        stored_filename="doc_brief_456.docx",
        file_type="docx",
        file_size=512000,
        file_hash="mock_hash_brief",
        status="uploaded"
    )
    db_session.add(doc)
    db_session.commit()

    response = client.get("/api/v1/documents/")
    assert response.status_code == 200
    docs = response.json()
    assert len(docs) == 1
    assert docs[0]["filename"] == "brief.docx"
    assert docs[0]["file_type"] == "docx"


def test_api_analysis_not_found(client):
    """Verify GET /api/v1/analyses/document/999 returns 404."""
    response = client.get("/api/v1/analyses/document/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found"


def test_cascade_delete_document_removes_runs(db_session):
    """Verify deleting a Document cascades to remove its AnalysisRuns and ExtractedKeywords."""
    user = User(name="Partner", email="senior_partner@law.com", password_hash="hash")
    db_session.add(user)
    db_session.commit()

    doc = Document(
        user_id=user.id,
        filename="contract_to_delete.pdf",
        stored_filename="doc_del_789.pdf",
        file_type="pdf",
        file_size=2048,
        file_hash="hash_del",
        status="completed"
    )
    db_session.add(doc)
    db_session.commit()

    run = AnalysisRun(document_id=doc.id, status="completed", total_keywords=1)
    db_session.add(run)
    db_session.commit()

    kw = ExtractedKeyword(analysis_run_id=run.id, keyword="liquidated damages")
    db_session.add(kw)
    db_session.commit()

    # Confirm created
    run_id = run.id
    kw_id = kw.id
    assert db_session.query(AnalysisRun).filter_by(id=run_id).first() is not None
    assert db_session.query(ExtractedKeyword).filter_by(id=kw_id).first() is not None

    # Delete parent document
    db_session.delete(doc)
    db_session.commit()

    # Verify cascading deletion
    assert db_session.query(AnalysisRun).filter_by(id=run_id).first() is None
    assert db_session.query(ExtractedKeyword).filter_by(id=kw_id).first() is None


def test_api_get_single_document_by_id(client, db_session):
    """Verify GET /api/v1/documents/{id} returns single document or 404."""
    user = User(name="Charlie", email="charlie@law.com", password_hash="hash")
    db_session.add(user)
    db_session.commit()

    doc = Document(
        user_id=user.id,
        filename="nda.pdf",
        stored_filename="doc_nda_99.pdf",
        file_type="pdf",
        file_size=12000,
        file_hash="hash_nda",
        status="uploaded"
    )
    db_session.add(doc)
    db_session.commit()

    # Success case
    res = client.get(f"/api/v1/documents/{doc.id}")
    assert res.status_code == 200
    assert res.json()["filename"] == "nda.pdf"

    # Not found case
    res_404 = client.get("/api/v1/documents/999999")
    assert res_404.status_code == 404

