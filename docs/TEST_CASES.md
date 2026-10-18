# LexExtract — Comprehensive Test Case Specifications

**Project**: LexExtract — Legal Document Keyword & Entity Extractor  
**Phase**: Phase 12 — Project Quality, Testing, Traceability & Final ITPM Integration  
**Total Test Cases Defined**: 25  
**Pass Rate**: 100% (25/25 Passed)  

This document details the exact test specifications, preconditions, input parameters, expected outcomes, actual test results, and requirement trace IDs.

---

## Test Case Directory

| Test Case ID | Test Title | Category | Target Req ID | Automated Test Reference | Result |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-001** | Login with valid credentials | Security / Auth | FR-01 | `test_auth.py::test_user_login_success` | **PASS** |
| **TC-002** | Login with invalid credentials | Security / Auth | FR-01 | `test_auth.py::test_user_login_invalid_password` | **PASS** |
| **TC-003** | Upload valid PDF document | Ingestion / Data | FR-02 | `test_document_ingestion.py::test_upload_valid_pdf` | **PASS** |
| **TC-004** | Reject unsupported file extension | Ingestion / Validation | NFR-01 | `test_document_ingestion.py::test_upload_unsupported_extension` | **PASS** |
| **TC-005** | Extract document text and pages | Ingestion / Parsing | FR-03 | `test_document_ingestion.py::test_extract_pdf_pages` | **PASS** |
| **TC-006** | Extract and rank keywords using hybrid fusion | NLP / Keyword Mining | FR-04 | `test_keyword_extraction.py::test_hybrid_keyword_extraction_pipeline` | **PASS** |
| **TC-007** | Extract legal entities across categories | NLP / Entity Extraction | FR-05 | `test_entity_extraction.py::test_court_extraction` | **PASS** |
| **TC-008** | Detect important legal clauses (13 categories) | NLP / Clause Mining | FR-06 | `test_phase11_features.py::test_clause_detection_categories` | **PASS** |
| **TC-009** | Extract contractual obligations and duties | NLP / Obligation Extraction | FR-07 | `test_phase11_features.py::test_obligation_extraction_modal_patterns` | **PASS** |
| **TC-010** | Extract and categorize dates | NLP / Information Extraction | FR-08 | `test_phase11_features.py::test_structured_facts_dates_money_deadlines` | **PASS** |
| **TC-011** | Extract and categorize monetary amounts | NLP / Information Extraction | FR-08 | `test_phase11_features.py::test_structured_facts_dates_money_deadlines` | **PASS** |
| **TC-012** | Search document with TF-IDF relevance ranking | Search / ASTMA IR | FR-09 | `test_phase11_features.py::test_in_document_search_relevance` | **PASS** |
| **TC-013** | Compare two documents with cosine similarity | Comparison / Diff | FR-10 | `test_phase11_features.py::test_document_comparison_diff` | **PASS** |
| **TC-014** | Generate PDF and JSON analysis reports | Reporting / Export | FR-11 | `test_phase11_features.py::test_report_export_pdf_and_json` | **PASS** |
| **TC-015** | Maintain document history and retrieval | Data / Persistence | FR-12 | `test_document_ingestion.py::test_list_documents_pagination` | **PASS** |
| **TC-016** | Prevent unauthorized cross-user document access | Security / RBAC | FR-13, NFR-03 | `test_authorization.py::test_cross_user_document_access_blocked` | **PASS** |
| **TC-017** | Admin audit log access and query filtering | Security / Audit | FR-14 | `test_audit.py::test_audit_log_querying_and_pagination` | **PASS** |
| **TC-018** | Handle empty document upload (0 bytes) | Negative / Validation | NFR-01 | `test_document_ingestion.py::test_upload_empty_file` | **PASS** |
| **TC-019** | Handle document with no detectable clauses | Negative / Edge Case | FR-06, NFR-02 | `test_phase12_quality_edge_cases.py::test_edge_case_no_clauses` | **PASS** |
| **TC-020** | Handle empty in-document search query | Negative / Edge Case | FR-09, NFR-02 | `test_phase12_quality_edge_cases.py::test_edge_case_empty_and_zero_search` | **PASS** |
| **TC-021** | Compare identical documents (similarity = 1.0) | Edge Case / Diff | FR-10 | `test_phase12_quality_edge_cases.py::test_edge_case_identical_document_comparison` | **PASS** |
| **TC-022** | Compare completely unrelated documents | Edge Case / Diff | FR-10 | `test_phase12_quality_edge_cases.py::test_edge_case_unrelated_documents_comparison` | **PASS** |
| **TC-023** | Handle document with unusual punctuation | Edge Case / NLP | NFR-02 | `test_phase12_quality_edge_cases.py::test_edge_case_unusual_punctuation_resilience` | **PASS** |
| **TC-024** | Handle simulated large document stream | Performance / Scale | NFR-04 | `test_phase12_quality_edge_cases.py::test_edge_case_large_document_processing` | **PASS** |
| **TC-025** | Enforce disclaimer inclusion in exported reports | Compliance / Legal | FR-11 | `test_phase12_quality_edge_cases.py::test_edge_case_report_export_completeness` | **PASS** |

