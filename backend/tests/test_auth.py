import pytest
from datetime import timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.core.database import Base, get_db
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token
from app.models.user import User
from main import app

# Isolated in-memory SQLite database for security testing
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


def test_password_hashing_and_verification():
    """Verify Argon2id hashes passwords securely and verifies correctly."""
    plain = "SuperSecret2026!"
    hashed = hash_password(plain)

    assert hashed != plain
    assert hashed.startswith("$argon2id$")
    assert verify_password(plain, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False
    assert verify_password("", hashed) is False


def test_jwt_generation_and_decoding():
    """Verify JWT encodes claims and decodes successfully."""
    payload = {"sub": "101", "email": "test@lex.local", "role": "ANALYST"}
    token = create_access_token(payload)

    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "101"
    assert decoded["email"] == "test@lex.local"
    assert decoded["role"] == "ANALYST"
    assert "exp" in decoded
    assert "iat" in decoded


def test_jwt_expired_token_rejected():
    """Verify expired token returns None on decoding."""
    payload = {"sub": "101", "email": "expired@lex.local", "role": "USER"}
    # Create token expired 1 minute ago
    token = create_access_token(payload, expires_delta=timedelta(minutes=-1))

    decoded = decode_access_token(token)
    assert decoded is None


def test_jwt_invalid_token_rejected():
    """Verify malformed or tampered token returns None."""
    assert decode_access_token("not.a.valid.jwt.token") is None
    assert decode_access_token("") is None


def test_user_registration_success(client):
    """Verify POST /api/v1/auth/register creates user and hashes password."""
    payload = {
        "email": "newlawyer@firm.com",
        "username": "newlawyer",
        "full_name": "New Lawyer",
        "password": "SecurePassword2026!"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()

    assert data["email"] == "newlawyer@firm.com"
    assert data["username"] == "newlawyer"
    assert data["full_name"] == "New Lawyer"
    assert data["role"] == "USER"
    assert data["is_active"] is True
    assert "password" not in data
    assert "password_hash" not in data


def test_user_registration_duplicate_email_rejected(client, db_session):
    """Verify duplicate email registration is rejected with HTTP 400."""
    user = User(
        username="lawyer1",
        email="common@firm.com",
        full_name="Lawyer One",
        password_hash=hash_password("Pass123456!"),
        role="USER"
    )
    db_session.add(user)
    db_session.commit()

    payload = {
        "email": "common@firm.com",
        "username": "lawyer2",
        "full_name": "Lawyer Two",
        "password": "AnotherPassword2026!"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400
    assert "email" in response.json()["detail"].lower()


def test_user_registration_duplicate_username_rejected(client, db_session):
    """Verify duplicate username registration is rejected with HTTP 400."""
    user = User(
        username="unique_handle",
        email="first@firm.com",
        full_name="First User",
        password_hash=hash_password("Pass123456!"),
        role="USER"
    )
    db_session.add(user)
    db_session.commit()

    payload = {
        "email": "second@firm.com",
        "username": "unique_handle",
        "full_name": "Second User",
        "password": "AnotherPassword2026!"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400
    assert "username" in response.json()["detail"].lower()


def test_user_registration_password_length_validation(client):
    """Verify short password (< 8 chars) is rejected by validation."""
    payload = {
        "email": "shortpass@firm.com",
        "username": "shortpass",
        "full_name": "Short Password",
        "password": "short"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422  # Pydantic validation error


def test_user_login_success(client, db_session):
    """Verify POST /api/v1/auth/login authenticates and returns Bearer token."""
    plain_pass = "LegalCounsel2026!"
    user = User(
        username="counsel",
        email="counsel@firm.com",
        full_name="Legal Counsel",
        password_hash=hash_password(plain_pass),
        role="ANALYST"
    )
    db_session.add(user)
    db_session.commit()

    # Login with email
    response = client.post("/api/v1/auth/login", json={
        "email_or_username": "counsel@firm.com",
        "password": plain_pass
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "counsel@firm.com"
    assert data["user"]["role"] == "ANALYST"

    # Login with username
    response2 = client.post("/api/v1/auth/login", json={
        "email_or_username": "counsel",
        "password": plain_pass
    })
    assert response2.status_code == 200


def test_user_login_invalid_password_rejected(client, db_session):
    """Verify login with incorrect password returns 401."""
    user = User(
        username="attorney",
        email="attorney@firm.com",
        full_name="Attorney",
        password_hash=hash_password("CorrectPass2026!"),
        role="USER"
    )
    db_session.add(user)
    db_session.commit()

    response = client.post("/api/v1/auth/login", json={
        "email_or_username": "attorney@firm.com",
        "password": "WrongPassword!"
    })
    assert response.status_code == 401


def test_user_login_unknown_user_rejected(client):
    """Verify login for nonexistent user returns generic 401 without user enumeration."""
    response = client.post("/api/v1/auth/login", json={
        "email_or_username": "nonexistent@firm.com",
        "password": "AnyPassword123!"
    })
    assert response.status_code == 401


def test_user_login_inactive_user_rejected(client, db_session):
    """Verify deactivated user cannot log in."""
    user = User(
        username="inactive_lawyer",
        email="inactive@firm.com",
        full_name="Inactive Lawyer",
        password_hash=hash_password("ValidPassword2026!"),
        role="USER",
        is_active=False
    )
    db_session.add(user)
    db_session.commit()

    response = client.post("/api/v1/auth/login", json={
        "email_or_username": "inactive@firm.com",
        "password": "ValidPassword2026!"
    })
    assert response.status_code == 401
    assert "deactivated" in response.json()["detail"].lower()


def test_auth_me_endpoint_with_valid_token(client, db_session):
    """Verify GET /api/v1/auth/me returns current user profile."""
    user = User(
        username="me_user",
        email="me@firm.com",
        full_name="Current User",
        password_hash=hash_password("ValidPass2026!"),
        role="USER"
    )
    db_session.add(user)
    db_session.commit()

    token = create_access_token({"sub": str(user.id), "email": user.email, "role": user.role})
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user.id
    assert data["email"] == "me@firm.com"
    assert data["username"] == "me_user"
    assert data["full_name"] == "Current User"
    assert "password_hash" not in data


def test_auth_me_unauthenticated_returns_401(client):
    """Verify GET /api/v1/auth/me without token returns 401."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
