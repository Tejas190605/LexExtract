# Phase 4 Walkthrough — Legal Keyword Extraction Engine

**Project:** LexExtract — Legal Document Keyword Extractor  
**Phase:** Phase 4 — Legal Keyword Extraction Engine  
**Status:** Completed, Verified, and Tested  

---

## 1. Phase Objective

The objective of Phase 4 was to construct the **Core Legal Keyword Extraction Engine** for LexExtract:
- Ingest normalized legal document text produced by Phase 3.
- Extract, score, categorize, and rank the top legal keywords and keyphrases.
- Implement an explainable, multi-signal scoring pipeline combining statistical relevance (TF-IDF), phrase co-occurrence graph scoring (RAKE), and a domain-specific legal taxonomy.
- Persist analysis runs and extracted terms in the SQLite relational database (`AnalysisRun` and `ExtractedKeyword`).
- Expose RESTful endpoints for initiating analyses, querying ranked keywords with category filters, and fetching run summaries.
- Deliver an authoritative, institutional editorial frontend UI featuring real-time analysis initiation, keyword ranking tables, and expandable score breakdowns for college project demonstration and viva defense.

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
                       │    - Verbal noise rejection   │
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

## 3. Candidate Generation

Implemented in `backend/app/services/candidate_generator.py`:
- Extracts contiguous n-grams spanning $N \in [1, 3]$ (unigrams, bigrams, trigrams).
- **Clause/Sentence Boundary Partitioning:** Uses punctuation terminals (`.`, `\n`, `;`, `!`, `?`) to split text into distinct semantic segments prior to n-gram sliding window generation. This guarantees candidate phrases do not bridge invalid syntactic boundaries (e.g. "...breach of contract. The plaintiff..." does not produce "contract The plaintiff").
- **Statutory Token Protection:** Regex recognizes statutory citations (`Section 302`, `Article 14`, `Section 10(2)`, `Order 39`) as cohesive tokens so their numerical modifiers are never severed.

---

## 4. Candidate Filtering & Controlled Stopwords

Implemented in `backend/app/services/candidate_filter.py`:
- **Controlled Stopwords:** Drops closed-class grammatical words (*the, and, of, to, in, for, a, an, is, was, are, were, with, on, by, at, from*).
- **Protected Legal Vocabulary:** Preserves core legal terms (*party, court, claim, section, agreement, contract, law, act, order, rule, notice, state*) even when high frequency.
- **Verbal Noise Filtering:** Rejects multi-word candidates containing auxiliary or participle verbs (*is, are, was, were, shall, will, have, has, had, entered, arising, relating, pertaining, agrees*) preventing non-keyphrase clause fragments from surfacing.
- **Allowed Interior Prepositions:** Multi-word phrases are permitted to contain only approved connective prepositions: `{"of", "and", "in", "to", "for", "on", "by", "with", "de"}` (e.g. *breach of contract*, *balance of convenience*, *articles of association*, *plaintiff and defendant*).
- **Preserved Citations:** Statutory references (`is_statutory_citation`) bypass numeric suppression.

---

## 5. TF-IDF Engine

Implemented in `backend/app/services/tfidf_scorer.py`:
- **Formula:**
  $$\text{TF-IDF}(t, d, D) = \text{TF}(t, d) \times \text{IDF}(t, D)$$
  where $\text{TF}(t, d)$ is the candidate term frequency in target document $d$, and:
  $$\text{IDF}(t, D) = \ln\left(\frac{1 + |D|}{1 + \text{DF}(t, D)}\right) + 1$$
- **Cross-Corpus Reference Strategy:** A single document analyzed in isolation has uniform $\text{IDF} = 1.0$ across all terms, eliminating inverse document frequency discriminative power. LexExtract solves this by maintaining a synthetic reference corpus of 10 legal benchmark contracts (`backend/app/data/legal_reference_corpus.json`). The target document is appended to this background collection when fitting `scikit-learn`'s `TfidfVectorizer`.
- **Configuration:**
  - `ngram_range = (1, 3)`
  - `lowercase = True`
  - `smooth_idf = True`
  - `sublinear_tf = False`
  - `token_pattern = r"(?u)\b[A-Za-z0-9]+(?:[-/][A-Za-z0-9]+)*\b"`

