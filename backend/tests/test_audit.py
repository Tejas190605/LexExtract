import io
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.core.database import Base, get_db
from app.core.security import hash_password, create_access_token
from app.core.audit_actions import AuditAction
from app.models.user import User
from app.models.document import Document
from app.models.audit import AuditLog
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


def test_audit_login_success(client, db_session):
    """Verify successful login writes LOGIN_SUCCESS audit event."""
    plain_pwd = "AuditPassword2026!"
    user = User(
        username="audit_user",
        email="audit@firm.com",
        full_name="Audit User",
        password_hash=hash_password(plain_pwd),
        role="USER"
    )
    db_session.add(user)
    db_session.commit()

    client.post("/api/v1/auth/login", json={"email_or_username": "audit@firm.com", "password": plain_pwd})

    log = db_session.query(AuditLog).filter(AuditLog.action == AuditAction.LOGIN_SUCCESS).first()
    assert log is not None
    assert log.user_id == user.id
    assert log.status == "SUCCESS"
    assert "authenticated successfully" in log.details


def test_audit_login_failure(client, db_session):
    """Verify failed login writes LOGIN_FAILURE audit event."""
    user = User(
        username="victim_user",
        email="victim@firm.com",
        full_name="Victim",
        password_hash=hash_password("RealPassword!"),
        role="USER"
    )
    db_session.add(user)
    db_session.commit()

    client.post("/api/v1/auth/login", json={"email_or_username": "victim@firm.com", "password": "WrongPassword!"})

    log = db_session.query(AuditLog).filter(AuditLog.action == AuditAction.LOGIN_FAILURE).first()
    assert log is not None
    assert log.user_id == user.id
    assert log.status == "FAILURE"
    assert "RealPassword!" not in log.details
    assert "WrongPassword!" not in log.details


def test_audit_registration_event(client, db_session):
    """Verify user registration writes REGISTER audit event."""
    client.post("/api/v1/auth/register", json={
        "email": "reg_audited@firm.com",
        "username": "reg_audited",
        "full_name": "Reg Audited",
        "password": "RegisterPassword2026!"
    })

    log = db_session.query(AuditLog).filter(AuditLog.action == AuditAction.REGISTER).first()
    assert log is not None
    assert log.status == "SUCCESS"
    assert "reg_audited@firm.com" in log.details
    assert "RegisterPassword2026!" not in log.details


def test_audit_unauthorized_access_attempt(client, db_session):
    """Verify unauthorized document access writes UNAUTHORIZED_ACCESS audit event."""
    owner = User(username="owner_u", email="owner_u@firm.com", full_name="Owner U", password_hash="h", role="USER")
    intruder = User(username="intruder_u", email="intruder_u@firm.com", full_name="Intruder U", password_hash="h", role="USER")
    db_session.add_all([owner, intruder])
    db_session.commit()

    doc = Document(
        user_id=owner.id,
        owner_id=owner.id,
        filename="secret_docket.pdf",
        stored_filename="doc_sec.pdf",
        file_type="pdf",
        file_size=1000,
        file_hash="sec_hash"
    )
    db_session.add(doc)
    db_session.commit()

    intruder_headers = make_auth_header(intruder)
    res = client.get(f"/api/v1/documents/{doc.id}", headers=intruder_headers)
    assert res.status_code == 403

    log = db_session.query(AuditLog).filter(AuditLog.action == AuditAction.UNAUTHORIZED_ACCESS).first()
    assert log is not None
    assert log.user_id == intruder.id
    assert log.status == "FAILURE"
    assert "denied access" in log.details


def test_audit_admin_role_change(client, db_session):
    """Verify admin modifying user role writes USER_ROLE_CHANGED event."""
    admin = User(username="admin_actor", email="admin_actor@firm.com", full_name="Admin Actor", password_hash="h", role="ADMIN")
    target = User(username="target_user", email="target@firm.com", full_name="Target User", password_hash="h", role="USER")
    db_session.add_all([admin, target])
    db_session.commit()

    admin_headers = make_auth_header(admin)
    res = client.patch(
        f"/api/v1/users/{target.id}/role",
        json={"role": "ANALYST"},
        headers=admin_headers
    )
    assert res.status_code == 200

    log = db_session.query(AuditLog).filter(AuditLog.action == AuditAction.USER_ROLE_CHANGED).first()
    assert log is not None
    assert log.user_id == admin.id
    assert "changed role" in log.details
    assert "ANALYST" in log.details


def test_passwords_and_tokens_never_stored_in_audit_records(client, db_session):
    """Verify that credentials, tokens, or hashes are strictly redacted from audit details."""
    admin = User(username="auditor", email="auditor@firm.com", full_name="Auditor", password_hash="h", role="ADMIN")
    db_session.add(admin)
    db_session.commit()

    # Attempt login with credential containing special tokens
    client.post("/api/v1/auth/login", json={
        "email_or_username": "auditor@firm.com",
        "password": "SecretToken12345!"
    })

    all_logs = db_session.query(AuditLog).all()
    for log in all_logs:
        if log.details:
            assert "SecretToken12345!" not in log.details
            assert "bearer" not in log.details.lower()
            assert "password=" not in log.details.lower()


def test_audit_logs_cannot_be_deleted_via_api(client, db_session):
    """Verify there is no DELETE route on /api/v1/admin/audit-logs (append-only governance ledger)."""
    admin = User(username="ledger_admin", email="ledger@firm.com", full_name="Ledger Admin", password_hash="h", role="ADMIN")
    db_session.add(admin)
    db_session.commit()

    admin_headers = make_auth_header(admin)
    # DELETE on audit-logs endpoint must return 405 Method Not Allowed
    res = client.delete("/api/v1/admin/audit-logs", headers=admin_headers)
    assert res.status_code == 405
