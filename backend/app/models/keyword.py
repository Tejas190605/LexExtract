from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship, synonym
from app.core.database import Base


class ExtractedKeyword(Base):
    """
    ExtractedKeyword entity storing candidate keyphrases and composite ranking scores.
    """
    __tablename__ = "extracted_keywords"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    analysis_run_id = Column(Integer, ForeignKey("analysis_runs.id", ondelete="CASCADE"), index=True, nullable=False)
    keyword = Column(String(255), nullable=False)
    category = Column(String(50), default="General", nullable=False)
    frequency = Column(Integer, default=1, nullable=False)
    rake_score = Column(Float, default=0.0, nullable=False)
    tfidf_score = Column(Float, default=0.0, nullable=False)
    lexicon_score = Column(Float, default=0.0, nullable=False)
    final_score = Column(Float, default=0.0, nullable=False)
    rank = Column(Integer, default=1, nullable=True)

    # Synonyms for seamless access across query filters and legacy constructors
    analysis_id = synonym("analysis_run_id")
    score = synonym("final_score")

    # Relationships
    analysis_run = relationship("AnalysisRun", back_populates="keywords")

    def __repr__(self) -> str:
        return f"<ExtractedKeyword id={self.id} keyword='{self.keyword}' score={self.final_score}>"
