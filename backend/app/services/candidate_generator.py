import re
from typing import List, Set


def split_into_clauses_or_sentences(text: str) -> List[str]:
    """
    Splits text into clauses or sentence fragments based on punctuation
    so n-grams do not span across sentence or clause boundaries.
    """
    if not text:
        return []
    # Split on sentence terminals and major clause delimiters
    segments = re.split(r"[.\n;!?]+", text)
    return [seg.strip() for seg in segments if seg.strip()]


def generate_ngram_candidates(text: str, min_n: int = 1, max_n: int = 3) -> List[str]:
    """
    Generates unigram, bigram, and trigram candidate keyphrases from the input text.
    Respects clause and sentence boundaries to avoid invalid cross-clause phrases.
    Preserves statutory notation such as 'Section 302' or 'Article 14'.
    """
    if not text:
        return []

    clauses = split_into_clauses_or_sentences(text)
    candidates: List[str] = []

    # Tokenizer that keeps alphanumeric tokens, hyphens, and statutory citation markers
    token_pattern = re.compile(
        r"(?:(?:Section|Sec\.|Article|Art\.|Order|Clause)\s+\d+(?:\([0-9a-zA-Z]+\))*)"
        r"|(?:\b[A-Za-z0-9]+(?:[-_'][A-Za-z0-9]+)*\b)",
        flags=re.IGNORECASE
    )

    for clause in clauses:
        tokens = token_pattern.findall(clause)
        if not tokens:
            continue

        n_tokens = len(tokens)
        for n in range(min_n, max_n + 1):
            for i in range(n_tokens - n + 1):
                ngram_tokens = tokens[i:i + n]
                candidate = " ".join(ngram_tokens).strip()
                if candidate:
                    candidates.append(candidate)

    return candidates
