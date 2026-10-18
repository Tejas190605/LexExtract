import re
import unicodedata
from typing import List, Dict, Any


def normalize_legal_text(raw_text: str) -> str:
    """
    Cleans raw document text while strictly preserving legal terms, statutes,
    citations, monetary figures, and structural punctuation.
    """
    if not raw_text:
        return ""

    # 1. Unicode normalization (NFKC fixes font ligatures such as 'fi', 'fl', 'oe')
    text = unicodedata.normalize("NFKC", raw_text)

    # 2. Normalize Windows/Mac line endings to standard Unix newline
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # 3. Reconnect words hyphenated across line breaks (e.g. 'obli-\ngation' -> 'obligation')
    text = re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)

    # 4. Clean intra-line whitespace (tabs, non-breaking spaces, repeated spaces)
    lines = []
    for line in text.split("\n"):
        clean_line = re.sub(r"[ \t\u00A0]+", " ", line).strip()
        lines.append(clean_line)

    cleaned_text = "\n".join(lines)

    # 5. Collapse excessive consecutive blank lines (max 2 consecutive newlines)
    cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text).strip()

    return cleaned_text


def tokenize_legal_text(text: str) -> List[str]:
    """
    Explainable, rule-based legal tokenizer.
    Retains statutory citations (e.g., 'Section 10(2)', 'Article 14'),
    currencies (e.g., 'Rs. 50,000', '₹10,00,000'), dates, and legal references.
    """
    if not text:
        return []

    # Regex capturing legal tokens:
    # 1. Statutory clauses like 'Section 10(2)' or 'Sec. 138'
    # 2. Currency/amounts like 'Rs. 50,000' or '₹10,00,000'
    # 3. Standard dates 'DD/MM/YYYY'
    # 4. Alphanumeric words, hyphenated compounds, or acronyms
    token_pattern = re.compile(
        r"(?:(?:Section|Sec\.|Article|Art\.)\s+\d+(?:\([0-9a-zA-Z]+\))*)"  # Citations
        r"|(?:(?:Rs\.|INR|₹|\$|USD)\s*[\d,]+(?:\.\d+)?)"                   # Currencies
        r"|(?:\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b)"                         # Dates
        r"|(?:\b[A-Za-z0-9]+(?:[-_'][A-Za-z0-9]+)*\b)"                    # Words & compounds
        r"|(?:\S)",                                                        # Other characters
        flags=re.IGNORECASE
    )

    tokens = [m.group(0) for m in token_pattern.finditer(text)]
    return tokens


def calculate_word_count(text: str) -> int:
    """
    Calculates word count using whitespace splitting on alphanumeric-bearing tokens.
    """
    if not text:
        return 0
    words = re.findall(r"\b\w+(?:[-']\w+)*\b", text)
    return len(words)


def preprocess_document_text(raw_text: str, pages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Applies normalization to full document text and individual page segments.
    Returns:
        {
            "cleaned_text": str,
            "word_count": int,
            "cleaned_pages": List[Dict[str, Any]],
            "sample_tokens": List[str]
        }
    """
    cleaned_full_text = normalize_legal_text(raw_text)
    word_count = calculate_word_count(cleaned_full_text)

    cleaned_pages = []
    for page in pages:
        cleaned_pages.append({
            "page_number": page.get("page_number", 1),
            "text": normalize_legal_text(page.get("text", ""))
        })

    sample_tokens = tokenize_legal_text(cleaned_full_text)[:50]

    return {
        "cleaned_text": cleaned_full_text,
        "word_count": word_count,
        "cleaned_pages": cleaned_pages,
        "sample_tokens": sample_tokens
    }
