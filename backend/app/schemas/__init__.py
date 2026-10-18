"""
Pydantic Data Contracts & Schemas for LexExtract.
"""

from app.schemas.user import UserBase, UserCreate, UserResponse
from app.schemas.document import (
    DocumentBase,
    DocumentCreate,
    DocumentResponse,
    DocumentUploadResponse,
    DocumentTextResponse,
    PageContent,
)
from app.schemas.analysis import AnalysisRunResponse, KeywordResponse, EntityResponse
from app.schemas.evaluation import EvaluationMetrics

__all__ = [
    "UserBase",
    "UserCreate",
    "UserResponse",
    "DocumentBase",
    "DocumentCreate",
    "DocumentResponse",
    "DocumentUploadResponse",
    "DocumentTextResponse",
    "PageContent",
    "AnalysisRunResponse",
    "KeywordResponse",
    "EntityResponse",
    "EvaluationMetrics",
]