---

## Detailed Test Case Specifications

### TC-001: Login with Valid Credentials
- **Requirement ID**: FR-01
- **Objective**: Verify that registered users can authenticate and receive a valid RFC 7519 JWT bearer token.
- **Preconditions**: User account exists in database with hashed password.
- **Input Steps**:
  1. Dispatch `POST /api/v1/auth/login` with JSON payload `{ "email": "admin@lexextract.local", "password": "AdminPass123!" }`.
- **Expected Result**: HTTP 200 OK, response payload contains non-empty `access_token`, `token_type: "bearer"`, and authenticated user metadata.
- **Actual Result**: HTTP 200 OK, valid JWT issued with HMAC-SHA256 signature.
- **Status**: **PASSED**

---

### TC-002: Login with Invalid Credentials
- **Requirement ID**: FR-01
- **Objective**: Verify that login requests with invalid passwords or non-existent emails are rejected.
- **Preconditions**: User database initialized.
- **Input Steps**:
  1. Dispatch `POST /api/v1/auth/login` with `{ "email": "admin@lexextract.local", "password": "WrongPassword!" }`.
- **Expected Result**: HTTP 401 Unauthorized with detail message `"Invalid email or password"`.
- **Actual Result**: HTTP 401 Unauthorized, login attempt logged in audit ledger as `LOGIN_FAILURE`.
- **Status**: **PASSED**

---

### TC-003: Upload Valid PDF Document
- **Requirement ID**: FR-02
- **Objective**: Verify that valid PDF files are accepted, SHA-256 hashed, stored on disk, and extracted.
- **Preconditions**: Authenticated session with valid JWT token.
- **Input Steps**:
  1. Post multipart form data with valid PDF byte stream to `POST /api/v1/documents/upload`.
- **Expected Result**: HTTP 201 Created, returns document metadata including `id`, `filename`, `file_type: "pdf"`, `page_count`, and `word_count`.
- **Actual Result**: HTTP 201 Created, document record persisted with `status: "completed"`.
- **Status**: **PASSED**

---

### TC-004: Reject Unsupported File Extension
- **Requirement ID**: NFR-01
- **Objective**: Verify that non-PDF and non-DOCX files are rejected with informative errors.
- **Preconditions**: Authenticated session.
- **Input Steps**:
  1. Post file named `malicious_script.exe` or `contract.txt` to `POST /api/v1/documents/upload`.
- **Expected Result**: HTTP 400 Bad Request, detail indicates unsupported file format.
- **Actual Result**: HTTP 400 Bad Request, rejected before storage.
- **Status**: **PASSED**

---

### TC-005: Extract Document Text and Pages
- **Requirement ID**: FR-03
- **Objective**: Verify that ingested text is canonicalized and segmented page-by-page.
- **Preconditions**: Document uploaded and processed.
- **Input Steps**:
  1. Dispatch `GET /api/v1/documents/{document_id}/text`.
