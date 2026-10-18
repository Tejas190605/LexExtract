# Implementation Plan — Phase 4: LexExtract Legal Keyword Extraction Engine

**Project Title:** LexExtract – Legal Document Keyword Extractor  
**Phase:** Phase 4 – Legal Keyword Extraction Engine  
**Status:** In Progress / Ready for Execution  

---

## 1. Executive Summary & Objective

The objective of Phase 4 is to implement the **Core Legal Keyword Extraction Engine** for LexExtract. The system ingests normalized legal document text produced by Phase 3 and produces ranked, categorised, and fully explainable legal keywords and keyphrases.

To ensure academic rigor for Enterprise Systems (ES) and Advanced Social, Text and Media Analytics (ASTMA) college project evaluation, the engine implements an **explainable multi-signal hybrid scoring pipeline**:
1. **Candidate Generation:** Extract unigrams, bigrams, and trigrams.
2. **Candidate Filtering:** Filter grammatical stopwords, noise, and punctuation while strictly preserving statutory citations, legal compounds, and numerical clauses (e.g., *Section 302*, *Article 14*, *breach of contract*).
3. **TF-IDF Scoring:** Statistical relevance scoring using `scikit-learn`'s `TfidfVectorizer` paired with a curated synthetic legal reference corpus to ensure meaningful document frequency discrimination.
4. **RAKE-Style Scoring:** Word co-occurrence graph scoring (word degree / word frequency ratio) to capture cohesive multi-word legal terminology.
5. **Legal Domain Dictionary Boost:** Rule-based taxonomic score boost using a curated legal lexicon (`backend/app/data/legal_terms.json`).
6. **Score Normalization & Rank Fusion:** Min-max normalization mapped into a weighted composite score ($0.40 \cdot \text{TF-IDF} + 0.35 \cdot \text{RAKE} + 0.25 \cdot \text{Lexicon}$).
7. **Relational Persistence:** Persist runs in `AnalysisRun` and extracted terms in `ExtractedKeyword`.
8. **REST API & Interactive UI:** Serve results via FastAPI endpoints and display them in a clean, non-AI-cliché legal editorial table with score breakdowns and category filtering.

### Strict Scope Control (Deferred to Later Phases)
- NO entity extraction, regex entities, or spaCy NER -> Phase 5.
- NO authentication, JWT, or RBAC -> Phase 6.
- NO audit logging service -> Phase 7.
- NO LLMs, embeddings, vector databases, RAG, or deep learning.
- NO OCR.
- NO keyword highlighting or evaluations dashboard -> Later phases.

---

## 2. Keyword Extraction Architecture

```
                       [ Normalized Legal Document Text ]
                                       │
                                       ▼
                       ┌───────────────────────────────┐
                       │ 1. Candidate Generation       │
                       │    (Unigrams, Bigrams, 3-grams)│
                       └───────────────┬───────────────┘
                                       │
                                       ▼
                       ┌───────────────────────────────┐
                       │ 2. Candidate Filtering        │
                       │    - Controlled stopwords     │
                       │    - Noise & punctuation      │
                       │    - Retain legal citations   │
                       └───────┬───────────────┬───────┘
                               │               │
            ┌──────────────────┼───────────────┼──────────────────┐
            │                  │               │                  │
            ▼                  ▼               ▼                  ▼
  ┌───────────────────┐ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
  │  3. TF-IDF Scorer │ │ 4. RAKE Scorer│ │ 5. Lexicon    │ │ 6. Frequency  │
  │     (sklearn +    │ │  (Co-occ. deg/│ │     Scorer    │ │     Counter   │
  │   reference corpus│ │   freq ratio) │ │ (Legal dict)  │ │ (Token-aware) │
  └─────────┬─────────┘ └───────┬───────┘ └───────┬───────┘ └───────┬───────┘
            │                   │                 │                 │
            └───────────────────┼─────────────────┘                 │
                                ▼                                   │
                       ┌───────────────────────────────┐            │
                       │ 7. Min-Max Score Normalization│            │
                       │    (Safeguarded against div 0)│            │
                       └───────────────┬───────────────┘            │
                                       │                            │
                                       ▼                            │
                       ┌───────────────────────────────┐            │
                       │ 8. Weighted Rank Fusion       │            │
                       │    0.40 TF-IDF + 0.35 RAKE     │            │
                       │    + 0.25 Lexicon             │            │
                       └───────────────┬───────────────┘            │
                                       │                            │
                                       ▼                            │
                       ┌───────────────────────────────┐            │
                       │ 9. Category Assignment &      │◄───────────┘
                       │    Top-K Sorting (DESC)       │
                       └───────────────┬───────────────┘
                                       │
                                       ▼
                       [ Top 20 Extracted Keywords ]
                                       │
                                       ▼
                       [ Database: ExtractedKeyword ]
```

