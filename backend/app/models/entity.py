from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship, synonym
from app.core.database import Base


class ExtractedEntity(Base):
    """
    ExtractedEntity entity storing statutory citations, judicial bodies, and named entities.
    Hybrid Legal NER combines spaCy statistical recognition with domain-specific rules.
    """
    __tablename__ = "extracted_entities"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    analysis_run_id = Column(Integer, ForeignKey("analysis_runs.id", ondelete="CASCADE"), index=True, nullable=False)
    entity_text = Column(String(255), nullable=False)
    normalized_text = Column(String(255), nullable=True)
    entity_type = Column(String(50), nullable=False)  # PERSON, ORGANIZATION, LOCATION, DATE, MONEY, LAW, ACT, SECTION, ARTICLE, CASE_REFERENCE, COURT, CONTRACT, LEGAL_ROLE
    confidence = Column(Float, default=1.0, nullable=False)
    source = Column(String(50), default="rule", nullable=False)  # spacy, regex, dictionary, hybrid
    frequency = Column(Integer, default=1, nullable=False)
    page_number = Column(Integer, default=1, nullable=False)
    start_position = Column(Integer, default=0, nullable=False)
    end_position = Column(Integer, default=0, nullable=False)

    # Synonyms for seamless access across query filters and legacy constructors
    analysis_id = synonym("analysis_run_id")
    text = synonym("entity_text")

    # Relationships
    analysis_run = relationship("AnalysisRun", back_populates="entities")

    def __repr__(self) -> str:
        return f"<ExtractedEntity id={self.id} text='{self.entity_text}' type='{self.entity_type}' conf={self.confidence}>"
