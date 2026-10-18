# LexExtract — ASTMA Academic Syllabus Mapping

**Subject:** Advanced Social, Text and Media Analytics (ASTMA)  
**Curriculum Domain:** Text Mining, Natural Language Processing & Information Retrieval  
**Implementation System:** LexExtract Legal Document Analysis Engine

---

## 1. Executive Curriculum Alignment

This document details the direct, verifiable mapping between the academic syllabus of **ASTMA** and the software modules implemented in LexExtract. Every concept listed corresponds to concrete Python algorithms and API endpoints within the workspace.

---

## 2. Topic-by-Topic Syllabus Mapping

### 2.1 Text Preprocessing & Tokenization
- **Syllabus Concept:** Text cleaning, tokenization, stopword removal, case-folding, and noise reduction.
- **Implemented in LexExtract:**
  - `backend/app/services/document_processing_service.py`
  - `backend/app/services/evaluation_service.py:normalize_term()`
- **Academic Implementation Details:**
  Standard tokenizers strip punctuation destructively. LexExtract implements a **citation-preserving normalizer** that cleans non-standard whitespace while explicitly maintaining internal parentheses for statutory citations (e.g., `Section 11(6)` and `Article 226(1)`). An extended stopword filter preserves legally discriminative connective particles (`whereas`, `hereinafter`, `pursuant to`).

---

### 2.2 Candidate Generation & N-Gram Modeling
- **Syllabus Concept:** N-gram language modeling, sliding windows, and phrase boundary detection.
- **Implemented in LexExtract:**
  - `backend/app/services/keyword_extractor.py:generate_candidates()`
- **Academic Implementation Details:**
  Extracts unigram ($n=1$), bigram ($n=2$), and trigram ($n=3$) candidates bounded by punctuation marks (commas, semicolons, clause boundaries). This ensures multi-word legal nominal compounds (e.g., `liquidated damages`, `master services agreement`) are captured as unified concepts rather than isolated tokens.

---

### 2.3 Statistical Information Retrieval (TF-IDF Weighting)
- **Syllabus Concept:** Vector Space Model, Term Frequency, Inverse Document Frequency, and document scoring.
- **Implemented in LexExtract:**
  - `backend/app/services/keyword_extractor.py:score_tfidf()`
- **Academic Implementation Details:**
  Calculates local term frequency $\text{TF}(t, d)$ and weights it against an inverse document frequency vector derived from a reference legal corpus:
  $$\text{TF-IDF}(w) = \text{TF}(w) \cdot \ln\left(\frac{N + 1}{\text{DF}(w) + 1}\right) + 1$$
  Contributes 35% to the final hybrid keyword score, prioritizing words that are distinct to the specific brief.

---

### 2.4 Graph-Based Text Mining (RAKE Co-occurrence Graphs)
- **Syllabus Concept:** Graph-based keyword extraction, word co-occurrence matrices, and degree-to-frequency ratios.
- **Implemented in LexExtract:**
  - `backend/app/services/keyword_extractor.py:score_rake()`
- **Academic Implementation Details:**
  Constructs a word co-occurrence graph across syntactic clause delimiters. Computes word degree $\text{deg}(w)$ and word frequency $\text{freq}(w)$, scoring candidates using the degree-to-frequency ratio:
  $$\text{Score}_{\text{RAKE}}(w) = \sum_{t \in w} \frac{\text{deg}(t)}{\text{freq}(t)}$$
  Contributes 35% to the final keyword score, capturing cohesive multi-word phrases without external training data.

---

### 2.5 Named Entity Recognition (NER)
- **Syllabus Concept:** Sequence tagging, transition-based statistical models, and rule-based entity extractors.
- **Implemented in LexExtract:**
  - `backend/app/services/entity_extractor.py`
  - `backend/app/data/legal_dictionary.py`
- **Academic Implementation Details:**
  Combines statistical linguistic parsing (`spaCy` `en_core_web_sm`) with symbolic regular expressions and legal gazetteers across 13 legal categories. Solves the legal domain gap where statistical models misclassify judicial bodies (e.g., `Supreme Court of India`) as commercial organizations. Uses longest-match span arbitration to resolve overlapping entity boundaries.

---

### 2.6 Quantitative Information Retrieval Evaluation Metrics
- **Syllabus Concept:** Precision, Recall, F1-score, Macro-averaging, Micro-averaging, and zero-division handling.
- **Implemented in LexExtract:**
  - `backend/app/services/evaluation_service.py:calculate_metrics()`
- **Academic Implementation Details:**
  Evaluates extractions against a curated 12-document legal ground truth (129 gold keywords, 157 gold entities). Computes contingency matrices:
  $$\text{Precision} = \frac{TP}{TP + FP}, \quad \text{Recall} = \frac{TP}{TP + FN}, \quad F_1 = \frac{2PR}{P + R}$$
  Enforces zero-division safeguards returning `0.0` when denominators equal zero, preventing IEEE 754 `NaN` values. Macro and micro averages are calculated across the corpus.

---

### 2.7 Ranked Retrieval Dynamics (Top-K Cutoffs)
- **Syllabus Concept:** Ranked retrieval evaluation, Precision@K, Recall@K, and cutoff trade-off analysis.
- **Implemented in LexExtract:**
  - `backend/app/services/evaluation_service.py:execute_full_benchmark()`
- **Academic Implementation Details:**
  Evaluates keyword candidate retrieval at cutoffs $K \in \{5, 10, 20\}$. Validates ranked retrieval dynamics:
  - **Top-5:** Precision = **0.217** (highest precision; ranks top legal concepts first).
  - **Top-20:** Recall = **0.224** (captures niche terms further down the ranked list).

---

### 2.8 Algorithm Ablation Studies & Failure Mode Analysis
- **Syllabus Concept:** Algorithmic ablation, feature contribution analysis, and error classification.
- **Implemented in LexExtract:**
  - `backend/app/services/evaluation_service.py:run_keyword_ablation_evaluation()`
  - `frontend/src/pages/EvaluationPage.jsx`
- **Academic Implementation Details:**
  Compares isolated sub-models (TF-IDF Alone vs. RAKE Alone vs. LexExtract Hybrid). Proves the hybrid model balances phrase extraction with domain constraints. Classifies extraction errors into False Positives (over-generation), False Negatives (omissions), and Entity Category Mismatches (correct span, wrong class).