---

## 3. Mathematical & Algorithmic Foundations

### 3.1 Candidate Generation & Filtering
- **N-gram Span:** $N \in [1, 3]$ (unigrams, bigrams, trigrams).
- **Candidate Filtering Rules:**
  - Token length $\ge 2$ characters (excluding meaningless single letters like 's', 'a', 'x').
  - Punctuation-only and noise tokens dropped.
  - Number-only candidates dropped, EXCEPT where qualified by a legal citation prefix (e.g. `Section 302`, `Article 14`, `Section 10(2)`, `Order 39`).
  - Leading/trailing stopwords stripped from multi-word candidates (e.g. "of the contract" -> "contract", "breach of the contract" -> "breach of contract").
  - Controlled Stopwords: English closed-class function words (*the, and, of, to, in, for, a, an, is, was, are, were, with, on, by, at, from*).
  - Explicit Non-Stopwords: Vital legal vocabulary (*party, court, claim, section, agreement, contract, law, act, order, rule, notice, state*) are explicitly protected.

### 3.2 TF-IDF Scoring (`tfidf_scorer.py`)
- **Formula:**
  $$\text{TF-IDF}(t, d, D) = \text{TF}(t, d) \times \text{IDF}(t, D)$$
  where $\text{TF}(t, d)$ is term frequency in document $d$, and $\text{IDF}(t, D) = \ln\left(\frac{1 + |D|}{1 + \text{DF}(t, D)}\right) + 1$.
- **Reference Corpus Design:** Single-document TF-IDF has $\text{IDF} = 1$ for all terms (zero cross-document discriminative power). We maintain `backend/app/data/legal_reference_corpus.json` containing 10 synthetic legal benchmark texts across various legal domains (contracts, leases, employment, litigation, IP, arbitration, criminal notices).
- The vectorizer is fitted on the reference corpus plus the target document, ensuring genuine IDF penalization for ubiquitously common terms.
- Implemented with `scikit-learn.feature_extraction.text.TfidfVectorizer`:
  - `ngram_range=(1, 3)`
  - `lowercase=True`
  - `smooth_idf=True`
  - `token_pattern=r"(?u)\b\w+(?:[-/]\w+)*\b"`

### 3.3 RAKE-Style Scoring (`rake_scorer.py`)
- Explainable, dependency-free implementation of Rapid Automatic Keyword Extraction:
  1. **Candidate Phrase Boundary Detection:** Segment text into candidate phrases partitioned by stopword delimiters and clause punctuation (`[,.;:\n]`).
  2. **Word Co-occurrence Graph:** For each word $w$ occurring in candidate phrases within a phrase window:
     - Word frequency $\text{freq}(w)$: total appearances of word $w$.
     - Word degree $\text{deg}(w)$: sum of lengths of all candidate phrases in which $w$ appears.
  3. **Word Score:**
     $$\text{score}(w) = \frac{\text{deg}(w)}{\text{freq}(w)}$$
     *(Words appearing predominantly in longer multi-word compounds receive higher degree-to-frequency ratios).*
  4. **Phrase Score:**
     $$\text{RAKE}(P) = \sum_{w \in P} \text{score}(w)$$

### 3.4 Legal Domain Lexicon Boost (`legal_scorer.py`)
- Controlled dictionary `backend/app/data/legal_terms.json` organized into 10 domains:
  - `contract`, `litigation`, `property`, `intellectual_property`, `criminal`, `procedure`, `corporate`, `employment`, `arbitration`, `general_legal`.
- Scoring rules:
  - Exact phrase/term match in legal taxonomy: `legal_score = 1.0`.
  - Multi-word candidate whose head noun matches a legal term: `legal_score = 0.8`.
  - Candidate containing a recognized statutory marker (`Section`, `Article`, `Order`, `Clause`): `legal_score = 0.9`.
  - Non-dictionary term: `legal_score = 0.0`.

### 3.5 Score Normalization & Final Weighted Ranking (`scoring.py`)
- Raw scores are mapped to $[0.0, 1.0]$ using min-max scaling:
  $$\hat{s}_i = \frac{s_i - \min(S)}{\max(S) - \min(S)}$$
  *Safeguard:* If $\max(S) == \min(S)$, all $\hat{s}_i = 1.0$ (or $0.0$ if all zero) to prevent division by zero.
