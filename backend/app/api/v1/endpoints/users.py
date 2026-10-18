from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.roles import Role
from app.core.audit_actions import AuditAction
from app.core.deps import require_admin, get_client_ip
from app.models.user import User
from app.schemas.user import UserResponse, UserStatusUpdate, UserRoleUpdate
from app.services.audit_service import AuditService

router = APIRouter()


@router.get("/", response_model=List[UserResponse], summary="List system users (Admin only)")
def list_users(
    skip: int = 0,
    limit: int = 100,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Returns list of system users.
    Restricted strictly to administrators.
    Password hash is never included in the response schema.
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserResponse, summary="Get user by ID (Admin only)")
def get_user(
    user_id: int,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Retrieves user profile by ID.
    Restricted strictly to administrators.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.patch("/{user_id}/status", response_model=UserResponse, summary="Activate or deactivate user (Admin only)")
def update_user_status(
    user_id: int,
    payload: UserStatusUpdate,
    request: Request,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Updates user active/inactive status.
    Critical Safeguard: Prevents deactivating the final active administrator.
    """
    ip = get_client_ip(request)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Safeguard: prevent deactivating the last active administrator
    if not payload.is_active and Role.normalize(user.role) == Role.ADMIN.value:
        active_admins_count = db.query(User).filter(
            User.role.in_(["ADMIN", "admin"]),
            User.is_active == True  # noqa: E712
        ).count()
        if active_admins_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Operation prohibited: Cannot deactivate the final active administrator."
            )

    user.is_active = payload.is_active
    db.commit()
    db.refresh(user)

    action = AuditAction.USER_ACTIVATED if user.is_active else AuditAction.USER_DEACTIVATED
    AuditService.record_audit_event(
        db=db,
        action=action,
        user_id=current_admin.id,
        resource_type="USER",
        resource_id=user.id,
        status="SUCCESS",
        details=f"Admin {current_admin.email} set active={user.is_active} for user {user.email}",
        ip_address=ip
    )

    return user


@router.patch("/{user_id}/role", response_model=UserResponse, summary="Modify user role (Admin only)")
def update_user_role(
    user_id: int,
    payload: UserRoleUpdate,
    request: Request,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Modifies user role (USER, ANALYST, ADMIN).
    Critical Safeguard: Prevents demoting the final active administrator.
    """
    ip = get_client_ip(request)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    target_role = Role.normalize(payload.role)
    current_role = Role.normalize(user.role)

    # Safeguard: prevent demoting the last active administrator
    if current_role == Role.ADMIN.value and target_role != Role.ADMIN.value:
        active_admins_count = db.query(User).filter(
            User.role.in_(["ADMIN", "admin"]),
            User.is_active == True  # noqa: E712
        ).count()
        if active_admins_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Operation prohibited: Cannot change role of the final active administrator."
            )

    user.role = target_role
    db.commit()
    db.refresh(user)

    AuditService.record_audit_event(
        db=db,
        action=AuditAction.USER_ROLE_CHANGED,
        user_id=current_admin.id,
        resource_type="USER",
        resource_id=user.id,
        status="SUCCESS",
        details=f"Admin {current_admin.email} changed role of user {user.email} from {current_role} to {target_role}",
        ip_address=ip
    )

    return user
