from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Document(Base):
    """
    Document entity representing uploaded and ingested legal files (.pdf, .docx).
    Stores file metadata, extracted normalized text, page-level segments, and owner reference.
    """
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=True)
    filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False)
    file_type = Column(String(10), nullable=False)  # 'pdf', 'docx'
    file_size = Column(Integer, nullable=False)
    file_hash = Column(String(64), nullable=False)  # SHA-256 digest
    page_count = Column(Integer, nullable=True)     # Int for PDF, None for DOCX
    word_count = Column(Integer, default=0, nullable=False)
    status = Column(String(20), default="uploaded", index=True, nullable=False)  # 'uploaded', 'processing', 'completed', 'failed'
    extracted_text = Column(Text, nullable=True)    # Normalized full document text
    pages_json = Column(Text, nullable=True)        # JSON representation of page-by-page text
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="documents", foreign_keys=[user_id])
    analysis_runs = relationship("AnalysisRun", back_populates="document", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="document", foreign_keys="AuditLog.document_id")

    def __init__(self, **kwargs):
        if "user_id" in kwargs and "owner_id" not in kwargs:
            kwargs["owner_id"] = kwargs["user_id"]
        elif "owner_id" in kwargs and "user_id" not in kwargs:
            kwargs["user_id"] = kwargs["owner_id"]
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return f"<Document id={self.id} filename='{self.filename}' owner_id={self.owner_id or self.user_id}>"
