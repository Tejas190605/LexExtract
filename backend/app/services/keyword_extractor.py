import logging
from typing import List, Dict, Any, Optional
from app.services.candidate_generator import generate_ngram_candidates
from app.services.candidate_filter import filter_candidates
from app.services.tfidf_scorer import score_candidates_with_tfidf
from app.services.rake_scorer import score_candidates_with_rake
from app.services.legal_scorer import score_candidates_with_lexicon
from app.services.scoring import normalize_scores, compute_final_scores

logger = logging.getLogger(__name__)

DEFAULT_KEYWORD_LIMIT = 20


def extract_keywords(
    document_text: str,
    top_k: int = DEFAULT_KEYWORD_LIMIT,
    additional_corpus: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Main Orchestration Service for Legal Keyword Extraction:
    1. Candidate Generation: Unigrams, bigrams, and trigrams (1 <= n <= 3)
    2. Candidate Filtering: Stopword elimination, noise rejection, legal citation preservation
    3. Multi-Signal Scoring:
       - Statistical relevance (TF-IDF with reference corpus)
       - Structural co-occurrence degree (RAKE)
       - Domain knowledge injection (Legal taxonomy lookup)
    4. Normalization: Min-max scaling onto [0.0, 1.0] with zero-division safeguard
    5. Weighted Rank Fusion: 0.40 * TF-IDF + 0.35 * RAKE + 0.25 * Lexicon
    6. Category Assignment & Top-K Truncation
    """
    if not document_text or not document_text.strip():
        return []

    # Step 1: Candidate Generation
    raw_candidates = generate_ngram_candidates(document_text, min_n=1, max_n=3)
    if not raw_candidates:
        return []

    # Step 2: Candidate Filtering
    filtered_candidates = filter_candidates(raw_candidates)
    if not filtered_candidates:
        return []

    logger.info(
        f"Generated {len(raw_candidates)} raw n-grams, filtered to {len(filtered_candidates)} candidates."
    )

    # Step 3: Multi-Signal Scoring
    raw_tfidf = score_candidates_with_tfidf(filtered_candidates, document_text, additional_corpus)
    raw_rake = score_candidates_with_rake(filtered_candidates, document_text)
    lexicon_scores = score_candidates_with_lexicon(filtered_candidates)

    # Step 4: Normalization
    norm_tfidf = normalize_scores(raw_tfidf)
    norm_rake = normalize_scores(raw_rake)

    # Step 5: Weighted Combination & Ranking
    ranked_keywords = compute_final_scores(norm_tfidf, norm_rake, lexicon_scores, document_text)

    # Step 6: Return Top-K
    return ranked_keywords[:top_k]
