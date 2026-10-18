import re
from typing import List, Set, Optional

# Controlled Stopwords: standard grammatical function words (closed-class words)
STOPWORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
    "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both",
    "but", "by", "can", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't",
    "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't",
    "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll",
    "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's",
    "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once",
    "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same",
    "shall", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some",
    "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then",
    "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this",
    "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd",
    "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", "where",
    "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself",
    "yourselves", "herein", "therein", "wherein", "hereto", "thereto", "thereof"
}

# Protected Legal Words: Never treat these as stopwords, even if high frequency
LEGAL_PRESERVED_WORDS: Set[str] = {
    "party", "court", "claim", "section", "agreement", "contract", "law", "act",
    "order", "rule", "clause", "suit", "appeal", "decree", "right", "duty", "state"
}

# Verbs and clause linkers that should not form legal keyphrases
VERBAL_STOPWORDS: Set[str] = {
    "is", "are", "was", "were", "be", "been", "being", "shall", "will", "have", "has",
    "had", "do", "does", "did", "may", "might", "must", "can", "could", "would", "should",
    "arise", "arising", "relate", "relating", "enter", "entered", "having", "pertaining",
    "subject", "agree", "agrees", "said", "says", "made"
}

STOPWORDS = STOPWORDS | VERBAL_STOPWORDS
# Remove protected words from stopwords if any overlap exists
STOPWORDS = STOPWORDS - LEGAL_PRESERVED_WORDS

# Allowed connective prepositions/conjunctions inside legitimate multi-word phrases
ALLOWED_INTERIOR_STOPWORDS: Set[str] = {
    "of", "and", "in", "to", "for", "on", "by", "with", "de"
}

# Pattern matching recognized statutory citations (e.g., Section 302, Article 14, Sec. 10(2), Order 39)
STATUTORY_PATTERN = re.compile(
    r"^(?:Section|Sec\.|Article|Art\.|Order|Clause)\s+\d+(?:\([0-9a-zA-Z]+\))*$",
    flags=re.IGNORECASE
)


def is_statutory_citation(candidate: str) -> bool:
    """
    Checks if a candidate is a legal statutory reference (e.g., 'Section 302', 'Article 14').
    """
    return bool(STATUTORY_PATTERN.match(candidate.strip()))


def clean_candidate(candidate: str) -> Optional[str]:
    """
    Cleans candidate:
    - Strips whitespace & extraneous punctuation
    - Strips leading and trailing stopwords (e.g. 'of contract' -> 'contract')
    - Preserves legal statutory citations
    - Rejects multi-word candidates with verbal or unapproved interior stopwords
    - Returns None if the cleaned term is invalid or noise
    """
    if not candidate:
        return None

    cand = candidate.strip()
    # If it is a statutory citation, preserve its format directly
    if is_statutory_citation(cand):
        return cand

    tokens = cand.split()
    if not tokens:
        return None

    # Strip leading stopwords
    while tokens and tokens[0].lower() in STOPWORDS and tokens[0].lower() not in LEGAL_PRESERVED_WORDS:
        tokens.pop(0)

    # Strip trailing stopwords
    while tokens and tokens[-1].lower() in STOPWORDS and tokens[-1].lower() not in LEGAL_PRESERVED_WORDS:
        tokens.pop()

    if not tokens:
        return None

    # Check unigram validity
    if len(tokens) == 1:
        tok_lower = tokens[0].lower()
        if tok_lower in STOPWORDS or tok_lower in VERBAL_STOPWORDS:
            return None
        if len(tok_lower) <= 1:
            return None
        if re.fullmatch(r"[\d,\.\-]+", tok_lower):
            return None

    # Multi-word phrase validation
    if len(tokens) > 1:
        for t in tokens:
            t_lower = t.lower()
            if t_lower in VERBAL_STOPWORDS:
                return None
            if t_lower in STOPWORDS and t_lower not in ALLOWED_INTERIOR_STOPWORDS and t_lower not in LEGAL_PRESERVED_WORDS:
                return None

    cleaned = " ".join(tokens).strip()

    # Discard single character candidates
    if len(cleaned) <= 1:
        return None

    # Discard pure numeric tokens (e.g., '2024', '15') that are not citations
    if re.fullmatch(r"[\d,\.\-]+", cleaned):
        return None

    # Discard punctuation-only strings
    if not re.search(r"[a-zA-Z0-9]", cleaned):
        return None

    return cleaned


def filter_candidates(candidates: List[str]) -> List[str]:
    """
    Filters a raw list of candidate n-grams.
    Deduplicates candidates preserving canonical case and order of first appearance.
    """
    seen: Set[str] = set()
    filtered: List[str] = []

    for raw in candidates:
        cleaned = clean_candidate(raw)
        if not cleaned:
            continue

        normalized_key = cleaned.lower()
        if normalized_key in seen:
            continue

        seen.add(normalized_key)
        filtered.append(cleaned)

    return filtered
