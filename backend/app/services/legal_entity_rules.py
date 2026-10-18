import re
from typing import List, Dict, Any, Tuple

# ---------------------------------------------------------------------------
# Pre-compiled Regular Expressions for Domain Entities
# ---------------------------------------------------------------------------

# Section references: 'Section 302', 'Section 10(2)', 'Sections 10 and 11', 'Sec. 302', 'Sec 10A'
SECTION_REGEX = re.compile(
    r"\b(?P<prefix>Sections?|Secs?\.?)\s+"
    r"(?P<number>\d+[A-Za-z]?(?:\s*\([0-9a-zA-Z]+\))*(?:\s*(?:and|,)\s*\d+[A-Za-z]?(?:\s*\([0-9a-zA-Z]+\))*)*)",
    flags=re.IGNORECASE
)

# Article references: 'Article 14', 'Article 21', 'Article 19(1)(a)', 'Articles 14 and 21', 'Art. 14'
ARTICLE_REGEX = re.compile(
    r"\b(?P<prefix>Articles?|Arts?\.?)\s+"
    r"(?P<number>\d+[A-Za-z]?(?:\s*\([0-9a-zA-Z]+\))*(?:\s*(?:and|,)\s*\d+[A-Za-z]?(?:\s*\([0-9a-zA-Z]+\))*)*)",
    flags=re.IGNORECASE
)

# Case / Petition references: 'Case No. ABC/123/2026', 'Petition No. 45/2025', 'Appeal No. 12 of 2026'
CASE_REF_REGEX = re.compile(
    r"\b(?:(?:Case|Petition|Appeal|Civil\s+Suit|Criminal\s+Appeal|Writ\s+Petition|Special\s+Leave\s+Petition|SLP)"
    r"(?:\s*\([A-Za-z\s]+\))?\s*No\.?\s*[A-Za-z0-9/\-]+(?:\s+of\s+\d{4})?)\b",
    flags=re.IGNORECASE
)

# Money / Currency mentions: '₹50,000', 'Rs. 50,000', 'INR 10,00,000', '$10,000', 'USD 10,000'
MONEY_REGEX = re.compile(
    r"(?:(?:₹|Rs\.|Rs|INR|\$|USD)\s*[\d,]+(?:\.\d+)?(?:\s*(?:crore|lakh|million|billion))?)\b",
    flags=re.IGNORECASE
)

# Date mentions: '15 January 2026', '15th January 2026', '01/01/2026', '15-01-2026', 'January 1, 2026'
DATE_REGEX = re.compile(
    r"\b(?:\d{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December),?\s+\d{4}"
    r"|(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}"
    r"|\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b",
    flags=re.IGNORECASE
)

# ---------------------------------------------------------------------------
# Gazetteers & Taxonomic Dictionaries
# ---------------------------------------------------------------------------

KNOWN_ACTS = [
    "Indian Contract Act",
    "Indian Penal Code",
    "Code of Civil Procedure",
    "Code of Criminal Procedure",
    "Companies Act",
    "Companies Act, 2013",
    "Arbitration and Conciliation Act",
    "Information Technology Act",
    "Consumer Protection Act",
    "Transfer of Property Act",
    "Specific Relief Act",
    "Negotiable Instruments Act",
    "Copyright Act",
    "Patents Act",
    "Trade Marks Act",
    "Constitution of India",
    "Evidence Act",
    "Insolvency and Bankruptcy Code",
    "Limitation Act"
]

KNOWN_COURTS = [
    "Supreme Court of India",
    "Supreme Court",
    "High Court of Delhi",
    "Delhi High Court",
    "Bombay High Court",
    "High Court",
    "District Court",
    "Sessions Court",
    "Civil Court",
    "Family Court",
    "Commercial Court",
    "National Company Law Tribunal",
    "NCLT",
    "National Company Law Appellate Tribunal",
    "NCLAT",
    "Debt Recovery Tribunal",
    "DRT",
    "Consumer Disputes Redressal Forum",
    "Consumer Court",
    "Arbitral Tribunal"
]