---

## 6. RAKE-Style Co-Occurrence Scorer

Implemented in `backend/app/services/rake_scorer.py`:
- A transparent, explainable in-house implementation of Rapid Automatic Keyword Extraction without external package black-boxes:
  1. **Candidate Sequence Partitioning:** Segments text into contiguous content-word sequences demarcated by stopword delimiters.
  2. **Word Co-Occurrence Graph:**
     - Word Frequency $\text{freq}(w)$: total occurrences across candidate sequences.
     - Word Degree $\text{deg}(w)$: sum of lengths of all candidate sequences containing $w$.
  3. **Word Score:**
     $$\text{score}(w) = \frac{\text{deg}(w)}{\text{freq}(w)}$$
  4. **Balanced Phrase Score Formulation:**
     To prevent long multi-word phrases from completely overwhelming high-value legal unigrams during min-max normalization, phrase scores are computed as the mean word score scaled by a multi-word cohesion bonus:
     $$\text{RAKE}(P) = \left(\frac{1}{|P|} \sum_{w \in P} \text{score}(w)\right) \times (1.0 + 0.15 \cdot (|P| - 1))$$

---

## 7. Legal Domain Lexicon

Implemented in `backend/app/data/legal_terms.json` & `backend/app/services/legal_scorer.py`:
- Curated taxonomy of 200+ legal terms across 10 practice areas:
  - `contract`, `litigation`, `property`, `intellectual_property`, `criminal`, `procedure`, `corporate`, `employment`, `arbitration`, `general_legal`.
- **Scoring Rules:**
  - Exact multi-word taxonomy match: $\text{score} = 1.00$
  - Exact unigram taxonomy match: $\text{score} = 0.85$
  - Statutory citation match (*Section 302*, *Article 14*): $\text{score} = 0.90$ (category: `procedure`)
  - Subphrase / head noun match in multi-word candidate: $\text{score} = 0.60$
  - Non-dictionary term: $\text{score} = 0.00$ (category: `other`)

---

## 8. Score Normalization

Implemented in `backend/app/services/scoring.py`:
- Min-max scaling maps raw TF-IDF and RAKE scores to $[0.0, 1.0]$:
  $$\hat{s}_i = \frac{s_i - \min(S)}{\max(S) - \min(S)}$$
- **Zero-Division Safeguard:** If $\max(S) - \min(S) \le 10^{-9}$, all $\hat{s}_i = 1.0$ (if non-zero) or $0.0$ (if all zero), preventing runtime exceptions.

---

## 9. Final Weighted Scoring Formula

Implemented in `backend/app/services/scoring.py`:
$$\text{Final Score} = 0.40 \cdot \hat{s}_{\text{TF-IDF}} + 0.35 \cdot \hat{s}_{\text{RAKE}} + 0.25 \cdot \hat{s}_{\text{Lexicon}}$$

- **Configuration Constants:**
  - `WEIGHT_TFIDF = 0.40`
  - `WEIGHT_RAKE = 0.35`
  - `WEIGHT_LEXICON = 0.25`
- **Weighting Rationale:**
  - **TF-IDF (0.40):** Primary statistical discriminator penalizing boilerplate across documents.
  - **RAKE (0.35):** Phrase structure signal surfacing multi-word compounds based on local word degree.
  - **Legal Lexicon (0.25):** Rule-based domain knowledge boost ensuring statutory terms rank prominently.
- **Ranking Order:** Primary: `final_score DESC`; Secondary: `frequency DESC`.
- **Default Limit:** Top 20 keywords returned.

---

## 10. Database & Relational Persistence Flow

1. Client triggers `POST /api/v1/analyses/{document_id}`.
2. System retrieves `Document`, verifies `extracted_text` is non-empty.
3. System creates a **new** `AnalysisRun` record with status `processing` and `started_at = func.now()`. Re-analysis creates a distinct run, preserving historical runs.
4. Orchestrator `extract_keywords(document.extracted_text)` runs synchronously.
5. System inserts top 20 `ExtractedKeyword` records linked to `analysis_run_id`:
   - `keyword`, `category`, `frequency`, `tfidf_score`, `rake_score`, `lexicon_score`, `final_score`.
