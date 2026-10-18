from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.roles import Role
from app.core.audit_actions import AuditAction
from app.core.security import hash_password, verify_password, create_access_token
from app.core.deps import get_current_user, get_client_ip
from app.models.user import User
from app.schemas.user import UserRegister, UserLogin, TokenResponse, UserResponse
from app.services.audit_service import AuditService

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Register new user")
def register(
    request: Request,
    payload: UserRegister,
    db: Session = Depends(get_db)
):
    """
    Registers a new public user.
    - Strictly forces new accounts to role USER (Admin privileges cannot be self-assigned).
    - Hashes password using Argon2id.
    - Records an audit event for accountability.
    """
    ip = get_client_ip(request)

    # Check duplicate email
    if db.query(User).filter(User.email == payload.email).first():
        AuditService.record_audit_event(
            db=db,
            action=AuditAction.REGISTER,
            status="FAILURE",
            details=f"Registration failed: duplicate email {payload.email}",
            ip_address=ip
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists."
        )

    # Check duplicate username
    if db.query(User).filter(User.username == payload.username).first():
        AuditService.record_audit_event(
            db=db,
            action=AuditAction.REGISTER,
            status="FAILURE",
            details=f"Registration failed: duplicate username {payload.username}",
            ip_address=ip
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this username already exists."
        )

    # Create user with securely hashed password
    hashed_pwd = hash_password(payload.password)
    user = User(
        username=payload.username,
        email=payload.email,
        full_name=payload.full_name,
        password_hash=hashed_pwd,
        role=Role.USER.value,  # Enforce role USER
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    AuditService.record_audit_event(
        db=db,
        action=AuditAction.REGISTER,
        user_id=user.id,
        resource_type="USER",
        resource_id=user.id,
        status="SUCCESS",
        details=f"User {user.email} registered successfully with role {user.role}",
        ip_address=ip
    )

    return user


@router.post("/login", response_model=TokenResponse, summary="Authenticate and acquire JWT access token")
async def login(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Authenticates user credentials and issues an RFC 7519 signed JWT token.
    Supports both JSON payloads and standard OAuth2 form encoding.
    """
    ip = get_client_ip(request)

    # Extract credentials from JSON or Form
    identifier = ""
    password = ""

    content_type = request.headers.get("content-type", "").lower()
    if "application/json" in content_type:
        try:
            body = await request.json()
            identifier = (body.get("email_or_username") or body.get("username") or body.get("email") or "").strip()
            password = body.get("password") or ""
        except Exception:
            pass
    elif "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
        try:
            form = await request.form()
            identifier = (form.get("username") or form.get("email") or form.get("email_or_username") or "").strip()
            password = form.get("password") or ""
        except Exception:
            pass
    else:
        # Fallback attempt JSON parse
        try:
            body = await request.json()
            identifier = (body.get("email_or_username") or body.get("username") or body.get("email") or "").strip()
            password = body.get("password") or ""
        except Exception:
            pass

    if not identifier or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Credentials missing. Provide username/email and password."
        )

    # Lookup user by email or username (case-insensitive)
    user = db.query(User).filter(
        (func.lower(User.email) == identifier.lower()) | (func.lower(User.username) == identifier.lower())
    ).first()

    # Generic authentication failure message (OWASP principle: avoid user enumeration)
    generic_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unable to sign in with the provided credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not user:
        AuditService.record_audit_event(
            db=db,
            action=AuditAction.LOGIN_FAILURE,
            status="FAILURE",
            details=f"Login failed: unrecognized identifier '{identifier}'",
            ip_address=ip
        )
        raise generic_error

    if not verify_password(password, user.password_hash):
        AuditService.record_audit_event(
            db=db,
            action=AuditAction.LOGIN_FAILURE,
            user_id=user.id,
            status="FAILURE",
            details=f"Login failed: invalid password for user '{user.email}'",
            ip_address=ip
        )
        raise generic_error

    if not user.is_active:
        AuditService.record_audit_event(
            db=db,
            action=AuditAction.LOGIN_FAILURE,
            user_id=user.id,
            status="FAILURE",
            details=f"Login failed: inactive account for user '{user.email}'",
            ip_address=ip
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your account has been deactivated. Please contact an administrator.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate JWT
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "role": Role.normalize(user.role)
        }
    )

    AuditService.record_audit_event(
        db=db,
        action=AuditAction.LOGIN_SUCCESS,
        user_id=user.id,
        status="SUCCESS",
        details=f"User {user.email} authenticated successfully (Role: {user.role})",
        ip_address=ip
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse, summary="Get profile of currently authenticated user")
def get_me(current_user: User = Depends(get_current_user)):
    """
    Returns profile details of the actor identified by the Bearer JWT token.
    Never exposes passwords or sensitive credentials.
    """
    return current_user


@router.post("/logout", summary="Record user logout event")
def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Records a logout event in the audit trail.
    Client clears local token storage upon calling this endpoint.
    """
    ip = get_client_ip(request)
    AuditService.record_audit_event(
        db=db,
        action=AuditAction.LOGOUT,
        user_id=current_user.id,
        status="SUCCESS",
        details=f"User {current_user.email} signed out",
        ip_address=ip
    )
    return {"message": "Logged out successfully"}
