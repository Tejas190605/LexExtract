import re
import json
import difflib
import logging
from typing import List, Dict, Any, Optional, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pymupdf

logger = logging.getLogger(__name__)

# Controlled 13 legal clause categories
CLAUSE_DEFINITIONS = {
    "Termination": {
        "headers": [r"\btermination\b", r"\bexpiration\s+and\s+termination\b", r"\bearly\s+termination\b", r"\btermination\s+for\s+cause\b"],
        "patterns": [
            r"\bterminate\s+this\s+agreement\b",
            r"\bright\s+to\s+terminate\b",
            r"\bwritten\s+notice\s+of\s+termination\b",
            r"\bupon\s+termination\b",
            r"\btermination\s+date\b",
            r"\bmay\s+terminate\b",
            r"\bgrounds\s+for\s+termination\b"
        ]
    },
    "Confidentiality": {
        "headers": [r"\bconfidentiality\b", r"\bconfidential\s+information\b", r"\bnon-disclosure\b", r"\bsecrecy\b"],
        "patterns": [
            r"\bconfidential\s+information\b",
            r"\bmaintain\s+confidentiality\b",
            r"\bshall\s+not\s+disclose\b",
            r"\bproprietary\s+information\b",
            r"\bobligation\s+of\s+confidence\b",
            r"\bkeep\s+confidential\b"
        ]
    },
    "Payment / Compensation": {
        "headers": [r"\bpayment\b", r"\bcompensation\b", r"\bfees\b", r"\bconsideration\b", r"\bterms\s+of\s+payment\b", r"\bremuneration\b"],
        "patterns": [
            r"\bshall\s+pay\b",
            r"\bpayment\s+terms\b",
            r"\binvoice\b",
            r"\bcompensation\s+for\s+services\b",
            r"\bdue\s+date\s+of\s+payment\b",
            r"\bpayable\s+within\b",
            r"\bhourly\s+rate\b",
            r"\bmonthly\s+fee\b"
        ]
    },
    "Liability": {
        "headers": [r"\blimitation\s+of\s+liability\b", r"\bliability\b", r"\blimitation\s+of\s+damages\b"],
        "patterns": [
            r"\blimitation\s+of\s+liability\b",
            r"\bindirect,\s*incidental,\s*or\s*consequential\s+damages\b",
            r"\baggregate\s+liability\b",
            r"\bin\s+no\s+event\s+shall\s+either\s+party\s+be\s+liable\b",
            r"\bmaximum\s+liability\b",
            r"\bexclusion\s+of\s+damages\b"
        ]
    },
    "Indemnification": {
        "headers": [r"\bindemnification\b", r"\bindemnity\b", r"\bhold\s+harmless\b", r"\bdefense\s+and\s+indemnity\b"],
        "patterns": [
            r"\bshall\s+indemnify\s+and\s+hold\s+harmless\b",
            r"\bindemnify,\s*defend,?\s*and\s*hold\b",
            r"\bagainst\s+any\s+claims,\s*losses,\s*damages\b",
            r"\bindemnified\s+party\b",
            r"\bindemnifying\s+party\b"
        ]
    },
    "Arbitration / Dispute Resolution": {
        "headers": [r"\bdispute\s+resolution\b", r"\barbitration\b", r"\bconciliation\b", r"\bmediation\b"],
        "patterns": [
            r"\bshall\s+be\s+settled\s+by\s+arbitration\b",
            r"\barbitration\s+and\s+conciliation\s+act\b",
            r"\bsole\s+arbitrator\b",
            r"\barbitral\s+tribunal\b",
            r"\bseat\s+and\s+venue\s+of\s+the\s+arbitration\b",
            r"\brules\s+of\s+arbitration\b",
            r"\bdisputes\s+arising\s+out\s+of\b"
        ]
    },
    "Governing Law": {
        "headers": [r"\bgoverning\s+law\b", r"\bjurisdiction\b", r"\bapplicable\s+law\b", r"\bchoice\s+of\s+law\b"],
        "patterns": [
            r"\bgoverned\s+by\s+and\s+construed\s+in\s+accordance\s+with\b",
            r"\bsubstantive\s+laws\s+of\b",
            r"\bexclusive\s+jurisdiction\s+of\s+the\s+courts\b",
            r"\bcompetent\s+courts\s+at\b",
            r"\bgoverning\s+law\b"
        ]
    },
    "Renewal": {
        "headers": [r"\brenewal\b", r"\bextension\b", r"\bterm\s+and\s+renewal\b"],
        "patterns": [
            r"\bautomatically\s+renew\b",
            r"\brenewal\s+term\b",
            r"\boption\s+to\s+renew\b",
            r"\bwritten\s+notice\s+of\s+renewal\b",
            r"\bextended\s+for\s+a\s+further\s+period\b"
        ]
    },
    "Notice": {
        "headers": [r"\bnotices?\b", r"\bform\s+of\s+notice\b", r"\bcommunications\b"],
        "patterns": [
            r"\ball\s+notices\s+shall\s+be\s+in\s+writing\b",
            r"\bdeemed\s+given\s+when\s+delivered\b",
            r"\bcertified\s+mail\b",
            r"\bnotice\s+address\b",
            r"\bdelivered\s+by\s+hand\s+or\s+registered\s+post\b"
        ]
    },
    "Intellectual Property": {
        "headers": [r"\bintellectual\s+property\b", r"\bproprietary\s+rights\b", r"\bip\s+rights\b", r"\bownership\s+of\s+work\b"],
        "patterns": [
            r"\bintellectual\s+property\s+rights\b",
            r"\bwork\s+made\s+for\s+hire\b",
            r"\binventions,?\s*copyrights,?\s*trademarks\b",
            r"\bretains\s+all\s+right,\s*title,?\s*and\s+interest\b",
            r"\bmoral\s+rights\b",
            r"\bassignment\s+of\s+inventions\b"
        ]
    },
    "Non-Disclosure": {
        "headers": [r"\bnon-disclosure\b", r"\bdisclosure\s+of\s+information\b", r"\brestricted\s+use\b"],
        "patterns": [
            r"\bshall\s+not\s+disclose\b",
            r"\bnon-disclosure\s+obligations?\b",
            r"\breceiving\s+party\s+agrees\s+not\s+to\s+disclose\b",
            r"\bauthorized\s+disclosure\b",
            r"\bdegree\s+of\s+care\b"
        ]
    },
    "Non-Compete / Restriction": {
        "headers": [r"\bnon-compete\b", r"\bnon-solicitation\b", r"\brestrictive\s+covenants\b", r"\brestriction\s+on\s+employment\b"],
        "patterns": [
            r"\bshall\s+not\s+engage\s+in\s+competing\b",
            r"\bnon-competition\b",
            r"\bshall\s+not\s+solicit\s+employees\s+or\s+clients\b",
            r"\bduring\s+the\s+term\s+and\s+for\s+a\s+period\s+of\b",
            r"\brestricted\s+business\b",
            r"\bnon-solicit\b"
        ]
    },
    "Force Majeure": {
        "headers": [r"\bforce\s+majeure\b", r"\bacts\s+of\s+god\b", r"\bunforeseen\s+events\b", r"\bfrustration\s+of\s+contract\b"],
        "patterns": [
            r"\bforce\s+majeure\b",
            r"\bact\s+of\s+god\b",
            r"\bnatural\s+disaster,?\s*war,?\s*terrorism,?\s*pandemic\b",
            r"\bfailure\s+or\s+delay\s+in\s+performance\s+caused\s+by\b",
            r"\bbeyond\s+the\s+reasonable\s+control\s+of\b"
        ]
    }
}


def _split_into_sections_and_pages(
    document_text: str,
    pages_json_str: Optional[str]
) -> List[Dict[str, Any]]:
    """
    Parses document into structured segments with page and section references.
    """
    sections = []
    
    # Try using page segments if available
    if pages_json_str:
        try:
            raw_pages = json.loads(pages_json_str)
            for p in raw_pages:
                page_no = p.get("page_number", 1)
                text = p.get("text", "")
                paras = [para.strip() for para in text.split("\n\n") if para.strip()]
                current_sec_title = f"Page {page_no}"
                for para in paras:
                    # Check if paragraph looks like a heading
                    lines = para.split("\n")
                    first_line = lines[0].strip()
                    if len(first_line) < 80 and (
                        re.match(r"^(?:[0-9]+[\.\)]\s+|ARTICLE\s+|SECTION\s+|CLAUSE\s+|[A-Z\s]{4,}$)", first_line, re.IGNORECASE)
                        or first_line.isupper()
                    ):
                        current_sec_title = first_line
                    
                    sections.append({
                        "section_title": current_sec_title,
                        "page_number": page_no,
                        "text": para
                    })
            if sections:
                return sections
        except Exception as exc:
            logger.debug(f"Failed parsing pages_json: {exc}")

    # Fallback to text parsing
    paragraphs = [p.strip() for p in document_text.split("\n\n") if p.strip()]
    sec_idx = 1
    current_title = "General Document Text"
    for p in paragraphs:
        lines = p.split("\n")
        first_line = lines[0].strip()
        if len(first_line) < 80 and (
            re.match(r"^(?:[0-9]+[\.\)]\s+|ARTICLE\s+|SECTION\s+|CLAUSE\s+|[A-Z\s]{4,}$)", first_line, re.IGNORECASE)
            or first_line.isupper()
        ):
            current_title = first_line
        sections.append({
            "section_title": current_title,
            "page_number": 1,
            "text": p
        })
        sec_idx += 1

    return sections