6. System updates `AnalysisRun`:
   - `status = "completed"`
   - `completed_at = func.now()`
   - `processing_time = round(duration, 3)`
   - `total_keywords = len(keywords)`
   - `total_entities = 0` (reserved for Phase 5)

---

## 11. REST API Endpoints

| Method | Endpoint | Description | Sample Status |
|---|---|---|---|
| `POST` | `/api/v1/analyses/{document_id}` | Initiates keyword extraction pipeline | `200 OK` (Summary returned) |
| `GET` | `/api/v1/analyses/{analysis_id}/keywords` | Retrieves ranked keywords with `limit` and `category` query filters | `200 OK` (Keyword array) |
| `GET` | `/api/v1/analyses/{analysis_id}` | Retrieves execution run metadata | `200 OK` (Run summary) |
| `GET` | `/api/v1/analyses/document/{document_id}` | Lists all historical analysis runs for a document | `200 OK` (Array of runs) |

---

## 12. Frontend Presentation Flow

1. **New Analysis Page (`NewAnalysisPage.jsx`):**
   - User uploads a `.pdf` or `.docx` file.
   - Upon upload completion, a distinct **"Analyze Document"** primary button appears.
   - User explicitly initiates analysis (preventing automatic/accidental execution during viva demos).
   - An active progress banner indicates pipeline execution:
     *"Generating 1-3 Grams ➔ Filtering Stopwords & Citations ➔ Computing TF-IDF (0.40) ➔ Building RAKE Co-occurrence Matrix (0.35) ➔ Matching Legal Lexicon (0.25) ➔ Fusing Weighted Ranks."*
   - Navigates automatically to **Analysis Results** on completion.
2. **Analysis Results Page (`AnalysisResultsPage.jsx`):**
   - **Document Analysis Banner:** Document Title, Status (`completed`), Processing Time (`0.361s`), Total Keywords (`20`).
   - **Top Legal Keywords Table:** Columns for Rank, Keyword, Category badge, Frequency, and Final Score.
   - **Score Breakdown Drawer:** Expanding any keyword row reveals individual TF-IDF, RAKE, and Lexicon sub-scores alongside the exact mathematical formula.
   - **Category Dropdown Filter:** Dynamically filters keywords by domain (`All`, `Contract`, `Litigation`, `Property`, `Criminal`, `Corporate`, `Employment`, `Intellectual Property`, `Procedure`, `Arbitration`, `Other`).
   - **Empty States:** Clear messaging when no analysis exists, no keywords are found, or an error occurs.
   - **Zero Mock Data:** Entire view is driven exclusively by real backend API responses.

---

## 13. Test Cases & Verification

12 new unit and integration tests implemented in `backend/tests/test_keyword_extraction.py`:
1. `test_candidate_generation_ngrams`: Verified unigrams, bigrams, and trigrams generated.
2. `test_candidate_filter_stopwords_and_noise`: Verified function words and numeric noise dropped.
3. `test_candidate_filter_legal_preservation`: Verified legal citations (*Section 302*, *Article 14*, *Section 10(2)*) and compounds preserved.
4. `test_rake_scoring_cooccurrence`: Verified word degree/frequency co-occurrence calculations.
5. `test_tfidf_scoring_with_reference_corpus`: Verified cross-corpus inverse document frequency scoring.
6. `test_legal_dictionary_matching_and_category`: Verified taxonomy matching and scoring tiers.
7. `test_score_normalization`: Verified min-max scaling and division-by-zero safeguards.
8. `test_token_aware_frequency`: Verified token-boundary precision ("contract" does not match "contractual").
9. `test_weighted_fusion_formula`: Verified mathematical combination $0.40 \cdot \text{TF-IDF} + 0.35 \cdot \text{RAKE} + 0.25 \cdot \text{Lexicon}$.
10. `test_deterministic_viva_legal_case`: Executed deterministic viva test text; verified top keywords include *breach of contract*, *agreement*, *plaintiff*, *defendant*, *arbitration*, *jurisdiction*, *dispute*.
11. `test_end_to_end_analysis_api_flow`: Verified full database round-trip via API client, including re-analysis history preservation.
12. `test_analysis_fails_gracefully_on_empty_document`: Verified empty documents return HTTP 400 with a clear error message.

### Test Results:
```
======================== 40 passed, 1 warning in 3.21s ========================
```
- 12/12 Phase 4 tests passed.
- 28/28 regression tests (Phases 1, 2, 3) passed.

---

## 14. Sample Output (Deterministic Viva Test Text)

**Input Text:**
> *"This agreement is entered into between the plaintiff and defendant. The parties agree that any dispute arising from breach of contract shall be subject to arbitration. The court shall have jurisdiction over proceedings relating to termination of this agreement."*

**Extracted & Ranked Keywords:**
| Rank | Keyword | Category | Frequency | TF-IDF (0.40) | RAKE (0.35) | Lexicon (0.25) | Final Score |
|---|---|---|:---:|:---:|:---:|:---:|:---:|
| 1 | plaintiff and defendant | litigation | 1 | 0.7620 | 1.0000 | 0.6000 | **0.8048** |
| 2 | breach of contract | contract | 1 | 0.1856 | 1.0000 | 1.0000 | **0.6742** |
| 3 | agreement | contract | 2 | 1.0000 | 0.0000 | 0.8500 | **0.6125** |
| 4 | plaintiff | litigation | 1 | 0.4248 | 0.0000 | 0.8500 | **0.3824** |
| 5 | defendant | litigation | 1 | 0.4248 | 0.0000 | 0.8500 | **0.3824** |
| 6 | arbitration | arbitration | 1 | 0.4248 | 0.0000 | 0.8500 | **0.3824** |
| 7 | parties | contract | 1 | 0.1856 | 0.0000 | 0.8500 | **0.2867** |
| 8 | dispute | litigation | 1 | 0.1856 | 0.0000 | 0.8500 | **0.2867** |
| 9 | contract | contract | 1 | 0.1856 | 0.0000 | 0.8500 | **0.2867** |
| 10 | jurisdiction | litigation | 1 | 0.1856 | 0.0000 | 0.8500 | **0.2867** |

---

## 15. Curriculum Mappings

### Advanced Social, Text and Media Analytics (ASTMA)
- **N-Gram Modeling:** Multi-word syntactic candidate extraction ($N \in [1, 3]$).
- **Graph-Based Keyphrase Extraction:** RAKE word-degree over word-frequency co-occurrence graph scoring.
- **Statistical Term Weighting:** TF-IDF calculation with multi-document cross-corpus reference support.
- **Domain Knowledge Injection:** Taxonomy matching and domain category assignment.
- **Rank Fusion:** Multi-signal weighted score normalization and combination.

### Enterprise Systems (ES)
- **Layered Architecture:** Clear separation between Presentation (`React`), Application (`FastAPI` + Services), and Data (`SQLAlchemy` + `SQLite`).
- **Synchronous Service Orchestration:** Synchronous, lightweight execution suitable for enterprise document evaluation without unnecessary queue broker overhead.
- **Relational Integrity:** Foreign key cascading from `Document` to `AnalysisRun` to `ExtractedKeyword`.
- **Audit Preservation:** Every analysis run creates an immutable record; re-analyses do not overwrite past execution history.

---

## 16. Limitations & Scope Control

- **No Entity Extraction:** spaCy Named Entity Recognition (NER) is intentionally deferred to **Phase 5**.
- **No Authentication / RBAC:** JWT authentication and role-based permissions are deferred to **Phase 6**.
- **No OCR:** Image-only scanned PDFs notify the user that text extraction cannot proceed without OCR.
- **No Keyword Highlighting:** Synchronized visual highlighting in the document viewer is deferred to **Phase 8**.

---

## 17. Phase 5 Boundary Confirmation

**Phase 5 (Legal Entity Extraction) has NOT been implemented.**  
All entity fields (`total_entities`) remain at default `0`. No spaCy NER, entity extractors, or entity tables have been populated. Awaiting explicit user instruction before proceeding to Phase 5.
