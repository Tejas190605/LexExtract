import logging
from typing import List, Dict, Any
from app.services.spacy_service import extract_spacy_entities
from app.services.legal_entity_rules import extract_regex_and_gazetteer_entities
from app.services.entity_normalizer import normalize_entity_record
from app.services.entity_deduplicator import deduplicate_and_merge_entities

logger = logging.getLogger(__name__)


def extract_legal_entities(document_text: str) -> List[Dict[str, Any]]:
    """
    Main Orchestration Service for Hybrid Legal Entity Extraction:
    1. Statistical NER: Extracts PERSON, ORGANIZATION, LOCATION, DATE, MONEY using spaCy.
    2. Rule & Gazetteer Engine: Extracts SECTION, ARTICLE, ACT, LAW, CASE_REFERENCE, COURT, CONTRACT, LEGAL_ROLE.
    3. Normalization: Expands abbreviations, canonicalizes casing, and standardizes numbers.
    4. Deduplication & Conflict Resolution: Resolves span overlaps, awards domain precedence to legal rules,
       and boosts hybrid agreement confidence.
    5. Returns ranked list of deduplicated entity records.
    """
    if not document_text or not document_text.strip():
        return []

    # 1. Statistical Extraction (spaCy)
    spacy_candidates: List[Dict[str, Any]] = []
    try:
        spacy_candidates = extract_spacy_entities(document_text)
    except Exception as exc:
        logger.warning(f"spaCy extraction encountered an issue: {exc}. Falling back to rule engine.")

    # 2. Domain Rule & Gazetteer Extraction (Regex + Dictionaries)
    rule_candidates = extract_regex_and_gazetteer_entities(document_text)

    # 3. Combine Candidates
    all_candidates = spacy_candidates + rule_candidates
    if not all_candidates:
        return []

    # 4. Normalize Candidates
    normalized_candidates = [normalize_entity_record(cand) for cand in all_candidates]

    # 5. Deduplicate, Resolve Overlaps, and Calibrate Confidence
    final_entities = deduplicate_and_merge_entities(normalized_candidates)

    logger.info(
        f"Extracted {len(all_candidates)} raw entity mentions, deduplicated to {len(final_entities)} distinct entities."
    )
    return final_entities
