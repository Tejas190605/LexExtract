from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, ConfigDict


class KeywordResponse(BaseModel):
    id: int
    analysis_run_id: int
    keyword: str
    category: str
    frequency: int
    rake_score: float
    tfidf_score: float
    lexicon_score: float
    final_score: float

    model_config = ConfigDict(from_attributes=True)


class KeywordItem(BaseModel):
    id: Optional[int] = None
    keyword: str
    category: str
    frequency: int
    tfidf_score: float
    rake_score: float
    lexicon_score: float
    final_score: float
    rank: Optional[int] = 1

    model_config = ConfigDict(from_attributes=True)


class KeywordListResponse(BaseModel):
    analysis_id: int
    total: int
    keywords: List[KeywordItem]


class EntityResponse(BaseModel):
    id: int
    analysis_run_id: int
    entity_text: str
    normalized_text: Optional[str] = None
    entity_type: str
    confidence: float = 1.0
    source: str = "rule"
    frequency: int
    page_number: int
    start_position: int
    end_position: int

    model_config = ConfigDict(from_attributes=True)


class EntityItem(BaseModel):
    id: Optional[int] = None
    text: str
    normalized_text: str
    entity_type: str
    confidence: float
    source: str
    frequency: int = 1
    start_position: Optional[int] = 0
    end_position: Optional[int] = 0
    page_number: Optional[int] = 1

    model_config = ConfigDict(from_attributes=True)


class EntityListResponse(BaseModel):
    analysis_id: int
    total: int
    entities: List[EntityItem]


class EntitySummaryResponse(BaseModel):
    analysis_id: int
    total_entities: int
    type_counts: Dict[str, int]


class AnalysisStartResponse(BaseModel):
    analysis_id: int
    document_id: int
    status: str
    total_keywords: int
    total_entities: int = 0
    processing_time: Optional[float] = None


class AnalysisSummaryResponse(BaseModel):
    analysis_id: int
    document_id: int
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    processing_time: Optional[float] = None
    total_keywords: int
    total_entities: int = 0


class AnalysisRunResponse(BaseModel):
    id: int
    document_id: int
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    processing_time: Optional[float] = None
    total_keywords: int
    total_entities: int
    keywords: List[KeywordResponse] = []
    entities: List[EntityResponse] = []

    model_config = ConfigDict(from_attributes=True)
