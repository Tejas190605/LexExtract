"""
Reusable FastAPI Authentication, Authorization, and RBAC Dependencies for LexExtract.
"""

from typing import List, Optional
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.core.roles import Role
from app.core.audit_actions import AuditAction
from app.core.security import decode_access_token
from app.models.user import User
from app.models.document import Document
from app.services.audit_service import AuditService

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False
)


def get_client_ip(request: Request) -> Optional[str]:
    """Extracts client IP address considering proxy forwarding headers."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return None


def get_current_user(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Decodes and validates Bearer JWT token from Authorization header.
    Returns authenticated active User or raises HTTP 401 Unauthorized.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise credentials_exception

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception

    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    if not user.is_active:
        ip = get_client_ip(request)
        AuditService.record_audit_event(
            db=db,
            action=AuditAction.UNAUTHORIZED_ACCESS,
            user_id=user.id,
            status="FAILURE",
            details=f"Inactive account access attempt by {user.email}",
            ip_address=ip
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user account",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_optional_current_user(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Returns authenticated user if valid token present, otherwise None without raising.
    Useful for endpoints with optional authorization or legacy fallback.
    """
    if not token:
        return None
    try:
        return get_current_user(request, token, db)
    except HTTPException:
        return None


def require_role(allowed_roles: List[str]):
    """
    Dependency factory checking if current user possesses one of the allowed roles.
    Raises 403 Forbidden and logs UNAUTHORIZED_ACCESS on role mismatch.
    """
    def role_checker(
        request: Request,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        user_role = Role.normalize(current_user.role)
        allowed_normalized = [Role.normalize(r) for r in allowed_roles]

        if user_role not in allowed_normalized:
            ip = get_client_ip(request)
            AuditService.record_audit_event(
                db=db,
                action=AuditAction.UNAUTHORIZED_ACCESS,
                user_id=current_user.id,
                status="FAILURE",
                details=f"User {current_user.email} (Role: {user_role}) denied access requiring roles: {allowed_normalized}",
                ip_address=ip
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource."
            )
        return current_user

    return role_checker


# Specialized role dependencies
require_admin = require_role([Role.ADMIN.value])
require_analyst_or_admin = require_role([Role.ANALYST.value, Role.ADMIN.value])


def check_document_access(
    document: Document,
    user: User,
    db: Session,
    ip_address: Optional[str] = None
) -> Document:
    """
    Enforces document isolation and ownership rules:
    - Administrators can inspect all documents.
    - Regular users and analysts can access documents they own.
    - Violations record an audit log and raise HTTP 403 Forbidden.
    """
    user_role = Role.normalize(user.role)
    if user_role == Role.ADMIN.value:
        return document

    is_owner = (document.user_id == user.id) or (document.owner_id is not None and document.owner_id == user.id)
    if is_owner:
        return document

    # Access denied
    AuditService.record_audit_event(
        db=db,
        action=AuditAction.UNAUTHORIZED_ACCESS,
        user_id=user.id,
        resource_type="DOCUMENT",
        resource_id=document.id,
        status="FAILURE",
        details=f"User {user.email} denied access to document {document.id} (Owner: {document.owner_id or document.user_id})",
        ip_address=ip_address
    )
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission to access this legal document."
    )
