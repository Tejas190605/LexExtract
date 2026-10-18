from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class AuditLog(Base):
    """
    AuditLog entity representing immutable governance records of user, document, and security actions.
    Append-only non-repudiation audit ledger.
    """
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True)
    action = Column(String(50), nullable=False)
    resource_type = Column(String(50), nullable=True)
    resource_id = Column(Integer, nullable=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="SET NULL"), index=True, nullable=True)
    status = Column(String(20), default="SUCCESS", nullable=False)  # 'SUCCESS', 'FAILURE'
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    ip_address = Column(String(45), nullable=True)
    details = Column(String(500), nullable=True)

    # Relationships
    user = relationship("User", back_populates="audit_logs", foreign_keys=[user_id])
    document = relationship("Document", back_populates="audit_logs", foreign_keys=[document_id])

    def __init__(self, **kwargs):
        # Sync document_id and resource_id if resource_type is DOCUMENT
        if kwargs.get("resource_type") == "DOCUMENT" and "resource_id" in kwargs and "document_id" not in kwargs:
            kwargs["document_id"] = kwargs["resource_id"]
        elif "document_id" in kwargs and kwargs.get("document_id") and "resource_id" not in kwargs:
            kwargs["resource_id"] = kwargs["document_id"]
            if "resource_type" not in kwargs:
                kwargs["resource_type"] = "DOCUMENT"
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return f"<AuditLog id={self.id} action='{self.action}' user_id={self.user_id} status='{self.status}'>"
