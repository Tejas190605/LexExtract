from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import require_admin
from app.models.user import User
from app.models.audit import AuditLog
from app.schemas.audit import AuditLogListResponse, AuditLogItem

router = APIRouter()


@router.get("/audit-logs", response_model=AuditLogListResponse, summary="Retrieve governance audit trail (Admin only)")
def get_audit_logs(
    limit: int = Query(50, ge=1, le=100, description="Page limit (1-100)"),
    offset: int = Query(0, ge=0, description="Page offset"),
    action: Optional[str] = Query(None, description="Filter by audit action"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    status: Optional[str] = Query(None, description="Filter by status (SUCCESS, FAILURE)"),
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Returns paginated, immutable audit trail records for compliance inspection.
    Restricted strictly to system administrators.
    """
    query = db.query(AuditLog)

    if action:
        query = query.filter(AuditLog.action == action.upper())
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if status:
        query = query.filter(AuditLog.status == status.upper())

    total = query.count()
    logs = query.order_by(AuditLog.timestamp.desc()).offset(offset).limit(limit).all()

    return AuditLogListResponse(
        total=total,
        limit=limit,
        offset=offset,
        logs=[AuditLogItem.model_validate(log) for log in logs]
    )
