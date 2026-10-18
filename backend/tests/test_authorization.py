import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.core.database import Base, get_db
from app.core.security import hash_password, create_access_token
from app.models.user import User
from app.models.document import Document
from app.models.analysis import AnalysisRun
from app.models.keyword import ExtractedKeyword
from app.models.entity import ExtractedEntity
from main import app

test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()


def make_auth_header(user: User) -> dict:
    token = create_access_token({
        "sub": str(user.id),
        "email": user.email,
        "role": user.role
    })
    return {"Authorization": f"Bearer {token}"}


def test_unauthenticated_protected_endpoint_returns_401(client):
    """Verify accessing protected routes without Bearer token returns 401."""
    assert client.get("/api/v1/documents/").status_code == 401
    assert client.get("/api/v1/documents/1").status_code == 401
    assert client.get("/api/v1/users/").status_code == 401
    assert client.get("/api/v1/admin/audit-logs").status_code == 401


def test_normal_user_cannot_access_admin_endpoints(client, db_session):
    """Verify USER role receives HTTP 403 on admin-only endpoints."""
    user = User(
        username="normal_user",
        email="user@firm.com",
        full_name="Normal User",
        password_hash=hash_password("Pass123!"),
        role="USER"
    )
    db_session.add(user)
    db_session.commit()

    headers = make_auth_header(user)
    assert client.get("/api/v1/users/", headers=headers).status_code == 403
    assert client.get("/api/v1/admin/audit-logs", headers=headers).status_code == 403
    assert client.patch(f"/api/v1/users/{user.id}/status", json={"is_active": False}, headers=headers).status_code == 403


def test_analyst_cannot_access_admin_endpoints(client, db_session):
    """Verify ANALYST role receives HTTP 403 on admin-only endpoints."""
    analyst = User(
        username="analyst_user",
        email="analyst@firm.com",
        full_name="Analyst User",
        password_hash=hash_password("Pass123!"),
        role="ANALYST"
    )
    db_session.add(analyst)
    db_session.commit()

    headers = make_auth_header(analyst)
    assert client.get("/api/v1/users/", headers=headers).status_code == 403
    assert client.get("/api/v1/admin/audit-logs", headers=headers).status_code == 403


def test_admin_can_access_admin_endpoints(client, db_session):
    """Verify ADMIN role successfully accesses admin endpoints."""
    admin = User(
        username="sys_admin",
        email="admin@firm.com",
        full_name="System Admin",
        password_hash=hash_password("Pass123!"),
        role="ADMIN"
    )
    db_session.add(admin)
    db_session.commit()

    headers = make_auth_header(admin)
    res_users = client.get("/api/v1/users/", headers=headers)
    assert res_users.status_code == 200

    res_audit = client.get("/api/v1/admin/audit-logs", headers=headers)
    assert res_audit.status_code == 200


def test_user_can_access_own_document_and_text(client, db_session):
    """Verify user can view metadata and text for a document they own."""
    user = User(
        username="doc_owner",
        email="owner@firm.com",
        full_name="Document Owner",
        password_hash=hash_password("Pass123!"),
        role="USER"
    )
    db_session.add(user)
    db_session.commit()

    doc = Document(
        user_id=user.id,
        owner_id=user.id,
        filename="my_contract.pdf",
        stored_filename="doc_1.pdf",
        file_type="pdf",
        file_size=1000,
        file_hash="hash1",
        extracted_text="Sample contract text under Section 302."
    )
    db_session.add(doc)
    db_session.commit()

    headers = make_auth_header(user)
    res_meta = client.get(f"/api/v1/documents/{doc.id}", headers=headers)
    assert res_meta.status_code == 200
    assert res_meta.json()["filename"] == "my_contract.pdf"

    res_text = client.get(f"/api/v1/documents/{doc.id}/text", headers=headers)
    assert res_text.status_code == 200
    assert "Section 302" in res_text.json()["text"]


def test_user_cannot_access_another_users_document(client, db_session):
    """
    CRITICAL ISOLATION TEST:
    Verify a user receives HTTP 403 when attempting to access another user's document.
    """
    owner = User(username="owner", email="owner@firm.com", full_name="Owner", password_hash="h", role="USER")
    intruder = User(username="intruder", email="intruder@firm.com", full_name="Intruder", password_hash="h", role="USER")
    db_session.add_all([owner, intruder])
    db_session.commit()

    doc = Document(
        user_id=owner.id,
        owner_id=owner.id,
        filename="confidential_settlement.pdf",
        stored_filename="doc_confidential.pdf",
        file_type="pdf",
        file_size=5000,
        file_hash="conf_hash",
        extracted_text="Confidential terms."
    )
    db_session.add(doc)
    db_session.commit()

    intruder_headers = make_auth_header(intruder)

    # Metadata request denied
    res_meta = client.get(f"/api/v1/documents/{doc.id}", headers=intruder_headers)
    assert res_meta.status_code == 403
    assert "permission" in res_meta.json()["detail"].lower()

    # Text extraction request denied
    res_text = client.get(f"/api/v1/documents/{doc.id}/text", headers=intruder_headers)
    assert res_text.status_code == 403


