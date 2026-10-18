import re
from typing import Dict, List, Set, Tuple
from collections import defaultdict
from app.services.candidate_filter import STOPWORDS, LEGAL_PRESERVED_WORDS


def split_sentences_and_clauses(text: str) -> List[str]:
    """
    Step 1: Partition raw text into sentence segments using punctuation delimiters.
    Clause boundaries prevent phrases from spanning distinct grammatical statements.
    """
    if not text:
        return []
    # Split on sentence terminals, punctuation, and clause delimiters
    raw_clauses = re.split(r"[.\n,;!?\"()\[\]]+", text)
    return [c.strip() for c in raw_clauses if c.strip()]


def extract_candidate_word_sequences(clauses: List[str]) -> List[List[str]]:
    """
    Step 2: Split clauses around stopword delimiters into contiguous content word sequences.
    Preserves protected legal words as content words.
    """
    candidate_sequences: List[List[str]] = []

    for clause in clauses:
        words = re.findall(r"\b[A-Za-z0-9]+(?:[-_'][A-Za-z0-9]+)*\b", clause)
        current_seq: List[str] = []

        for w in words:
            w_lower = w.lower()
            if w_lower in STOPWORDS and w_lower not in LEGAL_PRESERVED_WORDS:
                if current_seq:
                    candidate_sequences.append(current_seq)
                    current_seq = []
            else:
                current_seq.append(w_lower)

        if current_seq:
            candidate_sequences.append(current_seq)

    return candidate_sequences


def build_word_cooccurrence_graph(candidate_sequences: List[List[str]]) -> Tuple[Dict[str, int], Dict[str, int]]:
    """
    Steps 3 & 4: Calculate word frequency and word degree from co-occurrence in phrases.
    - Word Frequency freq(w): Number of times word w appears.
    - Word Degree deg(w): Sum of lengths of all candidate phrases in which w appears
      (representing co-occurrence graph edge weights).
    """
    word_freq: Dict[str, int] = defaultdict(int)
    word_deg: Dict[str, int] = defaultdict(int)

    for seq in candidate_sequences:
        seq_len = len(seq)
        for w in seq:
            word_freq[w] += 1
            word_deg[w] += seq_len  # Phrase length reflects co-occurrence connectivity

    return word_freq, word_deg


def calculate_word_scores(word_freq: Dict[str, int], word_deg: Dict[str, int]) -> Dict[str, float]:
    """
    Step 5: Calculate word score as the degree-to-frequency ratio:
        score(w) = deg(w) / freq(w)

    Explanation:
    - Words occurring predominantly in longer multi-word compounds have deg(w) >> freq(w),
      yielding higher scores.
    - Isolated single words have deg(w) == freq(w), yielding a score of 1.0.
    """
    word_scores: Dict[str, float] = {}
    for w, freq in word_freq.items():
        deg = word_deg.get(w, freq)
        word_scores[w] = float(deg) / float(freq) if freq > 0 else 0.0

    return word_scores


def compute_phrase_rake_score(candidate: str, word_scores: Dict[str, float]) -> float:
    """
    Step 6: Calculate composite phrase score based on member word degree-to-frequency ratios.
    Uses mean word score scaled by a multi-word cohesion bonus:
        RAKE(P) = (mean(score(w) for w in P)) * (1.0 + 0.15 * (|P| - 1))
    This ensures single-word terms and multi-word phrases compete fairly in min-max normalization.
    """
    if not candidate:
        return 0.0

    words = re.findall(r"\b[A-Za-z0-9]+(?:[-_'][A-Za-z0-9]+)*\b", candidate.lower())
    if not words:
        return 0.0

    scores = [word_scores.get(w, 1.0) for w in words]
    mean_score = sum(scores) / len(scores)
    # Cohesion multiplier boosts cohesive multi-word phrases
    cohesion_bonus = 1.0 + (0.15 * (len(words) - 1))
    return mean_score * cohesion_bonus


def score_candidates_with_rake(candidates: List[str], text: str) -> Dict[str, float]:
    """
    Complete RAKE Pipeline:
    1. Identify candidate phrases from text
    2. Split phrases around stopwords
    3. Calculate word frequencies
    4. Calculate word degrees
    5. Compute degree/frequency ratios
    6. Compute phrase score for every provided candidate
    """
    if not text or not candidates:
        return {cand: 0.0 for cand in candidates}

    clauses = split_sentences_and_clauses(text)
    sequences = extract_candidate_word_sequences(clauses)
    word_freq, word_deg = build_word_cooccurrence_graph(sequences)
    word_scores = calculate_word_scores(word_freq, word_deg)

    results: Dict[str, float] = {}
    for cand in candidates:
        results[cand] = compute_phrase_rake_score(cand, word_scores)

    return results
