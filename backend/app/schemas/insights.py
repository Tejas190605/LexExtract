from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ClauseItem(BaseModel):
    clause_type: str
    status: str  # "Found" | "Not Found"
    source_section: str = "Not detected"
    source_page: Optional[int] = None
    relevant_text: str = ""
    confidence: float = 0.0
    confidence_label: str = "NOT_FOUND"  # "HIGH", "MEDIUM", "LOW", "NOT_FOUND"
    start_char: Optional[int] = None
    end_char: Optional[int] = None


class ClauseListResponse(BaseModel):
    analysis_id: int
    document_id: int
    total_detected: int
    total_categories: int = 13
    clauses: List[ClauseItem]


class ObligationItem(BaseModel):
    id: int
    responsible_party: str = "Not specified"
    obligation: str
    deadline: str = "Not specified"
    obligation_type: str = "Duty"  # "Duty", "Prohibition", "Payment", "Confidentiality", "Compliance"
    source_section: str = "Not specified"
    source_page: Optional[int] = None
    source_sentence: str


class ObligationListResponse(BaseModel):
    analysis_id: int
    document_id: int
    total: int
    obligations: List[ObligationItem]


class FactItem(BaseModel):
    category: str
    type: str  # "DATE", "MONEY", "DEADLINE"
    value: str
    original_text: str
    source_section: str = "Not specified"
    source_page: Optional[int] = None


class FactsResponse(BaseModel):
    analysis_id: int
    document_id: int
    dates: List[FactItem]
    money: List[FactItem]
    deadlines: List[FactItem]


class DocumentInsightsResponse(BaseModel):
    analysis_id: int
    document_id: int
    document_name: str
    document_type: str
    page_count: int
    section_count: int
    keyword_count: int
    entity_count: int
    parties: List[str]
    important_dates: List[str]
    monetary_amounts: List[str]
    detected_clauses_count: int
    detected_clauses: List[str]
    obligations_count: int
    top_keywords: List[str]
    attention_areas: List[str]


class SearchMatchItem(BaseModel):
    match_id: int
    page_number: int
    section_title: str
    snippet: str
    start_offset: int
    end_offset: int
    score: float


class DocumentSearchResponse(BaseModel):
    document_id: int
    query: str
    total_matches: int
    matches: List[SearchMatchItem]


class DocumentCompareRequest(BaseModel):
    doc_a_id: int
    doc_b_id: int


class DocumentCompareResponse(BaseModel):
    doc_a: Dict[str, Any]
    doc_b: Dict[str, Any]
    similarity_score: float
    similarity_percentage: float
    metadata_comparison: Dict[str, Any]
    keyword_comparison: Dict[str, Any]
    entity_comparison: Dict[str, Any]
    clause_comparison: List[Dict[str, Any]]
    date_comparison: Dict[str, Any]
    money_comparison: Dict[str, Any]
    obligation_comparison: Dict[str, Any]