KNOWN_CONTRACTS = [
    "Commercial Lease Agreement",
    "Employment Agreement",
    "Service Agreement",
    "Lease Agreement",
    "Deed of Lease",
    "Non-Disclosure Agreement",
    "Confidentiality Agreement",
    "Sale Agreement",
    "Purchase Agreement",
    "Loan Agreement",
    "Partnership Agreement",
    "Licensing Agreement",
    "Share Purchase Agreement",
    "Commercial Supply Agreement",
    "Settlement Agreement"
]

LEGAL_ROLES = [
    "plaintiff",
    "defendant",
    "petitioner",
    "respondent",
    "appellant",
    "accused",
    "complainant",
    "claimant",
    "applicant",
    "responding party",
    "opposite party"
]


def extract_regex_and_gazetteer_entities(text: str) -> List[Dict[str, Any]]:
    """
    Executes compiled regex and gazetteer searches across document text.
    Returns list of candidate entity records:
    [
      {
        "text": raw_match,
        "entity_type": TYPE,
        "confidence": float,
        "source": "regex" | "dictionary",
        "start_position": int,
        "end_position": int
      }
    ]
    """
    if not text:
        return []

    entities: List[Dict[str, Any]] = []

    # 1. SECTION Extraction
    for m in SECTION_REGEX.finditer(text):
        entities.append({
            "text": m.group(0),
            "entity_type": "SECTION",
            "confidence": 0.95,
            "source": "regex",
            "start_position": m.start(),
            "end_position": m.end()
        })

    # 2. ARTICLE Extraction
    for m in ARTICLE_REGEX.finditer(text):
        entities.append({
            "text": m.group(0),
            "entity_type": "ARTICLE",
            "confidence": 0.95,
            "source": "regex",
            "start_position": m.start(),
            "end_position": m.end()
        })

    # 3. CASE_REFERENCE Extraction
    for m in CASE_REF_REGEX.finditer(text):
        entities.append({
            "text": m.group(0),
            "entity_type": "CASE_REFERENCE",
            "confidence": 0.95,
            "source": "regex",
            "start_position": m.start(),
            "end_position": m.end()
        })

    # 4. MONEY Extraction
    for m in MONEY_REGEX.finditer(text):
        entities.append({
            "text": m.group(0),
            "entity_type": "MONEY",
            "confidence": 0.90,
            "source": "regex",
            "start_position": m.start(),
            "end_position": m.end()
        })

    # 5. DATE Extraction
    for m in DATE_REGEX.finditer(text):
        entities.append({
            "text": m.group(0),
            "entity_type": "DATE",
            "confidence": 0.90,
            "source": "regex",
            "start_position": m.start(),
            "end_position": m.end()
        })

    # 6. ACT / LAW Gazetteer Matching
    for act in KNOWN_ACTS:
        pattern = rf"\b{re.escape(act)}\b"
        entity_type = "LAW" if "Code" in act or "Constitution" in act else "ACT"
        for m in re.finditer(pattern, text, flags=re.IGNORECASE):
            entities.append({
                "text": m.group(0),
                "entity_type": entity_type,
                "confidence": 0.95,
                "source": "dictionary",
                "start_position": m.start(),
                "end_position": m.end()
            })

    # 7. COURT Gazetteer Matching
    for court in KNOWN_COURTS:
        pattern = rf"\b{re.escape(court)}\b"
        for m in re.finditer(pattern, text, flags=re.IGNORECASE):
            entities.append({
                "text": m.group(0),
                "entity_type": "COURT",
                "confidence": 0.95,
                "source": "dictionary",
                "start_position": m.start(),
                "end_position": m.end()
            })

    # 8. CONTRACT Gazetteer Matching
    for contract in KNOWN_CONTRACTS:
        pattern = rf"\b{re.escape(contract)}\b"
        for m in re.finditer(pattern, text, flags=re.IGNORECASE):
            entities.append({
                "text": m.group(0),
                "entity_type": "CONTRACT",
                "confidence": 0.90,
                "source": "dictionary",
                "start_position": m.start(),
                "end_position": m.end()
            })

    # 9. LEGAL_ROLE Matching
    for role in LEGAL_ROLES:
        pattern = rf"\b{re.escape(role)}\b"
        for m in re.finditer(pattern, text, flags=re.IGNORECASE):
            entities.append({
                "text": m.group(0),
                "entity_type": "LEGAL_ROLE",
                "confidence": 0.90,
                "source": "dictionary",
                "start_position": m.start(),
                "end_position": m.end()
            })

    return entities