def test_user_cannot_access_another_users_analysis(client, db_session):
    """Verify a user receives HTTP 403 when attempting to access another user's analysis keywords or entities."""
    owner = User(username="owner_a", email="owner_a@firm.com", full_name="Owner A", password_hash="h", role="USER")
    intruder = User(username="intruder_b", email="intruder_b@firm.com", full_name="Intruder B", password_hash="h", role="USER")
    db_session.add_all([owner, intruder])
    db_session.commit()

    doc = Document(
        user_id=owner.id,
        owner_id=owner.id,
        filename="owner_deed.pdf",
        stored_filename="doc_deed.pdf",
        file_type="pdf",
        file_size=2000,
        file_hash="deed_hash",
        extracted_text="Deed text under Section 5."
    )
    db_session.add(doc)
    db_session.commit()

    analysis = AnalysisRun(document_id=doc.id, status="completed", total_keywords=1, total_entities=1)
    db_session.add(analysis)
    db_session.commit()

    kw = ExtractedKeyword(analysis_id=analysis.id, keyword="deed", score=0.88, category="Property", frequency=2, rank=1)
    ent = ExtractedEntity(analysis_id=analysis.id, text="Section 5", entity_type="SECTION", confidence=0.95, source="regex")
    db_session.add_all([kw, ent])
    db_session.commit()

    intruder_headers = make_auth_header(intruder)

    # Keywords access denied
    res_kw = client.get(f"/api/v1/analyses/{analysis.id}/keywords", headers=intruder_headers)
    assert res_kw.status_code == 403

    # Entities access denied
    res_ent = client.get(f"/api/v1/analyses/{analysis.id}/entities", headers=intruder_headers)
    assert res_ent.status_code == 403

    # Summary access denied
    res_sum = client.get(f"/api/v1/analyses/{analysis.id}/entities/summary", headers=intruder_headers)
    assert res_sum.status_code == 403


def test_admin_can_access_any_document_and_analysis(client, db_session):
    """Verify administrator has global access to all documents and analyses across users."""
    owner = User(username="client_user", email="client@firm.com", full_name="Client", password_hash="h", role="USER")
    admin = User(username="admin_global", email="admin_global@firm.com", full_name="Admin Global", password_hash="h", role="ADMIN")
    db_session.add_all([owner, admin])
    db_session.commit()

    doc = Document(
        user_id=owner.id,
        owner_id=owner.id,
        filename="client_contract.pdf",
        stored_filename="doc_client.pdf",
        file_type="pdf",
        file_size=1000,
        file_hash="client_hash",
        extracted_text="Client contract text."
    )
    db_session.add(doc)
    db_session.commit()

    admin_headers = make_auth_header(admin)
    res_doc = client.get(f"/api/v1/documents/{doc.id}", headers=admin_headers)
    assert res_doc.status_code == 200
    assert res_doc.json()["filename"] == "client_contract.pdf"


def test_admin_safeguard_prevents_deactivating_last_admin(client, db_session):
    """Verify admin cannot deactivate the final active administrator account."""
    admin = User(username="solo_admin", email="solo@firm.com", full_name="Solo Admin", password_hash="h", role="ADMIN", is_active=True)
    db_session.add(admin)
    db_session.commit()

    admin_headers = make_auth_header(admin)
    res = client.patch(
        f"/api/v1/users/{admin.id}/status",
        json={"is_active": False},
        headers=admin_headers
    )
    assert res.status_code == 400
    assert "final active administrator" in res.json()["detail"].lower()


def test_admin_safeguard_prevents_demoting_last_admin(client, db_session):
    """Verify admin cannot change role of the final active administrator to USER or ANALYST."""
    admin = User(username="solo_admin2", email="solo2@firm.com", full_name="Solo Admin 2", password_hash="h", role="ADMIN", is_active=True)
    db_session.add(admin)
    db_session.commit()

    admin_headers = make_auth_header(admin)
    res = client.patch(
        f"/api/v1/users/{admin.id}/role",
        json={"role": "USER"},
        headers=admin_headers
    )
    assert res.status_code == 400
    assert "final active administrator" in res.json()["detail"].lower()
