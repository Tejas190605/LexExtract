import re
from typing import Dict, Any


def normalize_entity_text(text: str, entity_type: str) -> str:
    """
    Normalizes extracted legal entity strings:
    - Strips surrounding whitespace, quotes, and framing brackets
    - Collapses internal multi-spaces and line breaks
    - Expands statutory abbreviations (e.g. 'Sec. 302' -> 'Section 302', 'Art. 14' -> 'Article 14')
    - Canonicalizes legal roles to lowercase ('PLAINTIFF' -> 'plaintiff')
    - Standardizes currency representations
    - Preserves meaningful capitalization for Persons, Courts, and Organizations
    """
    if not text:
        return ""

    # Strip framing punctuation (quotes, braces, parentheses, commas, colons)
    normalized = text.strip().strip("'\"()[]{}<>;:,")
    # Collapse intra-string whitespace
    normalized = re.sub(r"\s+", " ", normalized).strip()

    if not normalized:
        return ""

    # 1. SECTION Normalization
    if entity_type == "SECTION":
        normalized = re.sub(r"^(?:Sections?|Secs?\.?)\s+", "Section ", normalized, flags=re.IGNORECASE)

    # 2. ARTICLE Normalization
    elif entity_type == "ARTICLE":
        normalized = re.sub(r"^(?:Articles?|Arts?\.?)\s+", "Article ", normalized, flags=re.IGNORECASE)

    # 3. LEGAL_ROLE Normalization (canonical lowercase)
    elif entity_type == "LEGAL_ROLE":
        normalized = normalized.lower()

    # 4. MONEY Normalization (standardize symbol spacing)
    elif entity_type == "MONEY":
        # '₹ 50,000' -> '₹50,000', 'Rs. 50,000' -> 'Rs. 50,000'
        normalized = re.sub(r"^₹\s+", "₹", normalized)
        normalized = re.sub(r"^Rs\.?\s+", "Rs. ", normalized, flags=re.IGNORECASE)

    # 5. CASE_REFERENCE Normalization
    elif entity_type == "CASE_REFERENCE":
        # 'Case  No 123/2026' -> 'Case No. 123/2026'
        normalized = re.sub(r"\bNo\.?\s*", "No. ", normalized, flags=re.IGNORECASE)

    # 6. COURT / ACT / CONTRACT / PERSON / ORGANIZATION Normalization
    elif entity_type in ("COURT", "ACT", "CONTRACT", "PERSON", "ORGANIZATION"):
        # If text is ALL CAPS, convert to Title Case
        if normalized.isupper() and len(normalized) > 4:
            normalized = normalized.title()

    return normalized.strip()


def normalize_entity_record(entity: Dict[str, Any]) -> Dict[str, Any]:
    """
    Applies normalization to an entity record dictionary, setting 'normalized_text'.
    """
    raw_text = entity.get("text", "")
    ent_type = entity.get("entity_type", "OTHER")
    norm_text = normalize_entity_text(raw_text, ent_type)

    record = dict(entity)
    record["normalized_text"] = norm_text or raw_text
    return record