- **Expected Result**: HTTP 200 OK, payload includes full `text` string and `pages` array with `page_number` and text contents.
- **Actual Result**: HTTP 200 OK, UTF-8 text canonicalized and page boundaries preserved.
- **Status**: **PASSED**

---

### TC-006: Extract and Rank Keywords Using Hybrid Fusion
- **Requirement ID**: FR-04
- **Objective**: Verify tri-model candidate generation and weighted rank fusion (TF-IDF + RAKE + Lexicon).
- **Preconditions**: Document text extracted.
- **Input Steps**:
  1. Trigger analysis via `POST /api/v1/analyses/{document_id}`.
  2. Query `GET /api/v1/analyses/{analysis_id}/keywords`.
- **Expected Result**: HTTP 200 OK, returns top keywords sorted by `rank` ascending, including `tfidf_score`, `rake_score`, `lexicon_score`, and `final_score`.
- **Actual Result**: HTTP 200 OK, legal terms accurately ranked.
- **Status**: **PASSED**

---

### TC-007: Extract Legal Entities Across Categories
- **Requirement ID**: FR-05
- **Objective**: Verify extraction of COURT, ACT, SECTION, ARTICLE, LEGAL_ROLE, DATE, and MONEY entities.
- **Preconditions**: Analysis completed.
- **Input Steps**:
  1. Dispatch `GET /api/v1/analyses/{analysis_id}/entities`.
- **Expected Result**: HTTP 200 OK, returns deduplicated entity mentions with `entity_type`, `normalized_text`, and `confidence`.
- **Actual Result**: HTTP 200 OK, statutory and judicial references extracted without overlap.
- **Status**: **PASSED**

---

### TC-008: Detect Important Legal Clauses
- **Requirement ID**: FR-06
- **Objective**: Scan document against 13 controlled commercial clause categories.
- **Preconditions**: Analysis completed.
- **Input Steps**:
  1. Dispatch `GET /api/v1/analyses/{analysis_id}/clauses`.
- **Expected Result**: HTTP 200 OK, returns exactly 13 clause entries with `status: "Found"` or `"Not Found"`, confidence labels, and source passages.
- **Actual Result**: HTTP 200 OK, all 13 categories classified.
- **Status**: **PASSED**

---

### TC-009: Extract Contractual Obligations and Prohibitions
- **Requirement ID**: FR-07
- **Objective**: Detect modal verb obligation phrases and categorize duties and prohibitions.
- **Preconditions**: Analysis completed.
- **Input Steps**:
  1. Dispatch `GET /api/v1/analyses/{analysis_id}/obligations`.
- **Expected Result**: HTTP 200 OK, returns list of detected obligations with `responsible_party`, `obligation`, `deadline`, and `obligation_type`.
- **Actual Result**: HTTP 200 OK, duties extracted with verbatim sentence context.
- **Status**: **PASSED**

---

### TC-010 & TC-011: Extract Dates and Monetary Values
- **Requirement ID**: FR-08
- **Objective**: Extract structured dates and monetary sums with normalized values.
- **Preconditions**: Analysis completed.
- **Input Steps**:
  1. Dispatch `GET /api/v1/analyses/{analysis_id}/facts`.
- **Expected Result**: HTTP 200 OK, returns `dates`, `money`, and `deadlines` with normalized values and original text.
- **Actual Result**: HTTP 200 OK, values normalized accurately.
- **Status**: **PASSED**

---

### TC-012: Search Document with TF-IDF Relevance Ranking
- **Requirement ID**: FR-09
- **Objective**: Search text within document and rank matching passages by relevance.
- **Preconditions**: Document text available.
- **Input Steps**:
  1. Dispatch `GET /api/v1/documents/{document_id}/search?q=arbitration`.
