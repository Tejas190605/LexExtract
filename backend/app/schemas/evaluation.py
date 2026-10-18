from typing import Dict, Optional
from pydantic import BaseModel


class EvaluationMetrics(BaseModel):
    """Placeholder schema for ASTMA evaluation metrics (Phase 9)."""
    precision: float
    recall: float
    f1_score: float
    total_golden_keywords: int
    total_extracted_keywords: int
    true_positives: int
    false_positives: int
    false_negatives: int
