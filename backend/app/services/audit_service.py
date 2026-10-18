"""
Enterprise Audit Logging Service for LexExtract Governance and Non-Repudiation.
"""

import logging
from typing import Optional
from sqlalchemy.orm import Session
from app.models.audit import AuditLog

logger = logging.getLogger(__name__)

# Sensitive terms that must never appear in audit details
SENSITIVE_SUBSTRINGS = ["password", "secret", "token", "hash", "bearer", "authorization"]


class AuditService:
    @staticmethod
    def sanitize_details(details: Optional[str]) -> Optional[str]:
        """
        Cleans and sanitizes log details to ensure credentials, tokens,
        or excessive text bodies are not recorded in the audit trail.
        """
        if not details:
            return None

        # Truncate to maximum 500 characters
        sanitized = details.strip()
        if len(sanitized) > 490:
            sanitized = sanitized[:490] + "..."

        # Basic check for accidental credential inclusion
        lower_det = sanitized.lower()
        for term in SENSITIVE_SUBSTRINGS:
            if f"{term}=" in lower_det or f"{term}:" in lower_det:
                sanitized = "[REDACTED SENSITIVE DATA]"
                break

        return sanitized

    @classmethod
    def record_audit_event(
        cls,
        db: Session,
        action: str,
        user_id: Optional[int] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        status: str = "SUCCESS",
        details: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> AuditLog:
        """
        Appends an immutable audit record to the governance ledger.
        Catches and logs any DB failure so audit recording never crashes business operations.
        """
        clean_details = cls.sanitize_details(details)
        norm_status = status.upper() if status else "SUCCESS"

        audit_entry = AuditLog(
            user_id=user_id,
            action=action.upper() if action else "UNKNOWN",
            resource_type=resource_type.upper() if resource_type else None,
            resource_id=resource_id,
            status=norm_status,
            ip_address=ip_address,
            details=clean_details,
        )

        try:
            db.add(audit_entry)
            db.commit()
            db.refresh(audit_entry)
            return audit_entry
        except Exception as exc:
            db.rollback()
            logger.error(f"Failed to record audit event '{action}': {exc}", exc_info=True)
            return audit_entry