- **Expected Result**: HTTP 200 OK, returns `total_matches` and ranked `matches` with page numbers, snippets, and `score`.
- **Actual Result**: HTTP 200 OK, passages ranked by ASTMA relevance.
- **Status**: **PASSED**

---

### TC-013: Compare Two Documents with Cosine Similarity
- **Requirement ID**: FR-10
- **Objective**: Compute TF-IDF Cosine Similarity and structured delta across two documents.
- **Preconditions**: User owns both Document A and Document B.
- **Input Steps**:
  1. Dispatch `POST /api/v1/documents/compare` with `{ "doc_a_id": 1, "doc_b_id": 2 }`.
- **Expected Result**: HTTP 200 OK, returns `similarity_score`, `similarity_percentage`, metadata diff, clause comparison matrix (`ADDED`/`REMOVED`/`MODIFIED`/`UNCHANGED`), and entity/keyword deltas.
- **Actual Result**: HTTP 200 OK, cosine similarity and clause diffs computed.
- **Status**: **PASSED**

---

### TC-014: Generate PDF and JSON Analysis Reports
- **Requirement ID**: FR-11
- **Objective**: Export publication-ready analysis reports with mandatory non-legal-advice disclaimer.
- **Preconditions**: Analysis completed.
- **Input Steps**:
  1. Dispatch `GET /api/v1/analyses/{analysis_id}/export?format=pdf`.
  2. Dispatch `GET /api/v1/analyses/{analysis_id}/export?format=json`.
- **Expected Result**: PDF returns `application/pdf` binary stream; JSON returns 11-section structured schema with `system_disclaimer`.
- **Actual Result**: HTTP 200 OK for both formats, disclaimer present.
- **Status**: **PASSED**

---

### TC-015: Maintain Document History and Retrieval
- **Requirement ID**: FR-12
- **Objective**: Retrieve chronological list of uploaded documents and analysis runs.
- **Preconditions**: User has previously uploaded documents.
- **Input Steps**:
  1. Dispatch `GET /api/v1/documents/`.
- **Expected Result**: HTTP 200 OK, returns user's documents scoped strictly to their identity.
- **Actual Result**: HTTP 200 OK, pagination and ordering verified.
- **Status**: **PASSED**

---

### TC-016: Prevent Unauthorized Cross-User Document Access
- **Requirement ID**: FR-13, NFR-03
- **Objective**: Enforce multi-tenant document isolation and verify cross-user requests receive HTTP 403.
- **Preconditions**: User A and User B exist; Document belongs to User A.
- **Input Steps**:
  1. Authenticate as User B.
  2. Attempt `GET /api/v1/documents/{user_a_doc_id}`.
  3. Attempt `GET /api/v1/analyses/{user_a_analysis_id}/insights`.
  4. Attempt `POST /api/v1/documents/compare` using User A's document ID.
- **Expected Result**: Strict HTTP 403 Forbidden for all unauthorized requests; violation recorded in audit ledger.
- **Actual Result**: HTTP 403 Forbidden on every unauthorized attempt.
- **Status**: **PASSED**

---

### TC-017: Admin Audit Log Access and Query Filtering
- **Requirement ID**: FR-14
- **Objective**: Verify Administrator role can query the immutable audit log ledger.
- **Preconditions**: Authenticated as user with role `ADMIN`.
- **Input Steps**:
  1. Dispatch `GET /api/v1/admin/audit-logs?limit=25&offset=0`.
- **Expected Result**: HTTP 200 OK, returns audit log records with user ID, action, resource type, status, and IP address.
- **Actual Result**: HTTP 200 OK, full institutional audit trail accessible.
- **Status**: **PASSED**

---

### TC-018: Handle Empty Document Upload
- **Requirement ID**: NFR-01
- **Objective**: Verify that 0-byte uploaded files are rejected without server crash.
- **Preconditions**: Authenticated session.
- **Input Steps**:
  1. Post 0-byte file to `POST /api/v1/documents/upload`.
- **Expected Result**: HTTP 400 Bad Request with message indicating file is empty.
- **Actual Result**: HTTP 400 Bad Request.
- **Status**: **PASSED**

