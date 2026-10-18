import re
from typing import Dict, List, Tuple

# Configuration Constants for Multi-Signal Fusion
WEIGHT_TFIDF: float = 0.40
WEIGHT_RAKE: float = 0.35
WEIGHT_LEXICON: float = 0.25


def normalize_scores(raw_scores: Dict[str, float]) -> Dict[str, float]:
    """
    Min-max normalization mapping raw values into [0.0, 1.0].
    Safeguarded against zero division when all scores are equal or all zero:
    - If max_val == min_val and max_val > 0, returns 1.0 for all entries.
    - If max_val == min_val == 0.0, returns 0.0 for all entries.
    """
    if not raw_scores:
        return {}

    values = list(raw_scores.values())
    min_val = min(values)
    max_val = max(values)

    val_range = max_val - min_val
    if val_range <= 1e-9:
        default_val = 1.0 if max_val > 0 else 0.0
        return {k: default_val for k in raw_scores}

    normalized: Dict[str, float] = {}
    for k, v in raw_scores.items():
        scaled = (v - min_val) / val_range
        normalized[k] = max(0.0, min(1.0, scaled))

    return normalized


def calculate_token_aware_frequency(candidate: str, document_text: str) -> int:
    """
    Counts whole-word occurrences of candidate in document_text.
    Guarantees that 'contract' does not falsely match within 'contractual'.
    Safely handles statutory citations containing brackets like 'Section 10(2)'.
    """
    if not candidate or not document_text:
        return 0

    # Boundary pattern: word boundary or start/end of string/punctuation
    escaped = re.escape(candidate.strip())
    pattern = rf"(?:(?<=\W)|(?<=^)){escaped}(?:(?=\W)|(?=$))"
    matches = re.findall(pattern, document_text, flags=re.IGNORECASE)
    return len(matches)


def compute_final_scores(
    normalized_tfidf: Dict[str, float],
    normalized_rake: Dict[str, float],
    lexicon_scores: Dict[str, Tuple[float, str]],
    document_text: str
) -> List[Dict[str, any]]:
    """
    Combines normalized scoring signals into a final rank-fused score:
        Final Score = (0.40 * TF-IDF) + (0.35 * RAKE) + (0.25 * Lexicon)

    Weighting Rationale (ASTMA + ES Curriculum):
    - TF-IDF (0.40): Primary statistical signal penalizing ubiquitous legal boilerplate across corpus.
    - RAKE (0.35): Structural co-occurrence signal promoting cohesive multi-word legal keyphrases.
    - Lexicon (0.25): Domain knowledge injection ensuring recognized statutory terms are surfaced.
    """
    candidates = list(normalized_tfidf.keys())
    results: List[Dict[str, any]] = []

    for cand in candidates:
        tf_score = normalized_tfidf.get(cand, 0.0)
        rk_score = normalized_rake.get(cand, 0.0)
        lex_score, category = lexicon_scores.get(cand, (0.0, "other"))

        final = (WEIGHT_TFIDF * tf_score) + (WEIGHT_RAKE * rk_score) + (WEIGHT_LEXICON * lex_score)
        freq = calculate_token_aware_frequency(cand, document_text)
        # Ensure at least frequency of 1 if the candidate was generated from document
        if freq == 0:
            freq = 1

        results.append({
            "keyword": cand,
            "category": category,
            "frequency": freq,
            "tfidf_score": round(tf_score, 4),
            "rake_score": round(rk_score, 4),
            "lexicon_score": round(lex_score, 4),
            "final_score": round(final, 4)
        })

    # Sort primarily by final_score DESC, secondarily by frequency DESC
    results.sort(key=lambda x: (x["final_score"], x["frequency"]), reverse=True)
    return results