- **Final Ranking Formula:**
  $$\text{Final Score} = 0.40 \cdot \hat{s}_{\text{TF-IDF}} + 0.35 \cdot \hat{s}_{\text{RAKE}} + 0.25 \cdot \hat{s}_{\text{Lexicon}}$$
- **Configuration Constants:** Defined centrally in `backend/app/core/config.py` or `scoring.py`:
  - `WEIGHT_TFIDF = 0.40`
  - `WEIGHT_RAKE = 0.35`
  - `WEIGHT_LEXICON = 0.25`
- Primary sorting: `final_score DESC`; secondary sorting: `frequency DESC`.
- Top-K: Default 20 keywords.

---

## 4. Database & Relational Persistence Flow

1. **Trigger:** `POST /api/v1/analyses/{document_id}` received.
2. **AnalysisRun Creation:**
   - Retrieve `Document` by ID, verify `extracted_text` is non-empty.
   - Insert new `AnalysisRun` record with `status = "processing"` and `started_at = func.now()`.
   - Each analysis invocation creates a **new** `AnalysisRun`, strictly preserving the document's analysis history.
3. **Execution:**
   - Invoke `keyword_extractor.extract_keywords(document.extracted_text)`.
   - Measure wall-clock duration `processing_time`.
4. **Keyword Storage:**
   - Bulk-insert top 20 `ExtractedKeyword` instances linked via `analysis_run_id`:
     - `keyword`: str
     - `category`: str
     - `frequency`: int
     - `tfidf_score`: round(float, 4)
     - `rake_score`: round(float, 4)
     - `lexicon_score`: round(float, 4)
     - `final_score`: round(float, 4)
5. **Finalize Run:**
   - Update `AnalysisRun`:
     - `status = "completed"`
     - `completed_at = func.now()`
     - `processing_time = round(duration, 3)`
     - `total_keywords = len(keywords)`
     - `total_entities = 0` (reserved for Phase 5)
   - Commit transaction. On exception, set `status = "failed"` and re-raise.

---

## 5. API Contracts & Endpoints

### 5.1 `POST /api/v1/analyses/{document_id}`
- **Purpose:** Initiates synchronous keyword extraction for the specified document.
- **Response:** `200 OK`
  ```json
  {
    "analysis_id": 1,
    "document_id": 1,
    "status": "completed",
    "total_keywords": 20,
    "processing_time": 0.142
  }
  ```

### 5.2 `GET /api/v1/analyses/{analysis_id}/keywords`
- **Query Parameters:** `limit: int = 20`, `category: Optional[str] = None`
- **Response:** `200 OK`
  ```json
  {
    "analysis_id": 1,
    "total": 20,
    "keywords": [
      {
        "keyword": "breach of contract",
        "category": "contract",
        "frequency": 4,
        "tfidf_score": 0.8124,
        "rake_score": 0.7412,
        "lexicon_score": 1.0,
        "final_score": 0.8359
      }
    ]
  }
  ```

### 5.3 `GET /api/v1/analyses/{analysis_id}`
- **Purpose:** Detailed status and summary metadata of the analysis run.
- **Response:** `200 OK`
  ```json
  {
    "analysis_id": 1,
    "document_id": 1,
    "status": "completed",
    "started_at": "2026-10-04T18:30:00Z",
    "completed_at": "2026-10-04T18:30:01Z",
    "processing_time": 0.142,
    "total_keywords": 20,
    "total_entities": 0
  }
  ```

---

## 6. Frontend Presentation Flow

1. **New Analysis Page (`NewAnalysisPage.jsx`):**
   - User uploads document (PDF/DOCX).
   - Upon upload success, a distinct **"Analyze Document"** primary button appears alongside "View Extracted Text".
   - Clicking "Analyze Document" shows an active processing indicator ("Extracting & Scoring Keywords...") while calling `POST /api/v1/analyses/{doc_id}`.
   - Upon completion, automatically navigates to `AnalysisResultsPage` with `activeAnalysisId`.