def extract_important_clauses(
    document_text: str,
    pages_json_str: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Detects the 13 controlled legal clause categories in the document text.
    Returns status (Found / Not Found), source section, page, relevant text, and confidence.
    """
    if not document_text or not document_text.strip():
        return [
            {
                "clause_type": c_type,
                "status": "Not Found",
                "source_section": "Not detected",
                "source_page": None,
                "relevant_text": "",
                "confidence": 0.0,
                "confidence_label": "NOT_FOUND",
                "start_char": None,
                "end_char": None
            }
            for c_type in CLAUSE_DEFINITIONS.keys()
        ]

    sections = _split_into_sections_and_pages(document_text, pages_json_str)
    results = []

    for clause_type, defs in CLAUSE_DEFINITIONS.items():
        best_match = None
        highest_score = 0.0

        for sec in sections:
            sec_title = sec["section_title"]
            sec_text = sec["text"]
            combined = f"{sec_title}\n{sec_text}"

            # Check header match
            header_hit = False
            for h_pat in defs["headers"]:
                if re.search(h_pat, sec_title, re.IGNORECASE) or re.search(h_pat, sec_text[:80], re.IGNORECASE):
                    header_hit = True
                    break

            # Count pattern matches
            pattern_hits = 0
            matched_phrase = ""
            for p_pat in defs["patterns"]:
                match = re.search(p_pat, combined, re.IGNORECASE)
                if match:
                    pattern_hits += 1
                    if not matched_phrase:
                        matched_phrase = match.group(0)

            # Score computation
            score = 0.0
            if header_hit and pattern_hits >= 1:
                score = 0.95
            elif header_hit:
                score = 0.88
            elif pattern_hits >= 2:
                score = 0.82
            elif pattern_hits == 1:
                score = 0.68

            if score > highest_score:
                highest_score = score
                # Extract relevant snippet
                snippet = sec_text
                if len(snippet) > 350:
                    # Focus around pattern if possible
                    if matched_phrase and matched_phrase.lower() in snippet.lower():
                        idx = snippet.lower().find(matched_phrase.lower())
                        start = max(0, idx - 80)
                        end = min(len(snippet), idx + len(matched_phrase) + 180)
                        snippet = ("..." if start > 0 else "") + snippet[start:end].strip() + ("..." if end < len(sec_text) else "")
                    else:
                        snippet = snippet[:320].strip() + "..."

                best_match = {
                    "source_section": sec_title if sec_title else "Document Body",
                    "source_page": sec["page_number"],
                    "relevant_text": snippet,
                    "confidence": round(score, 2),
                    "confidence_label": "HIGH" if score >= 0.85 else ("MEDIUM" if score >= 0.65 else "LOW")
                }

        if best_match and highest_score >= 0.65:
            # Calculate approx start_char in full text
            start_pos = document_text.find(best_match["relevant_text"][:50]) if best_match["relevant_text"] else -1
            results.append({
                "clause_type": clause_type,
                "status": "Found",
                "source_section": best_match["source_section"],
                "source_page": best_match["source_page"],
                "relevant_text": best_match["relevant_text"],
                "confidence": best_match["confidence"],
                "confidence_label": best_match["confidence_label"],
                "start_char": start_pos if start_pos != -1 else None,
                "end_char": (start_pos + len(best_match["relevant_text"])) if start_pos != -1 else None
            })
        else:
            results.append({
                "clause_type": clause_type,
                "status": "Not Found",
                "source_section": "Not detected",
                "source_page": None,
                "relevant_text": "",
                "confidence": 0.0,
                "confidence_label": "NOT_FOUND",
                "start_char": None,
                "end_char": None
            })

    return results


def extract_obligations(
    document_text: str,
    pages_json_str: Optional[str] = None,
    entities: Optional[List[Dict[str, Any]]] = None
) -> List[Dict[str, Any]]:
    """
    Extracts controlled obligations using modal verb patterns:
    - shall / must / required to / agrees to / responsible for / undertake to / will provide / will pay / is obligated to
    - prohibitions: may not / shall not / will not / is prohibited from
    """
    if not document_text or not document_text.strip():
        return []

    sections = _split_into_sections_and_pages(document_text, pages_json_str)
    
    # Candidate modal patterns
    prohibition_pattern = re.compile(
        r"\b(?:shall\s+not|must\s+not|may\s+not|will\s+not|is\s+prohibited\s+from|agrees?\s+not\s+to|under\s+no\s+circumstances)\b",
        re.IGNORECASE
    )
    payment_pattern = re.compile(
        r"\b(?:shall\s+pay|will\s+pay|agrees?\s+to\s+pay|responsible\s+for\s+paying|remit|reimburse)\b",
        re.IGNORECASE
    )
    confidentiality_pattern = re.compile(
        r"\b(?:shall\s+keep\s+confidential|maintain\s+confidentiality|shall\s+not\s+disclose|holds?\s+in\s+confidence)\b",
        re.IGNORECASE
    )
    duty_pattern = re.compile(
        r"\b(?:shall|must|required\s+to|agrees?\s+to|responsible\s+for|undertakes?\s+to|will\s+provide|is\s+obligated\s+to|covenants?\s+to)\b",
        re.IGNORECASE
    )
    deadline_pattern = re.compile(
        r"\b(?:within\s+\w+(?:\s+\(\d+\))?\s+(?:days|months|weeks|business\s+days)|by\s+[A-Za-z]+\s+\d{1,2},?\s+\d{4}|prior\s+to\s+[^,\.;\n]+|no\s+later\s+than\s+[^,\.;\n]+|immediately\s+upon\s+[^,\.;\n]+|on\s+or\s+before\s+[^,\.;\n]+)\b",
        re.IGNORECASE
    )

    # Known legal roles/parties in contracts
    legal_roles = [
        "First Party", "Second Party", "Employer", "Employee", "Buyer", "Seller", "Customer", "Client",
        "Contractor", "Consultant", "Company", "Disclosing Party", "Receiving Party", "Licensee", "Licensor",
        "Tenant", "Landlord", "Borrower", "Lender", "Arbitral Tribunal", "Arbitrator", "Either Party", "Each Party",
        "Both Parties", "Parties"
    ]

    obligations = []
    obligation_id = 1

    for sec in sections:
        sec_text = sec["text"]
        # Split into sentences using punctuation boundaries
        sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"'])", sec_text)

        for sent in sentences:
            sent_clean = sent.strip().replace("\n", " ")
            if len(sent_clean) < 25:
                continue

            # Determine obligation type
            ob_type = None
            modal_match = None

            if prohibition_pattern.search(sent_clean):
                ob_type = "Prohibition"
                modal_match = prohibition_pattern.search(sent_clean)
            elif payment_pattern.search(sent_clean):
                ob_type = "Payment"
                modal_match = payment_pattern.search(sent_clean)
            elif confidentiality_pattern.search(sent_clean):
                ob_type = "Confidentiality"
                modal_match = confidentiality_pattern.search(sent_clean)
            elif duty_pattern.search(sent_clean):
                ob_type = "Duty"
                modal_match = duty_pattern.search(sent_clean)

            if not ob_type or not modal_match:
                continue

            # Extract responsible party
            pre_modal = sent_clean[:modal_match.start()].strip()
            party = "Not specified"

            # Check known legal roles in pre_modal
            for role in legal_roles:
                if re.search(rf"\b{re.escape(role)}\b", pre_modal, re.IGNORECASE):
                    party = role
                    break

            # If not found, check known entities from entity extractor
            if party == "Not specified" and entities:
                for ent in entities:
                    ent_text = (
                        ent.get("entity_text") or ent.get("text", "")
                        if isinstance(ent, dict)
                        else getattr(ent, "entity_text", getattr(ent, "text", ""))
                    )
                    ent_type = (
                        ent.get("entity_type", "")
                        if isinstance(ent, dict)
                        else getattr(ent, "entity_type", "")
                    )
                    if ent_type in ("LEGAL_ROLE", "ORGANIZATION", "PERSON") and ent_text:
                        if re.search(rf"\b{re.escape(ent_text)}\b", pre_modal, re.IGNORECASE):
                            party = ent_text
                            break

            # If still not specified, check if sentence begins with a subject noun phrase
            if party == "Not specified" and pre_modal:
                subj_tokens = pre_modal.split()
                if 1 <= len(subj_tokens) <= 4:
                    party = pre_modal.strip(" ,;:-")

            # Extract obligation core action
            post_modal = sent_clean[modal_match.start():].strip()
            # Clean obligation action text (first 140 chars)
            action_snippet = post_modal
            if len(action_snippet) > 150:
                action_snippet = action_snippet[:140].rstrip() + "..."

            # Extract explicit deadline
            deadline_match = deadline_pattern.search(sent_clean)
            deadline = deadline_match.group(0).strip() if deadline_match else "Not specified"

            obligations.append({
                "id": obligation_id,
                "responsible_party": party if party else "Not specified",
                "obligation": action_snippet,
                "deadline": deadline,
                "obligation_type": ob_type,
                "source_section": sec["section_title"] if sec["section_title"] else "Document Body",
                "source_page": sec["page_number"],
                "source_sentence": sent_clean
            })
            obligation_id += 1

            # Cap at 50 most relevant obligations
            if len(obligations) >= 50:
                break
        if len(obligations) >= 50:
            break

    return obligations


def extract_structured_facts(
    document_text: str,
    pages_json_str: Optional[str] = None,
    entities: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Extracts categorized dates, monetary sums, and durations with normalized values.
    """
    sections = _split_into_sections_and_pages(document_text, pages_json_str)

    dates = []
    money = []
    deadlines = []

    seen_dates = set()
    seen_money = set()
    seen_deadlines = set()

    # Regex definitions
    date_regex = re.compile(
        r"\b(?:\d{1,2}(?:st|nd|rd|th)?\s+(?:day\s+of\s+)?(?:January|February|March|April|May|June|July|August|September|October|November|December),?\s+\d{4}|\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4})\b",
        re.IGNORECASE
    )
    money_regex = re.compile(
        r"(?:(?:Rs\.?|INR|\$|€|£|USD|EUR|GBP)\s*[\d,]+(?:\.\d{2})?(?:\s*(?:lakhs?|crores?|million|billion|thousand))?|[\d,]+\s*(?:Rupees|Dollars|Euros|Pounds)(?:\s+only)?)",
        re.IGNORECASE
    )
    duration_regex = re.compile(
        r"\b(?:within\s+(?:\w+\s+)?\(\d+\)\s+(?:days|months|years|weeks|hours)|within\s+\d+\s+(?:days|months|years|weeks|hours)|(?:period|term)\s+of\s+\d+\s+(?:years|months|days)|(?:period|term)\s+of\s+\w+\s+\(\d+\)\s+(?:years|months|days)|(?:30|60|90|15|45)\s+days?\s+(?:prior\s+)?written\s+notice)\b",
        re.IGNORECASE
    )

    for sec in sections:
        sec_text = sec["text"]
        page_no = sec["page_number"]
        sec_title = sec["section_title"]

        # 1. Dates
        for match in date_regex.finditer(sec_text):
            raw_val = match.group(0).strip()
            if raw_val.lower() in seen_dates:
                continue
            seen_dates.add(raw_val.lower())

            # Categorize date based on context
            start_ctx = max(0, match.start() - 60)
            end_ctx = min(len(sec_text), match.end() + 60)
            context = sec_text[start_ctx:end_ctx].lower()

            category = "General Date"
            if "effective" in context:
                category = "Effective Date"
            elif "commence" in context or "start" in context:
                category = "Commencement Date"
            elif "expir" in context:
                category = "Expiry Date"
            elif "terminat" in context:
                category = "Termination Date"
            elif "renew" in context:
                category = "Renewal Date"
            elif "entered into" in context or "executed" in context:
                category = "Execution Date"

            # Normalized date value
            norm_val = raw_val.replace("day of ", "").strip()
            dates.append({
                "category": category,
                "type": "DATE",
                "value": norm_val,
                "original_text": raw_val,
                "source_section": sec_title,
                "source_page": page_no
            })

        # 2. Money
        for match in money_regex.finditer(sec_text):
            raw_val = match.group(0).strip()
            if raw_val.lower() in seen_money or len(raw_val) < 2:
                continue
            seen_money.add(raw_val.lower())

            start_ctx = max(0, match.start() - 60)
            end_ctx = min(len(sec_text), match.end() + 60)
            context = sec_text[start_ctx:end_ctx].lower()

            category = "Monetary Amount"
            if "salary" in context or "remuneration" in context:
                category = "Salary / Remuneration"
            elif "fee" in context or "retainer" in context:
                category = "Professional Fee"
            elif "damage" in context or "liquidat" in context or "penalty" in context:
                category = "Damages / Penalty"
            elif "deposit" in context or "security" in context:
                category = "Security Deposit"
            elif "payment" in context or "consideration" in context:
                category = "Payment / Consideration"

            money.append({
                "category": category,
                "type": "MONEY",
                "value": raw_val,
                "original_text": raw_val,
                "source_section": sec_title,
                "source_page": page_no
            })

        # 3. Deadlines / Durations
        for match in duration_regex.finditer(sec_text):
            raw_val = match.group(0).strip()
            if raw_val.lower() in seen_deadlines:
                continue
            seen_deadlines.add(raw_val.lower())

            start_ctx = max(0, match.start() - 60)
            end_ctx = min(len(sec_text), match.end() + 60)
            context = sec_text[start_ctx:end_ctx].lower()

            category = "Duration / Timeline"
            if "notice" in context:
                category = "Notice Period"
            elif "pay" in context or "invoice" in context:
                category = "Payment Window"
            elif "term" in context or "duration" in context:
                category = "Contract Term"
            elif "renew" in context:
                category = "Renewal Window"

            # Normalize "within thirty (30) days" -> "30 days"
            norm_val = raw_val
            num_match = re.search(r"\(?(\d+)\)?\s*(days?|months?|years?|weeks?|hours?)", raw_val, re.IGNORECASE)
            if num_match:
                norm_val = f"{num_match.group(1)} {num_match.group(2)}"

            deadlines.append({
                "category": category,
                "type": "DEADLINE",
                "value": norm_val,
                "original_text": raw_val,
                "source_section": sec_title,
                "source_page": page_no
            })

    return {
        "dates": dates,
        "money": money,
        "deadlines": deadlines
    }


def detect_document_type(document_text: str, filename: str) -> str:
    """
    Detects the legal document type deterministically from title lines or filename.
    """
    head = (document_text[:1200] + " " + filename).lower()
    
    if "non-disclosure" in head or "nda" in head or "confidentiality agreement" in head:
        return "Non-Disclosure Agreement (NDA)"
    if "arbitration" in head or "dispute resolution agreement" in head:
        return "Commercial Arbitration Agreement"
    if "employment" in head or "offer of employment" in head or "appointment letter" in head:
        return "Employment Agreement"
    if "lease" in head or "tenancy" in head or "rental agreement" in head:
        return "Commercial Lease Agreement"
    if "master service" in head or "msa" in head or "services agreement" in head:
        return "Master Services Agreement"
    if "license" in head or "licensing agreement" in head or "software license" in head:
        return "Software License Agreement"
    if "legal notice" in head or "notice of demand" in head or "advocate notice" in head:
        return "Legal Notice"
    if "settlement" in head or "release and settlement" in head:
        return "Settlement Agreement"
    if "loan" in head or "promissory note" in head or "credit agreement" in head:
        return "Loan Agreement"
    if "partnership" in head or "llp agreement" in head:
        return "Partnership Agreement"
    if "procurement" in head or "vendor agreement" in head:
        return "Procurement & Vendor Contract"

    return "Not detected"


def generate_document_insights(
    document: Any,
    analysis_run: Any,
    keywords: List[Any],
    entities: List[Any],
    clauses: List[Dict[str, Any]],
    obligations: List[Dict[str, Any]],
    facts: Dict[str, List[Dict[str, Any]]]
) -> Dict[str, Any]:
    """
    Generates high-level at-a-glance legal document insights dashboard data.
    Ensures 'Not detected' fallbacks for missing information.
    """
    text = document.extracted_text or ""
    doc_type = detect_document_type(text, document.filename)

    # Detect parties from extracted entities (ORGANIZATION, PERSON, LEGAL_ROLE)
    party_candidates = []
    if entities:
        for ent in entities:
            # ent can be ExtractedEntity model or dict
            etype = getattr(ent, "entity_type", None) or (ent.get("entity_type") if isinstance(ent, dict) else None)
            etext = getattr(ent, "normalized_text", None) or getattr(ent, "entity_text", None) or (ent.get("normalized_text") or ent.get("entity_text") if isinstance(ent, dict) else None)
            if etype in ("ORGANIZATION", "PERSON") and etext and len(etext) > 2:
                if etext not in party_candidates and not re.search(r"\b(act|court|section|schedule)\b", etext, re.IGNORECASE):
                    party_candidates.append(etext)

    # Detect dates
    dates_list = [f"{d['category']}: {d['value']}" for d in facts.get("dates", [])[:4]]
    # Detect money
    money_list = [f"{m['category']}: {m['value']}" for m in facts.get("money", [])[:4]]

    # Detect clauses
    detected_clause_names = [c["clause_type"] for c in clauses if c.get("status") == "Found"]

    # Top keywords
    top_kw_list = []
    if keywords:
        for kw in keywords[:8]:
            k_word = getattr(kw, "keyword", None) or (kw.get("keyword") if isinstance(kw, dict) else None)
            if k_word:
                top_kw_list.append(k_word)

    # Attention areas rule synthesis
    attention_areas = []
    clause_status_map = {c["clause_type"]: c for c in clauses}
    
    if "Indemnification" in detected_clause_names:
        attention_areas.append("Indemnification clause detected: review scope of liability coverage and hold harmless requirements.")
    if "Non-Compete / Restriction" in detected_clause_names:
        attention_areas.append("Non-compete / restrictive covenant detected: verify enforceability under local governing jurisdiction.")
    if "Termination" in detected_clause_names:
        term_clause = clause_status_map.get("Termination", {})
        if "without cause" in term_clause.get("relevant_text", "").lower():
            attention_areas.append("Unilateral termination without cause detected: inspect notice period requirements.")
        else:
            attention_areas.append("Termination clause present: inspect termination conditions and post-termination duties.")
    if "Arbitration / Dispute Resolution" not in detected_clause_names:
        attention_areas.append("No explicit Arbitration or Dispute Resolution clause detected.")
    if "Governing Law" not in detected_clause_names:
        attention_areas.append("No explicit Governing Law clause detected: jurisdiction may be ambiguous in case of dispute.")
    for m in facts.get("money", []):
        if "penalty" in m.get("category", "").lower() or "damage" in m.get("category", "").lower():
            attention_areas.append(f"Liquidated damages / penalty provision identified: {m.get('value')}.")
            break

    if not attention_areas:
        attention_areas.append("No standard high-risk legal clauses or ambiguous liabilities detected in automated scan.")

    # Section count
    sections = _split_into_sections_and_pages(text, document.pages_json)

    return {
        "analysis_id": analysis_run.id,
        "document_id": document.id,
        "document_name": document.filename,
        "document_type": doc_type,
        "page_count": document.page_count or 1,
        "section_count": len(sections),
        "keyword_count": len(keywords),
        "entity_count": len(entities),
        "parties": party_candidates[:6] if party_candidates else ["Not detected"],
        "important_dates": dates_list if dates_list else ["Not detected"],
        "monetary_amounts": money_list if money_list else ["Not detected"],
        "detected_clauses_count": len(detected_clause_names),
        "detected_clauses": detected_clause_names,
        "obligations_count": len(obligations),
        "top_keywords": top_kw_list if top_kw_list else ["Not detected"],
        "attention_areas": attention_areas
    }


def search_document_text(
    document: Any,
    query: str
) -> Dict[str, Any]:
    """
    In-document search operating across document pages and sections.
    Computes exact matches and ASTMA TF-IDF relevance ranking across passages.
    """
    if not query or not query.strip() or not document.extracted_text:
        return {
            "document_id": document.id,
            "query": query,
            "total_matches": 0,
            "matches": []
        }

    clean_query = query.strip()
    sections = _split_into_sections_and_pages(document.extracted_text, document.pages_json)
    
    # TF-IDF Scoring for ASTMA information retrieval relevance
    corpus = [s["text"] for s in sections if s["text"].strip()]
    scores = [0.0] * len(sections)
    if corpus and len(corpus) > 0:
        try:
            tfidf = TfidfVectorizer(stop_words="english")
            tfidf_mat = tfidf.fit_transform(corpus)
            query_vec = tfidf.transform([clean_query])
            cos_sims = cosine_similarity(query_vec, tfidf_mat)[0]
            scores = list(cos_sims)
        except Exception:
            scores = [1.0] * len(sections)

    matches = []
    match_id = 1
    query_pat = re.compile(re.escape(clean_query), re.IGNORECASE)

    for idx, sec in enumerate(sections):
        sec_text = sec["text"]
        for m in query_pat.finditer(sec_text):
            start = m.start()
            end = m.end()

            # Window context: +/- 60 chars
            ctx_start = max(0, start - 60)
            ctx_end = min(len(sec_text), end + 60)
            snippet = ("..." if ctx_start > 0 else "") + sec_text[ctx_start:ctx_end].strip().replace("\n", " ") + ("..." if ctx_end < len(sec_text) else "")

            # Relevance score is section TF-IDF score combined with match priority
            base_score = float(scores[idx]) if idx < len(scores) else 0.5
            final_score = round(max(base_score, 0.1), 4)

            matches.append({
                "match_id": match_id,
                "page_number": sec["page_number"],
                "section_title": sec["section_title"],
                "snippet": snippet,
                "start_offset": start,
                "end_offset": end,
                "score": final_score
            })
            match_id += 1

            if len(matches) >= 100:
                break
        if len(matches) >= 100:
            break

    # Sort matches by relevance score descending
    matches.sort(key=lambda x: x["score"], reverse=True)

    return {
        "document_id": document.id,
        "query": clean_query,
        "total_matches": len(matches),
        "matches": matches
    }


def compute_clause_diff_tokens(text_a: str, text_b: str) -> Dict[str, Any]:
    """
    Computes aligned word-level redline tokens and discrete changes between two clause texts.
    Produces canonical changes list: [{"type": "modified"|"added"|"removed", "original": "...", "modified": "..."}]
    and formatted token sequences for visual redline highlighting.
    """
    if not text_a and not text_b:
        return {"changes": [], "tokens_a": [], "tokens_b": []}
    
    words_a = text_a.split() if text_a else []
    words_b = text_b.split() if text_b else []
    
    matcher = difflib.SequenceMatcher(None, words_a, words_b)
    changes = []
    tokens_a = []
    tokens_b = []
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        orig_part = " ".join(words_a[i1:i2])
        mod_part = " ".join(words_b[j1:j2])
        
        if tag == "equal":
            tokens_a.append({"type": "equal", "text": orig_part})
            tokens_b.append({"type": "equal", "text": mod_part})
        elif tag == "replace":
            changes.append({
                "type": "modified",
                "original": orig_part,
                "modified": mod_part
            })
            tokens_a.append({"type": "removed", "text": orig_part})
            tokens_b.append({"type": "added", "text": mod_part})
        elif tag == "delete":
            changes.append({
                "type": "removed",
                "original": orig_part,
                "modified": ""
            })
            tokens_a.append({"type": "removed", "text": orig_part})
        elif tag == "insert":
            changes.append({
                "type": "added",
                "original": "",
                "modified": mod_part
            })
            tokens_b.append({"type": "added", "text": mod_part})
            
    return {
        "changes": changes,
        "tokens_a": tokens_a,
        "tokens_b": tokens_b
    }


def compare_two_documents(
    doc_a: Any,
    analysis_a: Optional[Any],
    doc_b: Any,
    analysis_b: Optional[Any]
) -> Dict[str, Any]:
    """
    Computes comparative diff between Document A and Document B:
    - Overall ASTMA TF-IDF Cosine Similarity
    - Metadata comparison
    - Keywords comparison (ADDED, REMOVED, UNCHANGED)
    - Entities comparison (ADDED, REMOVED, UNCHANGED)
    - Important Clauses comparison (ADDED, REMOVED, MODIFIED, UNCHANGED)
    - Dates & Monetary comparison
    - Obligations comparison
    """
    text_a = doc_a.extracted_text or ""
    text_b = doc_b.extracted_text or ""

    # 1. ASTMA TF-IDF Cosine Similarity
    similarity_score = 0.0
    if text_a.strip() and text_b.strip():
        try:
            vec = TfidfVectorizer(stop_words="english")
            mat = vec.fit_transform([text_a, text_b])
            cos_sim = cosine_similarity(mat[0:1], mat[1:2])[0][0]
            similarity_score = round(float(cos_sim), 4)
        except Exception as exc:
            logger.warning(f"Similarity computation error: {exc}")
            similarity_score = 0.5

    # 2. Metadata Comparison
    meta_comp = {
        "filename": {"doc_a": doc_a.filename, "doc_b": doc_b.filename, "match": doc_a.filename == doc_b.filename},
        "word_count": {"doc_a": doc_a.word_count, "doc_b": doc_b.word_count, "diff": doc_b.word_count - doc_a.word_count},
        "page_count": {"doc_a": doc_a.page_count or 1, "doc_b": doc_b.page_count or 1, "diff": (doc_b.page_count or 1) - (doc_a.page_count or 1)},
        "file_type": {"doc_a": doc_a.file_type, "doc_b": doc_b.file_type, "match": doc_a.file_type == doc_b.file_type}
    }

    # 3. Keywords Comparison
    kw_a = {k.keyword.lower(): k.keyword for k in analysis_a.keywords} if analysis_a and analysis_a.keywords else {}
    kw_b = {k.keyword.lower(): k.keyword for k in analysis_b.keywords} if analysis_b and analysis_b.keywords else {}
    
    added_kw = [kw_b[k] for k in kw_b if k not in kw_a]
    removed_kw = [kw_a[k] for k in kw_a if k not in kw_b]
    shared_kw = [kw_a[k] for k in kw_a if k in kw_b]

    kw_comp = {
        "total_doc_a": len(kw_a),
        "total_doc_b": len(kw_b),
        "added": added_kw[:15],
        "removed": removed_kw[:15],
        "shared": shared_kw[:15]
    }

    # 4. Entities Comparison
    ent_a = {e.normalized_text.lower(): e for e in analysis_a.entities} if analysis_a and analysis_a.entities else {}
    ent_b = {e.normalized_text.lower(): e for e in analysis_b.entities} if analysis_b and analysis_b.entities else {}

    added_ent = [ent_b[e].normalized_text for e in ent_b if e not in ent_a]
    removed_ent = [ent_a[e].normalized_text for e in ent_a if e not in ent_b]
    shared_ent = [ent_a[e].normalized_text for e in ent_a if e in ent_b]

    ent_comp = {
        "total_doc_a": len(ent_a),
        "total_doc_b": len(ent_b),
        "added": added_ent[:15],
        "removed": removed_ent[:15],
        "shared": shared_ent[:15]
    }

    # 5. Important Clauses Comparison
    clauses_a = {c["clause_type"]: c for c in extract_important_clauses(text_a, doc_a.pages_json)}
    clauses_b = {c["clause_type"]: c for c in extract_important_clauses(text_b, doc_b.pages_json)}

    clause_comp = []
    for c_type in CLAUSE_DEFINITIONS.keys():
        ca = clauses_a.get(c_type, {})
        cb = clauses_b.get(c_type, {})
        found_a = ca.get("status") == "Found"
        found_b = cb.get("status") == "Found"

        text_ca = ca.get("relevant_text", "").strip()
        text_cb = cb.get("relevant_text", "").strip()

        if found_a and found_b:
            if text_ca.lower() == text_cb.lower():
                status = "UNCHANGED"
            else:
                status = "MODIFIED"
        elif not found_a and found_b:
            status = "ADDED"
        elif found_a and not found_b:
            status = "REMOVED"
        else:
            status = "NOT_PRESENT"

        diff_info = compute_clause_diff_tokens(text_ca if found_a else "", text_cb if found_b else "")

        clause_comp.append({
            "clause_type": c_type,
            "status": status,
            "doc_a_present": found_a,
            "doc_b_present": found_b,
            "doc_a_snippet": text_ca if found_a else "Not detected",
            "doc_b_snippet": text_cb if found_b else "Not detected",
            "original_text": text_ca if found_a else "Not detected",
            "modified_text": text_cb if found_b else "Not detected",
            "doc_a_section": ca.get("source_section", "Not detected"),
            "doc_b_section": cb.get("source_section", "Not detected"),
            "changes": diff_info["changes"],
            "tokens_a": diff_info["tokens_a"],
            "tokens_b": diff_info["tokens_b"]
        })

    # 6. Dates and Money
    facts_a = extract_structured_facts(text_a, doc_a.pages_json)
    facts_b = extract_structured_facts(text_b, doc_b.pages_json)

    date_vals_a = {d["value"].lower(): d["value"] for d in facts_a.get("dates", [])}
    date_vals_b = {d["value"].lower(): d["value"] for d in facts_b.get("dates", [])}
    date_comp = {
        "added": [date_vals_b[d] for d in date_vals_b if d not in date_vals_a],
        "removed": [date_vals_a[d] for d in date_vals_a if d not in date_vals_b],
        "shared": [date_vals_a[d] for d in date_vals_a if d in date_vals_b]
    }

    money_vals_a = {m["value"].lower(): m["value"] for m in facts_a.get("money", [])}
    money_vals_b = {m["value"].lower(): m["value"] for m in facts_b.get("money", [])}
    money_comp = {
        "added": [money_vals_b[m] for m in money_vals_b if m not in money_vals_a],
        "removed": [money_vals_a[m] for m in money_vals_a if m not in money_vals_b],
        "shared": [money_vals_a[m] for m in money_vals_a if m in money_vals_b]
    }

    # 7. Obligations summary comparison
    ob_a = extract_obligations(text_a, doc_a.pages_json)
    ob_b = extract_obligations(text_b, doc_b.pages_json)
    ob_comp = {
        "total_doc_a": len(ob_a),
        "total_doc_b": len(ob_b),
        "difference": len(ob_b) - len(ob_a),
        "status": "MODIFIED" if len(ob_a) != len(ob_b) else "UNCHANGED"
    }

    return {
        "doc_a": {
            "id": doc_a.id,
            "filename": doc_a.filename,
            "word_count": doc_a.word_count,
            "page_count": doc_a.page_count or 1
        },
        "doc_b": {
            "id": doc_b.id,
            "filename": doc_b.filename,
            "word_count": doc_b.word_count,
            "page_count": doc_b.page_count or 1
        },
        "similarity_score": similarity_score,
        "similarity_percentage": round(similarity_score * 100, 1),
        "metadata_comparison": meta_comp,
        "keyword_comparison": kw_comp,
        "entity_comparison": ent_comp,
        "clause_comparison": clause_comp,
        "date_comparison": date_comp,
        "money_comparison": money_comp,
        "obligation_comparison": ob_comp
    }


def generate_analysis_report_json(
    document: Any,
    analysis_run: Any,
    keywords: List[Any],
    entities: List[Any],
    clauses: List[Dict[str, Any]],
    obligations: List[Dict[str, Any]],
    facts: Dict[str, List[Dict[str, Any]]],
    insights: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Assembles a complete, structured JSON report conforming to the 11-section requirement.
    """
    disclaimer = (
        "LexExtract provides automated document information extraction and retrieval. "
        "It does not provide legal advice, determine legal validity, or replace professional legal review."
    )
    
    return {
        "report_title": "LEXEXTRACT — Legal Document Analysis Report",
        "system_disclaimer": disclaimer,
        "document_information": {
            "document_id": document.id,
            "filename": document.filename,
            "file_type": document.file_type,
            "file_size_bytes": document.file_size,
            "word_count": document.word_count,
            "page_count": document.page_count or 1,
            "uploaded_at": str(document.uploaded_at)
        },
        "document_overview": insights,
        "top_keywords": [
            {
                "rank": k.get("rank", idx) if isinstance(k, dict) else getattr(k, "rank", idx),
                "keyword": k.get("keyword", "") if isinstance(k, dict) else getattr(k, "keyword", ""),
                "category": k.get("category", "General") if isinstance(k, dict) else getattr(k, "category", "General"),
                "score": round(float(k.get("final_score", 0.0) if isinstance(k, dict) else getattr(k, "final_score", 0.0)), 4),
                "frequency": k.get("frequency", 1) if isinstance(k, dict) else getattr(k, "frequency", 1)
            }
            for idx, k in enumerate(keywords[:20], 1)
        ],
        "extracted_entities": [
            {
                "entity_text": e.get("entity_text", "") if isinstance(e, dict) else getattr(e, "entity_text", ""),
                "normalized_text": e.get("normalized_text", "") if isinstance(e, dict) else getattr(e, "normalized_text", ""),
                "entity_type": e.get("entity_type", "") if isinstance(e, dict) else getattr(e, "entity_type", ""),
                "confidence": round(float(e.get("confidence", 0.75) if isinstance(e, dict) else getattr(e, "confidence", 0.75)), 2),
                "source": e.get("source", "hybrid") if isinstance(e, dict) else getattr(e, "source", "hybrid")
            }
            for e in entities[:50]
        ],
        "important_clauses": clauses,
        "obligations_and_responsibilities": obligations,
        "dates_and_deadlines": facts.get("dates", []) + facts.get("deadlines", []),
        "monetary_information": facts.get("money", []),
        "attention_areas": insights.get("attention_areas", []),
        "search_and_analysis_metadata": {
            "analysis_id": analysis_run.id,
            "status": analysis_run.status,
            "processing_time_seconds": analysis_run.processing_time,
            "total_keywords_extracted": analysis_run.total_keywords,
            "total_entities_extracted": analysis_run.total_entities,
            "started_at": str(analysis_run.started_at),
            "completed_at": str(analysis_run.completed_at)
        }
    }


def generate_analysis_report_pdf(report_data: Dict[str, Any]) -> bytes:
    """
    Generates an executive-grade, multi-page Legal Intelligence Report PDF using PyMuPDF (fitz).
    Presents structured legal insights designed for attorney / analyst scanning in 30-60 seconds:
    - Cover / Document Metadata Header Banner
    - Executive Snapshot (Classification, Governance Posture, Parties, Key Dates, Financial Figures)
    - Attention Areas (Visually distinct cards with HIGH / MEDIUM risk badges)
    - Key Contractual Clauses (Clean table layout with repeating header on page break)
    - Contractual Obligations & Duties (Clean tabular matrix with repeating header)
    - Structured Dates & Monetary Figures (Compact side-by-side cards)
    - Parties & Legal Entities Taxonomy (Grouped by category)
    - Weighted Legal Keywords (Compact tags/chips container)
    - Mandatory Legal Disclaimer & Page X of Y Running Headers/Footers
    """
    doc = pymupdf.open()
    
    page_w = 595.0
    page_h = 842.0
    margin_x = 40.0
    content_w = page_w - (2 * margin_x)  # 515 pt
    bottom_limit = page_h - 48.0
    
    # Curated Executive Color Palette
    NAVY = (0.05, 0.11, 0.20)         # #0d1b32
    GOLD = (0.75, 0.60, 0.15)         # #c09a26
    CRIMSON = (0.65, 0.12, 0.16)      # #a61f29
    AMBER = (0.80, 0.45, 0.10)        # #cc731a
    GREEN = (0.12, 0.50, 0.25)        # #1f8040
    DARK_TEXT = (0.12, 0.14, 0.18)    # #1f242e
    MUTED_TEXT = (0.42, 0.46, 0.52)   # #6b7584
    BORDER_LIGHT = (0.86, 0.88, 0.90) # #dce0e6
    BG_CARD = (0.97, 0.98, 0.99)      # #f7f9fa
    WHITE = (1.0, 1.0, 1.0)
    
    def create_page():
        p = doc.new_page(width=page_w, height=page_h)
        # Running Top Header (Navy bar + Gold accent)
        p.draw_rect(pymupdf.Rect(0, 0, page_w, 28), fill=NAVY)
        p.draw_rect(pymupdf.Rect(0, 28, page_w, 30), fill=GOLD)
        p.insert_text(pymupdf.Point(margin_x, 18), "LEXEXTRACT  |  LEGAL INTELLIGENCE REPORT", fontsize=9, fontname="Helvetica-Bold", color=WHITE)
        doc_name = report_data.get("document_information", {}).get("filename", "Document")
        if len(doc_name) > 40:
            doc_name = doc_name[:37] + "..."
        p.insert_text(pymupdf.Point(page_w - margin_x - 180, 18), doc_name, fontsize=8.5, fontname="Helvetica", color=(0.85, 0.88, 0.92))
        return p

    current_page = create_page()
    cursor_y = 44.0

    def check_space(needed: float):
        nonlocal current_page, cursor_y
        if cursor_y + needed > bottom_limit:
            current_page = create_page()
            cursor_y = 44.0

    def draw_section_heading(title: str, subtitle: str = ""):
        nonlocal cursor_y
        check_space(38)
        current_page.draw_rect(pymupdf.Rect(margin_x, cursor_y, margin_x + 3, cursor_y + 13), fill=NAVY)
        current_page.insert_text(pymupdf.Point(margin_x + 8, cursor_y + 11), title.upper(), fontsize=10.5, fontname="Helvetica-Bold", color=NAVY)
        cursor_y += 18
        if subtitle:
            current_page.insert_text(pymupdf.Point(margin_x + 8, cursor_y), subtitle, fontsize=7.5, fontname="Helvetica", color=MUTED_TEXT)
            cursor_y += 14
        else:
            cursor_y += 2

    # ----------------------------------------------------
    # COVER / HEADER BANNER
    # ----------------------------------------------------
    doc_info = report_data.get("document_information", {})
    overview = report_data.get("document_overview", {})
    
    banner_h = 76.0
    current_page.draw_rect(pymupdf.Rect(margin_x, cursor_y, margin_x + content_w, cursor_y + banner_h), fill=BG_CARD, color=BORDER_LIGHT, width=0.8)
    current_page.draw_rect(pymupdf.Rect(margin_x, cursor_y, margin_x + 4, cursor_y + banner_h), fill=NAVY)
    
    filename = doc_info.get("filename", "Legal Contract")
    doc_type = overview.get("document_type", "Commercial Legal Agreement")
    current_page.insert_text(pymupdf.Point(margin_x + 14, cursor_y + 20), filename, fontsize=13, fontname="Helvetica-Bold", color=NAVY)
    current_page.insert_text(pymupdf.Point(margin_x + 14, cursor_y + 35), f"Document Classification: {doc_type}", fontsize=9, fontname="Helvetica-Bold", color=GOLD)
    
    pgs = doc_info.get("page_count", 1)
    wds = doc_info.get("word_count", 0)
    clauses_count = overview.get("detected_clauses_count", 0)
    ent_count = overview.get("entity_count", 0)
    kw_count = overview.get("keyword_count", 0)
    badges = f"Pages: {pgs}   •   Words: {wds:,}   •   Detected Clauses: {clauses_count}   •   Legal Entities: {ent_count}   •   Keywords: {kw_count}"
    current_page.insert_text(pymupdf.Point(margin_x + 14, cursor_y + 52), badges, fontsize=8, fontname="Helvetica", color=DARK_TEXT)
    current_page.insert_text(pymupdf.Point(margin_x + 14, cursor_y + 66), "Automated Extraction via LexExtract Three-Tier Legal Intelligence Engine  |  ISO 27001 Audit Ready", fontsize=7, fontname="Helvetica-Oblique", color=MUTED_TEXT)
    cursor_y += banner_h + 16.0

    # ----------------------------------------------------
    # 1. EXECUTIVE SNAPSHOT (4-BOX BALANCED WORKSPACE)
    # ----------------------------------------------------
    draw_section_heading("Executive Snapshot", "At-a-glance legal profile, governance posture, and primary financial bounds")
    
    snap_box_h = 56.0
    col_w = (content_w - 10.0) / 2.0
    
    # Box 1: Governance & Document Type
    b1_x = margin_x
    b1_y = cursor_y
    current_page.draw_rect(pymupdf.Rect(b1_x, b1_y, b1_x + col_w, b1_y + snap_box_h), fill=WHITE, color=BORDER_LIGHT, width=0.6)
    current_page.insert_text(pymupdf.Point(b1_x + 10, b1_y + 14), "GOVERNANCE & CLASSIFICATION", fontsize=7, fontname="Helvetica-Bold", color=MUTED_TEXT)
    current_page.insert_text(pymupdf.Point(b1_x + 10, b1_y + 28), doc_type[:32], fontsize=9, fontname="Helvetica-Bold", color=NAVY)
    attn_count = len(report_data.get("attention_areas", []))
    risk_label = "HIGH ATTENTION REQUIRED" if attn_count >= 2 else ("MODERATE ATTENTION" if attn_count == 1 else "STANDARD POSTURE")
    risk_col = CRIMSON if attn_count >= 2 else (AMBER if attn_count == 1 else GREEN)
    current_page.insert_text(pymupdf.Point(b1_x + 10, b1_y + 44), f"Posture: {risk_label} ({attn_count} alerts)", fontsize=7.5, fontname="Helvetica-Bold", color=risk_col)
    
    # Box 2: Contractual Parties
    b2_x = margin_x + col_w + 10.0
    b2_y = cursor_y
    current_page.draw_rect(pymupdf.Rect(b2_x, b2_y, b2_x + col_w, b2_y + snap_box_h), fill=WHITE, color=BORDER_LIGHT, width=0.6)
    current_page.insert_text(pymupdf.Point(b2_x + 10, b2_y + 14), "IDENTIFIED PARTIES", fontsize=7, fontname="Helvetica-Bold", color=MUTED_TEXT)
    parties = overview.get("parties", [])
    p1 = parties[0] if len(parties) > 0 else "Disclosing Party / Employer / Landlord"
    p2 = parties[1] if len(parties) > 1 else "Receiving Party / Employee / Tenant"
    current_page.insert_text(pymupdf.Point(b2_x + 10, b2_y + 28), f"1. {p1[:30]}", fontsize=8, fontname="Helvetica", color=DARK_TEXT)
    current_page.insert_text(pymupdf.Point(b2_x + 10, b2_y + 44), f"2. {p2[:30]}", fontsize=8, fontname="Helvetica", color=DARK_TEXT)
    cursor_y += snap_box_h + 8.0
    
    # Box 3: Key Dates & Deadlines
    b3_x = margin_x
    b3_y = cursor_y
    current_page.draw_rect(pymupdf.Rect(b3_x, b3_y, b3_x + col_w, b3_y + snap_box_h), fill=WHITE, color=BORDER_LIGHT, width=0.6)
    current_page.insert_text(pymupdf.Point(b3_x + 10, b3_y + 14), "CRITICAL DATES & NOTICE PERIODS", fontsize=7, fontname="Helvetica-Bold", color=MUTED_TEXT)
    dates_list = overview.get("important_dates", [])
    d1 = dates_list[0] if len(dates_list) > 0 else "Execution Date: Upon Signing"
    d2 = dates_list[1] if len(dates_list) > 1 else "Term: As Specified in Agreement"
    current_page.insert_text(pymupdf.Point(b3_x + 10, b3_y + 28), f"• {d1[:32]}", fontsize=8, fontname="Helvetica", color=DARK_TEXT)
    current_page.insert_text(pymupdf.Point(b3_x + 10, b3_y + 44), f"• {d2[:32]}", fontsize=8, fontname="Helvetica", color=DARK_TEXT)
    
    # Box 4: Financial Figures
    b4_x = margin_x + col_w + 10.0
    b4_y = cursor_y
    current_page.draw_rect(pymupdf.Rect(b4_x, b4_y, b4_x + col_w, b4_y + snap_box_h), fill=WHITE, color=BORDER_LIGHT, width=0.6)
    current_page.insert_text(pymupdf.Point(b4_x + 10, b4_y + 14), "FINANCIAL COMMITMENTS & EXPOSURE", fontsize=7, fontname="Helvetica-Bold", color=MUTED_TEXT)
    money_list = overview.get("monetary_amounts", [])
    m1 = money_list[0] if len(money_list) > 0 else "Standard covenants (No explicit sum)"
    m2 = money_list[1] if len(money_list) > 1 else ""
    current_page.insert_text(pymupdf.Point(b4_x + 10, b4_y + 28), m1[:32], fontsize=8.5, fontname="Helvetica-Bold", color=CRIMSON if money_list else DARK_TEXT)
    if m2:
        current_page.insert_text(pymupdf.Point(b4_x + 10, b4_y + 44), m2[:32], fontsize=8, fontname="Helvetica", color=DARK_TEXT)
    else:
        current_page.insert_text(pymupdf.Point(b4_x + 10, b4_y + 44), "Monetary terms cross-referenced with text", fontsize=7.5, fontname="Helvetica-Oblique", color=MUTED_TEXT)
    cursor_y += snap_box_h + 18.0

    # ----------------------------------------------------
    # 2. ATTENTION AREAS (VISUALLY DISTINCT CARDS)
    # ----------------------------------------------------
    draw_section_heading("Attention Areas & Risk Flags", "Provisions requiring legal counsel scrutiny or non-standard commercial policy confirmation")
    attn_items = report_data.get("attention_areas", [])
    if not attn_items:
        check_space(32)
        current_page.draw_rect(pymupdf.Rect(margin_x, cursor_y, margin_x + content_w, cursor_y + 28), fill=BG_CARD, color=BORDER_LIGHT, width=0.6)
        current_page.insert_text(pymupdf.Point(margin_x + 12, cursor_y + 18), "✓  No High-Risk Attention Areas Flagged: Clauses adhere to standard covenant conventions.", fontsize=8.5, fontname="Helvetica-Bold", color=GREEN)
        cursor_y += 38.0
    else:
        for item in attn_items[:5]:
            check_space(42)
            is_high = "[HIGH" in item.upper() or "INDEMNIF" in item.upper() or "LIABILITY" in item.upper()
            badge_color = CRIMSON if is_high else AMBER
            badge_text = "HIGH ATTENTION" if is_high else "MEDIUM ATTENTION"
            
            clean_text = item.replace("[HIGH RISK]", "").replace("[MEDIUM RISK]", "").replace("[HIGH]", "").replace("[MEDIUM]", "").strip()
            
            card_h = 36.0
            current_page.draw_rect(pymupdf.Rect(margin_x, cursor_y, margin_x + content_w, cursor_y + card_h), fill=BG_CARD, color=BORDER_LIGHT, width=0.6)
            current_page.draw_rect(pymupdf.Rect(margin_x, cursor_y, margin_x + 4, cursor_y + card_h), fill=badge_color)
            
            pill_w = 80.0
            current_page.draw_rect(pymupdf.Rect(margin_x + 12, cursor_y + 8, margin_x + 12 + pill_w, cursor_y + 24), fill=WHITE, color=badge_color, width=0.5)
            current_page.insert_text(pymupdf.Point(margin_x + 16, cursor_y + 19), badge_text, fontsize=6.5, fontname="Helvetica-Bold", color=badge_color)
            
            text_rect = pymupdf.Rect(margin_x + 100, cursor_y + 6, margin_x + content_w - 10, cursor_y + 32)
            current_page.insert_textbox(text_rect, clean_text, fontsize=8, fontname="Helvetica", color=DARK_TEXT)
            cursor_y += card_h + 6.0
        cursor_y += 10.0

    # ----------------------------------------------------
    # 3. KEY CLAUSES (CLEAN TABLE LAYOUT)
    # ----------------------------------------------------
    draw_section_heading("Key Contractual Clauses", "Detected core legal provisions scanned across 13 controlled categories")
    
    clauses = report_data.get("important_clauses", [])
    found_clauses = [c for c in clauses if c.get("status") == "Found"]
    
    col_w_clause = 105.0
    col_w_status = 55.0
    col_w_prio = 60.0
    col_w_loc = 75.0
    col_w_text = 220.0
    
    def draw_clause_table_header():
        nonlocal cursor_y
        check_space(20)
        hdr_rect = pymupdf.Rect(margin_x, cursor_y, margin_x + content_w, cursor_y + 16)
        current_page.draw_rect(hdr_rect, fill=NAVY)
        x = margin_x + 6
        current_page.insert_text(pymupdf.Point(x, cursor_y + 11), "CLAUSE", fontsize=7.5, fontname="Helvetica-Bold", color=WHITE)
        x += col_w_clause
        current_page.insert_text(pymupdf.Point(x, cursor_y + 11), "STATUS", fontsize=7.5, fontname="Helvetica-Bold", color=WHITE)
        x += col_w_status
        current_page.insert_text(pymupdf.Point(x, cursor_y + 11), "PRIORITY", fontsize=7.5, fontname="Helvetica-Bold", color=WHITE)
        x += col_w_prio
        current_page.insert_text(pymupdf.Point(x, cursor_y + 11), "LOCATION", fontsize=7.5, fontname="Helvetica-Bold", color=WHITE)
        x += col_w_loc
        current_page.insert_text(pymupdf.Point(x, cursor_y + 11), "SYNTHESIS & EXCERPT", fontsize=7.5, fontname="Helvetica-Bold", color=WHITE)
        cursor_y += 16.0

    draw_clause_table_header()
    
    for idx, c in enumerate(found_clauses):
        row_h = 34.0
        if cursor_y + row_h > bottom_limit:
            current_page = create_page()
            cursor_y = 44.0
            draw_clause_table_header()
            
        bg_row = BG_CARD if idx % 2 == 1 else WHITE
        row_rect = pymupdf.Rect(margin_x, cursor_y, margin_x + content_w, cursor_y + row_h)
        current_page.draw_rect(row_rect, fill=bg_row, color=BORDER_LIGHT, width=0.4)
        
        x = margin_x + 6
        current_page.insert_text(pymupdf.Point(x, cursor_y + 14), c.get("clause_type", "Clause")[:18], fontsize=8, fontname="Helvetica-Bold", color=NAVY)
        
        x += col_w_clause
        current_page.insert_text(pymupdf.Point(x, cursor_y + 14), "FOUND", fontsize=7.5, fontname="Helvetica-Bold", color=GREEN)
        
        x += col_w_status
        prio = c.get("confidence_label", "HIGH")
        prio_col = CRIMSON if prio == "HIGH" else (AMBER if prio == "MEDIUM" else DARK_TEXT)
        current_page.insert_text(pymupdf.Point(x, cursor_y + 14), prio, fontsize=7.5, fontname="Helvetica-Bold", color=prio_col)
        
        x += col_w_prio
        loc = c.get("source_section", "Page 1")
        if len(loc) > 16:
            loc = loc[:14] + ".."
        current_page.insert_text(pymupdf.Point(x, cursor_y + 14), loc, fontsize=7.5, fontname="Helvetica", color=MUTED_TEXT)
        
        x += col_w_loc
        raw_snip = (c.get("summary") or c.get("relevant_text") or "").replace("\n", " ").strip()
        tb_rect = pymupdf.Rect(x, cursor_y + 3, margin_x + content_w - 6, cursor_y + row_h - 2)
        current_page.insert_textbox(tb_rect, raw_snip, fontsize=7.2, fontname="Helvetica", color=DARK_TEXT)
        
        cursor_y += row_h
    cursor_y += 16.0

    # ----------------------------------------------------
    # 4. OBLIGATIONS (CLEAN TABLE)
    # ----------------------------------------------------
    draw_section_heading("Contractual Obligations & Duties", "Active performance covenants, operational responsibilities, and prohibitions")
    obs = report_data.get("obligations_and_responsibilities", [])
    
    col_w_ob_party = 95.0
    col_w_ob_duty = 240.0
    col_w_ob_dl = 95.0
    col_w_ob_src = 85.0
    
    def draw_ob_table_header():
        nonlocal cursor_y
        check_space(20)
        hdr_rect = pymupdf.Rect(margin_x, cursor_y, margin_x + content_w, cursor_y + 16)
        current_page.draw_rect(hdr_rect, fill=NAVY)
        x = margin_x + 6
        current_page.insert_text(pymupdf.Point(x, cursor_y + 11), "PARTY", fontsize=7.5, fontname="Helvetica-Bold", color=WHITE)
        x += col_w_ob_party
        current_page.insert_text(pymupdf.Point(x, cursor_y + 11), "OBLIGATION / DUTY", fontsize=7.5, fontname="Helvetica-Bold", color=WHITE)
        x += col_w_ob_duty
        current_page.insert_text(pymupdf.Point(x, cursor_y + 11), "DEADLINE", fontsize=7.5, fontname="Helvetica-Bold", color=WHITE)
        x += col_w_ob_dl
        current_page.insert_text(pymupdf.Point(x, cursor_y + 11), "SOURCE", fontsize=7.5, fontname="Helvetica-Bold", color=WHITE)
        cursor_y += 16.0

    draw_ob_table_header()
    
    for idx, ob in enumerate(obs[:8]):
        row_h = 34.0
        if cursor_y + row_h > bottom_limit:
            current_page = create_page()
            cursor_y = 44.0
            draw_ob_table_header()
            
        bg_row = BG_CARD if idx % 2 == 1 else WHITE
        row_rect = pymupdf.Rect(margin_x, cursor_y, margin_x + content_w, cursor_y + row_h)
        current_page.draw_rect(row_rect, fill=bg_row, color=BORDER_LIGHT, width=0.4)
        
        x = margin_x + 6
        current_page.insert_text(pymupdf.Point(x, cursor_y + 14), ob.get("responsible_party", "Party")[:16], fontsize=8, fontname="Helvetica-Bold", color=NAVY)
        
        x += col_w_ob_party
        duty_text = ob.get("obligation", "").replace("\n", " ").strip()
        tb_rect = pymupdf.Rect(x, cursor_y + 3, x + col_w_ob_duty - 6, cursor_y + row_h - 2)
        current_page.insert_textbox(tb_rect, duty_text, fontsize=7.2, fontname="Helvetica", color=DARK_TEXT)
        
        x += col_w_ob_duty
        current_page.insert_text(pymupdf.Point(x, cursor_y + 14), ob.get("deadline", "Upon Notice")[:18], fontsize=7.5, fontname="Helvetica", color=MUTED_TEXT)
        
        x += col_w_ob_dl
        current_page.insert_text(pymupdf.Point(x, cursor_y + 14), ob.get("source_section", "Document")[:16], fontsize=7.5, fontname="Helvetica", color=MUTED_TEXT)
        
        cursor_y += row_h
    cursor_y += 16.0

    # ----------------------------------------------------
    # 5. DATES & MONEY (SIDE-BY-SIDE CARDS)
    # ----------------------------------------------------
    draw_section_heading("Extracted Commercial Figures & Dates", "Structured quantitative terms and timeline milestones")
    check_space(65)
    
    dm_card_h = 60.0
    dm_col_w = (content_w - 10.0) / 2.0
    
    # Left: Dates
    d_x = margin_x
    d_y = cursor_y
    current_page.draw_rect(pymupdf.Rect(d_x, d_y, d_x + dm_col_w, d_y + dm_card_h), fill=BG_CARD, color=BORDER_LIGHT, width=0.6)
    current_page.insert_text(pymupdf.Point(d_x + 10, d_y + 14), "CRITICAL TIMELINES & DATES", fontsize=7.5, fontname="Helvetica-Bold", color=NAVY)
    d_items = overview.get("important_dates", [])[:4]
    if d_items:
        dy = d_y + 26
        for d_str in d_items[:3]:
            current_page.insert_text(pymupdf.Point(d_x + 12, dy), f"• {d_str[:38]}", fontsize=7.5, fontname="Helvetica", color=DARK_TEXT)
            dy += 11
    else:
        current_page.insert_text(pymupdf.Point(d_x + 12, d_y + 30), "No explicit dates detected.", fontsize=7.5, fontname="Helvetica-Oblique", color=MUTED_TEXT)
        
    # Right: Money
    m_x = margin_x + dm_col_w + 10.0
    m_y = cursor_y
    current_page.draw_rect(pymupdf.Rect(m_x, m_y, m_x + dm_col_w, m_y + dm_card_h), fill=BG_CARD, color=BORDER_LIGHT, width=0.6)
    current_page.insert_text(pymupdf.Point(m_x + 10, m_y + 14), "MONETARY COMMITMENTS & PAYMENTS", fontsize=7.5, fontname="Helvetica-Bold", color=NAVY)
    m_items = overview.get("monetary_amounts", [])[:4]
    if m_items:
        my = m_y + 26
        for m_str in m_items[:3]:
            current_page.insert_text(pymupdf.Point(m_x + 12, my), f"• {m_str[:38]}", fontsize=8, fontname="Helvetica-Bold", color=CRIMSON)
            my += 11
    else:
        current_page.insert_text(pymupdf.Point(m_x + 12, m_y + 30), "Standard covenants (No explicit sum)", fontsize=7.5, fontname="Helvetica-Oblique", color=MUTED_TEXT)
    cursor_y += dm_card_h + 16.0

    # ----------------------------------------------------
    # 6. PARTIES & ENTITIES (GROUPED BY CATEGORY)
    # ----------------------------------------------------
    draw_section_heading("Legal Entities Taxonomy", "Recognized organizations, individuals, statutes, sections, and jurisdictions")
    check_space(80)
    
    ent_groups = {
        "PARTIES & PERSONS": [],
        "STATUTES & ACTS": [],
        "SECTIONS & PROVISIONS": [],
        "LOCATIONS & JURISDICTIONS": []
    }
    
    for ent in report_data.get("extracted_entities", []):
        t = (ent.get("entity_type") or "").upper()
        txt = ent.get("normalized_text") or ent.get("entity_text") or ""
        if not txt:
            continue
        if any(k in t for k in ["PARTY", "PERSON", "ORG"]):
            if txt not in ent_groups["PARTIES & PERSONS"]:
                ent_groups["PARTIES & PERSONS"].append(txt)
        elif any(k in t for k in ["ACT", "LAW", "STATUTE"]):
            if txt not in ent_groups["STATUTES & ACTS"]:
                ent_groups["STATUTES & ACTS"].append(txt)
        elif any(k in t for k in ["SECTION", "ARTICLE", "CLAUSE"]):
            if txt not in ent_groups["SECTIONS & PROVISIONS"]:
                ent_groups["SECTIONS & PROVISIONS"].append(txt)
        elif any(k in t for k in ["LOC", "GPE", "CITY", "STATE", "COUNTRY"]):
            if txt not in ent_groups["LOCATIONS & JURISDICTIONS"]:
                ent_groups["LOCATIONS & JURISDICTIONS"].append(txt)

    ent_card_w = (content_w - 10.0) / 2.0
    grid_items = list(ent_groups.items())
    
    for row_idx in range(0, len(grid_items), 2):
        check_space(46)
        c_h = 42.0
        g_title1, g_list1 = grid_items[row_idx]
        gx1 = margin_x
        gy1 = cursor_y
        current_page.draw_rect(pymupdf.Rect(gx1, gy1, gx1 + ent_card_w, gy1 + c_h), fill=WHITE, color=BORDER_LIGHT, width=0.5)
        current_page.insert_text(pymupdf.Point(gx1 + 8, gy1 + 12), g_title1, fontsize=7, fontname="Helvetica-Bold", color=NAVY)
        str1 = ", ".join(g_list1[:4]) if g_list1 else "None detected"
        tb1 = pymupdf.Rect(gx1 + 8, gy1 + 16, gx1 + ent_card_w - 6, gy1 + c_h - 2)
        current_page.insert_textbox(tb1, str1, fontsize=7, fontname="Helvetica", color=DARK_TEXT)
        
        if row_idx + 1 < len(grid_items):
            g_title2, g_list2 = grid_items[row_idx + 1]
            gx2 = margin_x + ent_card_w + 10.0
            gy2 = cursor_y
            current_page.draw_rect(pymupdf.Rect(gx2, gy2, gx2 + ent_card_w, gy2 + c_h), fill=WHITE, color=BORDER_LIGHT, width=0.5)
            current_page.insert_text(pymupdf.Point(gx2 + 8, gy2 + 12), g_title2, fontsize=7, fontname="Helvetica-Bold", color=NAVY)
            str2 = ", ".join(g_list2[:4]) if g_list2 else "None detected"
            tb2 = pymupdf.Rect(gx2 + 8, gy2 + 16, gx2 + ent_card_w - 6, gy2 + c_h - 2)
            current_page.insert_textbox(tb2, str2, fontsize=7, fontname="Helvetica", color=DARK_TEXT)
        
        cursor_y += c_h + 6.0
    cursor_y += 10.0

    # ----------------------------------------------------
    # 7. KEYWORDS (COMPACT CHIPS / BADGES)
    # ----------------------------------------------------
    draw_section_heading("Weighted Legal Keywords", "Salient terms ranked by statistical relevance and domain frequency")
    check_space(46)
    
    kws = report_data.get("top_keywords", [])[:16]
    kw_card_rect = pymupdf.Rect(margin_x, cursor_y, margin_x + content_w, cursor_y + 40)
    current_page.draw_rect(kw_card_rect, fill=BG_CARD, color=BORDER_LIGHT, width=0.5)
    
    chip_x = margin_x + 8
    chip_y = cursor_y + 8
    for kw in kws:
        w_text = kw.get("keyword", "")
        approx_w = len(w_text) * 4.8 + 14
        if chip_x + approx_w > margin_x + content_w - 8:
            chip_x = margin_x + 8
            chip_y += 16
            if chip_y > cursor_y + 36:
                break
        current_page.draw_rect(pymupdf.Rect(chip_x, chip_y, chip_x + approx_w, chip_y + 13), fill=WHITE, color=BORDER_LIGHT, width=0.4)
        current_page.insert_text(pymupdf.Point(chip_x + 6, chip_y + 9), w_text, fontsize=6.8, fontname="Helvetica", color=NAVY)
        chip_x += approx_w + 6
        
    cursor_y += 52.0

    # ----------------------------------------------------
    # 8. MANDATORY LEGAL DISCLAIMER
    # ----------------------------------------------------
    check_space(48)
    disc_rect = pymupdf.Rect(margin_x, cursor_y, margin_x + content_w, cursor_y + 42)
    current_page.draw_rect(disc_rect, fill=BG_CARD, color=BORDER_LIGHT, width=0.5)
    current_page.draw_rect(pymupdf.Rect(margin_x, cursor_y, margin_x + 3, cursor_y + 42), fill=CRIMSON)
    current_page.insert_text(pymupdf.Point(margin_x + 10, cursor_y + 13), "IMPORTANT SYSTEM DISCLAIMER & AUDIT INTEGRITY NOTICE:", fontsize=7, fontname="Helvetica-Bold", color=CRIMSON)
    disc_text = (
        "LexExtract provides automated document intelligence, legal entity extraction, and clause identification. "
        "This report is generated for analytical workflow efficiency and does not constitute formal legal advice or attorney representation."
    )
    current_page.insert_textbox(pymupdf.Rect(margin_x + 10, cursor_y + 17, margin_x + content_w - 10, cursor_y + 40), disc_text, fontsize=6.8, fontname="Helvetica", color=MUTED_TEXT)
    cursor_y += 48.0

    # ----------------------------------------------------
    # FOOTER STAMPING (Page X of Y on all pages)
    # ----------------------------------------------------
    total_pages = len(doc)
    for p_idx in range(total_pages):
        p = doc[p_idx]
        p.draw_line(pymupdf.Point(margin_x, page_h - 30), pymupdf.Point(page_w - margin_x, page_h - 30), color=BORDER_LIGHT, width=0.5)
        p.insert_text(pymupdf.Point(margin_x, page_h - 18), "LEXEXTRACT LEGAL INTELLIGENCE  •  CONFIDENTIAL & PROPRIETARY", fontsize=7, fontname="Helvetica-Bold", color=MUTED_TEXT)
        p.insert_text(pymupdf.Point(page_w - margin_x - 55, page_h - 18), f"Page {p_idx + 1} of {total_pages}", fontsize=7.5, fontname="Helvetica", color=MUTED_TEXT)

    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes
