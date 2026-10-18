# LexExtract — Master Quality Assurance & Test Plan

**Project**: LexExtract — Legal Document Keyword & Entity Extractor  
**Phase**: Phase 12 — Project Quality, Testing, Traceability & Final ITPM Integration  
**Standard**: IEEE 829 Standard for Software and System Test Documentation  
**Disciplines**: Enterprise Systems (ES) + Advanced Statistical & Text Mining Analysis (ASTMA) + IT Project Management (ITPM)  

---

## 1. Testing Objectives

The primary objective of the LexExtract Test Plan is to provide empirical, reproducible verification of the system's functional, algorithmic, architectural, and security integrity. Specifically:
1. Verify end-to-end correctness of the legal document intake, normalization, keyword extraction, and entity recognition pipelines.
2. Validate user-value analytical features: Document At-a-Glance, 13 Important Clause Categories, Obligations & Duties, Structured Facts, In-Document Search, Document Comparison, and Multi-Format Report Export.
3. Enforce cryptographic authentication, role-based access control (USER, ANALYST, ADMIN), document ownership boundaries, and immutable audit logging.
4. Measure information retrieval quality (Precision, Recall, F1) across top-K cutoffs and conduct rigorous algorithm ablation on benchmark datasets.
5. Demonstrate graceful degradation and robust error handling across edge cases, corrupted inputs, and boundary conditions.

---

## 2. Testing Scope

### In-Scope
- **API & Backend Layer**: FastAPI routes, Pydantic schemas, dependency injection, exception handlers, PyMuPDF parsing, python-docx parsing.
- **NLP & Mining Layer (ASTMA)**: Tokenization, candidate generation (n-grams), stopword filtering, TF-IDF scoring, RAKE graph scoring, legal lexicon scoring, spaCy NER, regex/gazetteer matching, deduplication, cosine similarity, clause pattern matching, modal verb obligation parsing.
- **Enterprise Security (ES)**: RFC 7519 JWT generation/validation, Argon2id password hashing, ownership checks (`check_document_access`), audit ledger creation and query filtering.
- **Frontend Layer**: React 18 single-page application, responsive layout, tabbed navigation, term highlighting, side-by-side comparison UI, report export triggers.
- **Data Persistence**: SQLite database schema, SQLAlchemy ORM relationships, foreign key cascade constraints, session lifecycle.

### Out-of-Scope
- Cloud multi-region distributed clustering (LexExtract is designed as an on-premise/local enterprise server).
- OCR processing of raw scanned photographic bitmaps (LexExtract strictly ingests digitally generated PDF and DOCX streams).

---

## 3. Test Strategy & Levels

```
+-------------------------------------------------------------------+
|                     User Acceptance Testing (UAT)                 |
|               End-to-End Legal Workflow & Viva Defense            |
+-------------------------------------------------------------------+
                                  ^
+-------------------------------------------------------------------+
|                       System & UI Testing                         |
|         Browser Subagent Automated Interaction, Production Build  |
+-------------------------------------------------------------------+
                                  ^
+-------------------------------------------------------------------+
|               Integration & Security Testing (RBAC)               |
|    FastAPI TestClient, SQLite Memory DB, Cross-User Isolation     |
+-------------------------------------------------------------------+
                                  ^
+-------------------------------------------------------------------+
|                      Algorithmic NLP Evaluation                   |
|     12-Document Curated Benchmark, Precision, Recall, F1 Ablation |
+-------------------------------------------------------------------+
                                  ^
+-------------------------------------------------------------------+
|                        Unit Testing (PyTest)                      |
|       Scorers, Validators, Preprocessors, Regex Rules, Filters    |
+-------------------------------------------------------------------+
```

---

## 4. Test Categories

### 4.1 Unit Testing
- Focus: Individual functions and class methods isolated from external state.
- Modules: `candidate_generator.py`, `candidate_filter.py`, `tfidf_scorer.py`, `rake_scorer.py`, `legal_entity_rules.py`, `entity_normalizer.py`, `document_validator.py`.
- Framework: `pytest` with parameterized test cases.

### 4.2 Integration Testing
- Focus: Interactions between API route handlers, service orchestrators, and database transactions.
- Execution: `FastAPI.testclient.TestClient` using in-memory SQLite (`sqlite:///:memory:`) with session teardown and recreation per test.
- Coverage: Authentication routes, document upload and text retrieval, analysis orchestration, keyword/entity querying, audit log retrieval.

### 4.3 Security & Access Control Testing (RBAC)
- Multi-User Isolation: Generating tokens for `User A`, `User B`, and verifying that `User B` attempting to view, analyze, search, compare, or export `User A`'s documents strictly receives `HTTP 403 Forbidden`.
- Authentication Rejection: Unauthenticated requests to protected endpoints return `HTTP 401 Unauthorized`.
- Administrative Guards: Normal `USER` role attempting to access `/api/v1/users/` or `/api/v1/admin/audit-logs` strictly receives `HTTP 403 Forbidden`.
- Non-Repudiation: Every security-sensitive action generates an immutable record in `audit_logs`.

### 4.4 Algorithmic ASTMA Evaluation
- Benchmark Dataset: 12 representative legal contracts, deeds, and statutory notices with human-curated gold annotations.
- Metrics Evaluated:
  - Micro and Macro Precision, Recall, F1-score for keywords and entities.
  - Top-K cutoffs ($K=5, 10, 20$).
  - Algorithm ablation: Pure TF-IDF vs Pure RAKE vs Hybrid Weighted Fusion.
  - Real-time wall-clock latency measurement per document.

### 4.5 Negative & Edge Case Testing
- Empty files (0 bytes) and files with empty text streams.
- Extremely short text (single word or single sentence).
- Documents lacking standard legal clauses or recognized entities.
- Unsupported file formats (`.exe`, `.png`, `.txt`) and oversized files (>25MB).
- In-document search queries with zero matching passages.
- Document comparison with identical documents (verifying Cosine Similarity = 1.0) and completely unrelated documents.

### 4.6 UI & System Verification
- Vite production build verification: `npm run build` validating zero syntax, bundling, or CSS errors.
- Browser automation: Headless Chrome subagent simulating realistic end-to-end sessions (login $\rightarrow$ upload $\rightarrow$ inspect results $\rightarrow$ clauses $\rightarrow$ obligations $\rightarrow$ search $\rightarrow$ compare $\rightarrow$ export).

---

## 5. Test Environment & Automation Tools

| Component | Tool / Technology | Version | Purpose |
| :--- | :--- | :--- | :--- |
| Test Runner | `pytest` | 9.1+ | Test discovery, execution, assertion reporting |
| API Client | `starlette.testclient.TestClient` | In-process | HTTP request dispatch without external network overhead |
| Test Database | SQLite (`sqlite:///:memory:`) | 3.x | Isolated in-memory relational testing |
| Benchmark Engine | Python `evaluation_service.py` | Custom | Gold standard annotation evaluation & ablation |
| Frontend Builder | Vite / Rollup | 5.4+ | Production bundle compilation verification |
| Browser Agent | Playwright / Headless Chrome | 131+ | Live DOM validation, rendering check, visual recordings |

---

## 6. Pass / Fail Criteria & Exit Standards

A test cycle is deemed **PASSED** if and only if:
1. 100% of automated unit, integration, and security tests pass with zero errors.
2. All 14 Functional Requirements and 5 Non-Functional Requirements achieve verified status.
3. No cross-user data leakage occurs under any tested condition (zero HTTP 200 responses for unauthorized resources).
4. No uncaught Python exceptions or raw stack traces are returned to the client.
5. The frontend builds with zero compilation errors and executes without console errors.