2. **Analysis Results Page (`AnalysisResultsPage.jsx`):**
   - Renders Document Analysis Header: Document Name, Status badge ("Completed"), Processing Time ("0.14s"), Total Keywords ("20").
   - Category Filter Bar: Interactive tabs/dropdown `[All, Contract, Litigation, Property, Criminal, Corporate, Employment, Intellectual Property, Procedure, Other]`.
   - Results Table:
     - Rank (`#1`, `#2`, ...)
     - Keyword / Keyphrase (bold institutional serif/sans typography)
     - Category tag (subtle parchment badge with domain tone)
     - Frequency count
     - Final Score (with progress-bar indicator)
     - Expandable Score Breakdown: TF-IDF score, RAKE score, Lexicon score, Final weighted score.
   - Empty/Error States: Clear, graceful messages for "No analysis in session", "No keywords found", or "Analysis failed".
   - Completely removes any placeholder/mock data.

---

## 7. Testing Strategy

### 7.1 Unit Tests (`backend/tests/test_keyword_extraction.py`)
- `test_candidate_generator`: Verify 1-grams, 2-grams, 3-grams generated from sample phrases.
- `test_candidate_filter_stopwords`: Ensure function words ("the", "and", "of") are discarded.
- `test_candidate_filter_legal_preservation`: Ensure legal terms and citations ("Section 302", "Article 14", "breach of contract") survive filtering.
- `test_rake_scorer`: Verify co-occurrence graph scoring and degree-to-frequency calculation on deterministically constructed phrases.
- `test_tfidf_scorer`: Verify non-zero TF-IDF scores with reference corpus integration.
- `test_legal_scorer`: Verify lexicon lookup and domain categorization from `legal_terms.json`.
- `test_score_normalization`: Verify min-max normalization, edge-case identical scores, zero division avoidance.
- `test_weighted_scoring`: Verify mathematical combination with exact weights $0.40, 0.35, 0.25$.
- `test_token_aware_frequency`: Ensure "contract" frequency doesn't falsely increment on "contractual".

### 7.2 Integration Tests
- Ingest deterministic test passage:
  *"This agreement is entered into between the plaintiff and defendant. The parties agree that any dispute arising from breach of contract shall be subject to arbitration. The court shall have jurisdiction over proceedings relating to termination of this agreement."*
- Trigger `POST /api/v1/analyses/{doc_id}`.
- Verify `AnalysisRun` status is `completed`, `total_keywords >= 5`, keywords include *agreement*, *plaintiff*, *defendant*, *breach of contract*, *arbitration*, *jurisdiction*, *termination*.
- Verify `GET /api/v1/analyses/{analysis_id}/keywords` returns descending order of `final_score`.
- Test category filter query param `?category=contract`.
- Verify re-analysis produces a new `AnalysisRun` ID and preserves history.

---

## 8. Acceptance Criteria Checklist

- [ ] `scikit-learn` installed in virtual environment and added to `requirements.txt`.
- [ ] `backend/app/data/legal_terms.json` (150–300 terms categorized) created.
- [ ] `backend/app/data/legal_reference_corpus.json` (10 synthetic legal texts) created.
- [ ] Candidate generator produces 1-3 grams.
- [ ] Candidate filter drops stopwords while preserving legal citations & compounds.
- [ ] Lightweight RAKE scorer implemented with clear degree/frequency comments.
- [ ] TF-IDF scorer utilizes `TfidfVectorizer` against reference corpus + document.
- [ ] Legal scorer provides rule-based boost from taxonomy.
- [ ] Score normalization handles division by zero safely.
- [ ] Final weighted rank fusion implemented: $0.40 \cdot \text{TF-IDF} + 0.35 \cdot \text{RAKE} + 0.25 \cdot \text{Lexicon}$.
- [ ] Frequency computed with token-aware matching.
- [ ] AnalysisRun record created with status lifecycle: `processing` -> `completed` / `failed`.
- [ ] Top 20 keywords persisted in `ExtractedKeyword` database table.
- [ ] REST API endpoints implemented:
  - `POST /api/v1/analyses/{document_id}`
  - `GET /api/v1/analyses/{analysis_id}/keywords`
  - `GET /api/v1/analyses/{analysis_id}`
- [ ] Frontend `NewAnalysisPage` includes explicit "Analyze Document" trigger.
- [ ] Frontend `AnalysisResultsPage` displays real keyword rankings, score breakdowns, and category filtering.
- [ ] Zero mock data remaining in analysis view.
- [ ] All unit and integration tests pass cleanly (`pytest`).
- [ ] Frontend builds without errors (`npm run build`).
- [ ] Browser verification passes using real document flow.
- [ ] Regression test verifies Phase 1, Phase 2, and Phase 3 remain unbroken.
- [ ] `README.md` and `docs/PHASE4_WALKTHROUGH.md` updated.
- [ ] Phase 5 (NER/Entities) remains strictly untouched.
