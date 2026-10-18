import json
import logging
import os
from typing import Dict, List, Optional
from sklearn.feature_extraction.text import TfidfVectorizer

logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
REFERENCE_CORPUS_PATH = os.path.join(DATA_DIR, "legal_reference_corpus.json")

_REFERENCE_CORPUS_CACHE: Optional[List[str]] = None


def load_legal_reference_corpus() -> List[str]:
    """
    Loads synthetic multi-document legal reference corpus.
    Design rationale:
      In a single-document context, raw IDF = ln(1/1) = 0 or a constant for all terms,
      providing ZERO cross-document discriminative power.
      Fitting on a small multi-document reference corpus allows common legal boilerplate
      (e.g., 'entered into between', 'shall', 'party') to receive appropriately high
      document frequency (DF), reducing their IDF weight relative to document-specific terms.
    """
    global _REFERENCE_CORPUS_CACHE
    if _REFERENCE_CORPUS_CACHE is not None:
        return _REFERENCE_CORPUS_CACHE

    corpus_texts: List[str] = []
    if os.path.exists(REFERENCE_CORPUS_PATH):
        try:
            with open(REFERENCE_CORPUS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    text = item.get("text", "").strip()
                    if text:
                        corpus_texts.append(text)
        except Exception as exc:
            logger.warning(f"Could not load legal reference corpus: {exc}")

    _REFERENCE_CORPUS_CACHE = corpus_texts
    return _REFERENCE_CORPUS_CACHE


def score_candidates_with_tfidf(
    candidates: List[str],
    document_text: str,
    additional_corpus: Optional[List[str]] = None
) -> Dict[str, float]:
    """
    Computes statistical TF-IDF score for each candidate phrase using scikit-learn's TfidfVectorizer.

    Mathematical Concept:
        TF-IDF(t, d, D) = TF(t, d) × IDF(t, D)
        where:
        - TF(t, d): Term frequency of candidate t in the analyzed document d.
        - IDF(t, D) = ln((1 + |D|) / (1 + DF(t, D))) + 1: Inverse document frequency across collection D.
          Terms appearing across all legal contracts receive lower IDF; distinctive terms receive higher IDF.

    Configuration:
        - ngram_range = (1, 3) : Unigrams, bigrams, and trigrams
        - lowercase = True : Case-insensitive statistical matching
        - smooth_idf = True : Adds 1 to document frequencies, preventing zero division
        - sublinear_tf = False : Direct linear term frequency scaling
        - token_pattern = r"(?u)\b[A-Za-z0-9]+(?:[-/][A-Za-z0-9]+)*\b" : Retains citations and compounds
    """
    if not document_text or not candidates:
        return {cand: 0.0 for cand in candidates}

    reference_corpus = list(load_legal_reference_corpus())
    if additional_corpus:
        reference_corpus.extend(additional_corpus)

    # Build corpus: reference background corpus + current target document as final document
    corpus = reference_corpus + [document_text]
    target_doc_idx = len(corpus) - 1

    try:
        vectorizer = TfidfVectorizer(
            ngram_range=(1, 3),
            lowercase=True,
            smooth_idf=True,
            sublinear_tf=False,
            token_pattern=r"(?u)\b[A-Za-z0-9]+(?:[-/][A-Za-z0-9]+)*\b"
        )
        tfidf_matrix = vectorizer.fit_transform(corpus)
        feature_names = vectorizer.get_feature_names_out()
        target_vector = tfidf_matrix[target_doc_idx].toarray()[0]

        feature_score_map: Dict[str, float] = {}
        for idx, feature in enumerate(feature_names):
            val = float(target_vector[idx])
            if val > 0:
                feature_score_map[feature] = val

    except Exception as exc:
        logger.error(f"TfidfVectorizer fitting failed: {exc}", exc_info=True)
        return {cand: 0.0 for cand in candidates}

    results: Dict[str, float] = {}
    for cand in candidates:
        cand_norm = cand.strip().lower()
        if cand_norm in feature_score_map:
            results[cand] = feature_score_map[cand_norm]
        else:
            # Fallback for candidates with internal punctuation or variations:
            # Average TF-IDF weights of constituent recognized tokens
            tokens = cand_norm.split()
            token_scores = [feature_score_map.get(t, 0.0) for t in tokens if t in feature_score_map]
            if token_scores:
                results[cand] = sum(token_scores) / len(token_scores)
            else:
                results[cand] = 0.0

    return results
