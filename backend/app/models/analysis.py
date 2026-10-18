from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship, synonym
from app.core.database import Base


class AnalysisRun(Base):
    """
    AnalysisRun entity tracking an execution of the hybrid NLP pipeline.
    A document can have multiple analysis runs with different parameter calibrations.
    """
    __tablename__ = "analysis_runs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), index=True, nullable=False)
    status = Column(String(20), default="pending", nullable=False)  # 'pending', 'running', 'completed', 'failed'
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    processing_time = Column(Float, nullable=True)  # in seconds
    total_keywords = Column(Integer, default=0, nullable=False)
    total_entities = Column(Integer, default=0, nullable=False)

    # Synonym for created_at so .desc(), .asc(), and filters work identically
    created_at = synonym("started_at")

    # Relationships
    document = relationship("Document", back_populates="analysis_runs")
    keywords = relationship("ExtractedKeyword", back_populates="analysis_run", cascade="all, delete-orphan")
    entities = relationship("ExtractedEntity", back_populates="analysis_run", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<AnalysisRun id={self.id} doc_id={self.document_id} status='{self.status}'>"