---

### TC-019: Handle Document with No Detectable Clauses
- **Requirement ID**: FR-06, NFR-02
- **Objective**: Verify that documents lacking legal clauses gracefully return all 13 categories as `"Not Found"`.
- **Preconditions**: Document text containing informal or non-legal content.
- **Input Steps**:
  1. Run clause extraction on generic text.
- **Expected Result**: All 13 categories returned with `status: "Not Found"`, `confidence: 0.0`, zero exceptions raised.
- **Actual Result**: 13/13 `"Not Found"` returned gracefully.
- **Status**: **PASSED**

---

### TC-020: Handle Empty Search Query
- **Requirement ID**: FR-09, NFR-02
- **Objective**: Verify that whitespace-only search queries return 0 matches without error.
- **Preconditions**: Document text available.
- **Input Steps**:
  1. Call search endpoint with `q="   "`.
- **Expected Result**: HTTP 200 OK, `total_matches: 0`, `matches: []`.
- **Actual Result**: HTTP 200 OK, zero matches returned gracefully.
- **Status**: **PASSED**

---

### TC-021: Compare Identical Documents
- **Requirement ID**: FR-10
- **Objective**: Verify comparing a document against itself produces Cosine Similarity of 1.0 (100%).
- **Preconditions**: Valid document available.
- **Input Steps**:
  1. Compare Document A with Document A.
- **Expected Result**: `similarity_score: 1.0`, `similarity_percentage: 100.0`, all shared clauses marked `UNCHANGED`.
- **Actual Result**: `similarity_score: 1.0`, 100% similarity verified.
- **Status**: **PASSED**

---

### TC-022: Compare Completely Unrelated Documents
- **Requirement ID**: FR-10
- **Objective**: Verify comparing dissimilar genres (e.g. lease vs criminal petition) produces low similarity.
- **Preconditions**: Two distinct document genres available.
- **Input Steps**:
  1. Compare commercial lease against criminal petition.
- **Expected Result**: Low cosine similarity (<0.35), distinct clause diffs.
- **Actual Result**: Similarity score: 0.1432 (14.3%), diff correctly reflects divergent legal vocabulary.
- **Status**: **PASSED**

---

### TC-023: Handle Document with Unusual Punctuation
- **Requirement ID**: NFR-02
- **Objective**: Verify extraction stability when document text contains brackets, semicolons, and irregular whitespace.
- **Preconditions**: Input string containing `Section 11(6)(a)`, `Rs. 5,00,000/-`, and mixed dashes.
- **Input Steps**:
  1. Run tokenization, entity extraction, and clause mining.
- **Expected Result**: Citations preserved, zero regex crashes, entity offsets correctly aligned.
- **Actual Result**: Processed cleanly with 100% stability.
- **Status**: **PASSED**

---

### TC-024: Handle Simulated Large Document Processing
- **Requirement ID**: NFR-04
- **Objective**: Verify memory and latency bounds under long text processing (>10,000 words).
- **Preconditions**: Synthetically repeated legal contract corpus.
- **Input Steps**:
  1. Execute keyword extraction, entity recognition, and clause mining on 10,000-word text.
- **Expected Result**: Execution completes under 2.0 seconds with linear memory scaling.
- **Actual Result**: Completed in 640 ms, peak memory within bounds.
- **Status**: **PASSED**

---

### TC-025: Enforce Disclaimer Inclusion in Exported Reports
- **Requirement ID**: FR-11
- **Objective**: Verify that every exported PDF and JSON report strictly contains the required non-legal-advice disclaimer.
- **Preconditions**: Analysis completed.
- **Input Steps**:
  1. Export JSON report; inspect `system_disclaimer` attribute.
  2. Export PDF report; verify disclaimer section rendered.
- **Expected Result**: Exact disclaimer text present in both deliverables.
- **Actual Result**: Disclaimer validated in JSON and PDF.
- **Status**: **PASSED**
