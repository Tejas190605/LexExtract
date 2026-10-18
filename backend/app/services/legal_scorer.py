import json
import os
import re
from typing import Dict, Tuple, List, Optional
from app.services.candidate_filter import is_statutory_citation

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
LEGAL_TERMS_PATH = os.path.join(DATA_DIR, "legal_terms.json")

_LEGAL_TERMS_CACHE: Optional[Dict[str, List[str]]] = None


def load_legal_terms() -> Dict[str, List[str]]:
    """
    Loads and caches the categorized legal dictionary from JSON.
    """
    global _LEGAL_TERMS_CACHE
    if _LEGAL_TERMS_CACHE is not None:
        return _LEGAL_TERMS_CACHE

    if not os.path.exists(LEGAL_TERMS_PATH):
        _LEGAL_TERMS_CACHE = {}
        return _LEGAL_TERMS_CACHE

    try:
        with open(LEGAL_TERMS_PATH, "r", encoding="utf-8") as f:
            _LEGAL_TERMS_CACHE = json.load(f)
    except Exception:
        _LEGAL_TERMS_CACHE = {}

    return _LEGAL_TERMS_CACHE


def get_legal_score_and_category(candidate: str) -> Tuple[float, str]:
    """
    Computes a rule-based domain relevance score [0.0 - 1.0] and assigns
    the most specific legal category.

    Scoring Tiers:
    - Exact multi-word legal phrase match: 1.00
    - Exact single-word legal term match: 0.85
    - Statutory citation match (e.g., 'Section 302'): 0.90
    - Subphrase / head noun match in multi-word candidate: 0.60
    - Non-dictionary candidate: 0.00 (category: 'other')
    """
    if not candidate:
        return 0.0, "other"

    taxonomy = load_legal_terms()
    cand_lower = candidate.strip().lower()

    # Check for statutory citation first
    if is_statutory_citation(candidate):
        return 0.90, "procedure"

    # Tier 1 & 2: Exact matches in taxonomy
    for category, terms in taxonomy.items():
        for term in terms:
            term_lower = term.lower()
            if cand_lower == term_lower:
                # Multi-word exact match gets full 1.0, unigram exact gets 0.85
                score = 1.0 if len(term_lower.split()) > 1 else 0.85
                return score, category

    # Tier 3: Subphrase match within multi-word candidates
    cand_tokens = cand_lower.split()
    if len(cand_tokens) > 1:
        for category, terms in taxonomy.items():
            for term in terms:
                term_lower = term.lower()
                # Check word-boundary match
                pattern = r"\b" + re.escape(term_lower) + r"\b"
                if re.search(pattern, cand_lower):
                    return 0.60, category

    return 0.0, "other"


def score_candidates_with_lexicon(candidates: List[str]) -> Dict[str, Tuple[float, str]]:
    """
    Batch scores a list of candidates against the legal taxonomy.
    Returns: { candidate: (legal_score, category) }
    """
    scores: Dict[str, Tuple[float, str]] = {}
    for cand in candidates:
        scores[cand] = get_legal_score_and_category(cand)
    return scores
