# LexExtract — Requirements Traceability Matrix (RTM)

**Project**: LexExtract — Legal Document Keyword & Entity Extractor  
**Phase**: Phase 12 — Project Quality, Testing, Traceability & Final ITPM Integration  
**Governance Framework**: IEEE 830 / ISO/IEC/IEEE 29148 Requirements Engineering & Traceability  

This matrix maps every functional requirement (FR) and non-functional requirement (NFR) forward to its architectural design module, concrete API route/frontend component, automated test case, and implementation verification status.

---

## 1. Functional Requirements Traceability (FR-01 to FR-14)

| Req ID | Requirement Description | Design Module / Service | API Endpoint / Frontend Component | Verification Test Case ID | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **FR-01** | User shall be able to register and login with secure credentials. | Auth Service, JWT Manager, Argon2id Hash Engine | `POST /api/v1/auth/register`<br/>`POST /api/v1/auth/login`<br/>`frontend/src/pages/LoginPage.jsx`<br/>`frontend/src/pages/RegisterPage.jsx` | `TC-001`<br/>`TC-002`<br/>`test_auth.py::test_user_registration_success`<br/>`test_auth.py::test_user_login_success` | **PASSED** |
| **FR-02** | User shall be able to upload a supported legal document (`.pdf`, `.docx`). | Document Processing Service, Document Validator, File Storage | `POST /api/v1/documents/upload`<br/>`frontend/src/pages/NewAnalysisPage.jsx` | `TC-003`<br/>`TC-004`<br/>`test_document_ingestion.py::test_upload_valid_pdf`<br/>`test_document_ingestion.py::test_upload_valid_docx` | **PASSED** |
| **FR-03** | System shall extract document text and segment by pages. | Document Extractor (PyMuPDF, python-docx), Text Preprocessor | `GET /api/v1/documents/{id}/text`<br/>`frontend/src/pages/DocumentViewerPage.jsx` | `TC-005`<br/>`test_document_ingestion.py::test_extract_pdf_pages`<br/>`test_document_ingestion.py::test_extract_docx_paragraphs` | **PASSED** |
| **FR-04** | System shall extract and rank keywords using hybrid statistical scoring. | Keyword Extractor (Candidate Generator, TF-IDF Scorer, RAKE Scorer, Lexicon Scorer, Rank Fusion) | `POST /api/v1/analyses/{doc_id}`<br/>`GET /api/v1/analyses/{id}/keywords`<br/>`frontend/src/pages/AnalysisResultsPage.jsx` | `TC-006`<br/>`test_keyword_extraction.py::test_hybrid_keyword_extraction_pipeline`<br/>`test_keyword_extraction.py::test_tfidf_scoring` | **PASSED** |
| **FR-05** | System shall extract legal entities across 13 domain categories. | Legal Entity Extractor (spaCy NER, Gazetteer Engine, Regex Rules, Deduplicator) | `GET /api/v1/analyses/{id}/entities`<br/>`GET /api/v1/analyses/{id}/entities/summary`<br/>`frontend/src/pages/AnalysisResultsPage.jsx` | `TC-007`<br/>`test_entity_extraction.py::test_court_extraction`<br/>`test_entity_extraction.py::test_section_and_act_extraction` | **PASSED** |
| **FR-06** | System shall identify important clauses across 13 legal categories. | Clause Mining Service (Pattern Matcher, Heading Detector, Confidence Evaluator) | `GET /api/v1/analyses/{id}/clauses`<br/>`frontend/src/pages/AnalysisResultsPage.jsx` | `TC-008`<br/>`test_phase11_features.py::test_clause_detection_categories`<br/>`test_phase12_quality_edge_cases.py::test_edge_case_no_clauses` | **PASSED** |
| **FR-07** | System shall identify contractual obligations, responsibilities, and prohibitions. | Obligation Extraction Service (Modal Verb Parser, Party Resolver, Deadline Matcher) | `GET /api/v1/analyses/{id}/obligations`<br/>`frontend/src/pages/AnalysisResultsPage.jsx` | `TC-009`<br/>`test_phase11_features.py::test_obligation_extraction_modal_patterns`<br/>`test_phase12_quality_edge_cases.py::test_edge_case_obligation_prohibitions` | **PASSED** |
| **FR-08** | System shall extract and normalize dates, monetary values, and deadlines. | Structured Facts Service (Regex Normalizer, Context Categorizer) | `GET /api/v1/analyses/{id}/facts`<br/>`frontend/src/pages/AnalysisResultsPage.jsx` | `TC-010`<br/>`TC-011`<br/>`test_phase11_features.py::test_structured_facts_dates_money_deadlines` | **PASSED** |
| **FR-09** | User shall be able to search within a document with ASTMA relevance scoring. | Document Search Engine (TF-IDF Passage Scorer, Offset Matcher) | `GET /api/v1/documents/{id}/search?q=...`<br/>`frontend/src/pages/AnalysisResultsPage.jsx`<br/>`frontend/src/pages/DocumentViewerPage.jsx` | `TC-012`<br/>`test_phase11_features.py::test_in_document_search_relevance`<br/>`test_phase12_quality_edge_cases.py::test_edge_case_empty_and_zero_search` | **PASSED** |
| **FR-10** | User shall be able to compare two documents side-by-side with similarity scoring. | Document Comparison Engine (TF-IDF Cosine Similarity, Clause/Keyword/Entity Diff) | `POST /api/v1/documents/compare`<br/>`frontend/src/pages/DocumentComparePage.jsx` | `TC-013`<br/>`test_phase11_features.py::test_document_comparison_diff`<br/>`test_phase12_quality_edge_cases.py::test_edge_case_identical_document_comparison` | **PASSED** |
| **FR-11** | User shall be able to export an analysis report in PDF and JSON formats. | Report Generator Service (PyMuPDF Multi-Page Formatter, JSON Serializer, Disclaimer Engine) | `GET /api/v1/analyses/{id}/export?format=pdf\|json`<br/>`frontend/src/pages/AnalysisResultsPage.jsx` | `TC-014`<br/>`test_phase11_features.py::test_report_export_pdf_and_json`<br/>`test_phase12_quality_edge_cases.py::test_edge_case_report_export_completeness` | **PASSED** |
| **FR-12** | System shall maintain document repository history and past analysis runs. | Repository History Service, Document Registry | `GET /api/v1/documents/`<br/>`GET /api/v1/analyses/document/{id}`<br/>`frontend/src/pages/DocumentHistoryPage.jsx` | `TC-015`<br/>`test_document_ingestion.py::test_list_documents_pagination`<br/>`test_database.py::test_document_crud` | **PASSED** |
| **FR-13** | System shall enforce strict user ownership and multi-tenant document isolation. | Security Dependencies (`check_document_access`), DB Query Scoping | `backend/app/core/deps.py`<br/>All document and analysis endpoints | `TC-016`<br/>`test_authorization.py::test_cross_user_document_access_blocked`<br/>`test_phase11_features.py::test_phase11_api_endpoints_and_rbac` | **PASSED** |
| **FR-14** | Admin shall be able to access system governance audit information. | Audit Service, Audit Ledger Table (`audit_logs`) | `GET /api/v1/admin/audit-logs`<br/>`GET /api/v1/users/`<br/>`frontend/src/pages/AdminAuditPage.jsx` | `TC-017`<br/>`test_audit.py::test_audit_log_querying_and_pagination`<br/>`test_authorization.py::test_admin_can_access_audit_logs` | **PASSED** |

---

## 2. Non-Functional Requirements Traceability (NFR-01 to NFR-05)

| Req ID | Requirement Description | Design Module / Service | Architectural Safeguard | Verification Test Case ID | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **NFR-01** | System shall provide appropriate validation (MIME, size, empty file, schema). | Document Validator, Pydantic Request Models | Magic byte verification, 25MB limit, 400/413 HTTP rejection | `TC-004`<br/>`TC-018`<br/>`test_document_ingestion.py::test_upload_file_too_large`<br/>`test_document_ingestion.py::test_upload_empty_file` | **PASSED** |
| **NFR-02** | System shall provide meaningful error handling without exposing stack traces. | Global Exception Handlers, Structured JSON Responses | Uniform error envelopes (`detail`), zero unhandled 500 dumps in UI | `TC-019`<br/>`test_health.py::test_404_handling`<br/>`test_phase12_quality_edge_cases.py::test_edge_case_malformed_document` | **PASSED** |
| **NFR-03** | Unauthorized users shall strictly not access another user's documents or analyses. | Role & Ownership Guards, RFC 7519 Bearer Claims | HTTP 403 Forbidden on ownership mismatch, HTTP 401 on missing token | `TC-016`<br/>`test_authorization.py::test_unauthenticated_protected_endpoint_returns_401`<br/>`test_authorization.py::test_analyst_cannot_access_other_users_document` | **PASSED** |
| **NFR-04** | The system shall maintain acceptable response time for supported documents (<2s). | In-Memory Tokenizer, Local PyMuPDF Stream, Vectorized TF-IDF | Latency benchmarking (average per-document execution: 258.2 ms) | `TC-020`<br/>`test_evaluation.py::test_evaluation_benchmark_runtime`<br/>`latest_evaluation_report.json` | **PASSED** |
| **NFR-05** | The UI shall be usable, responsive, and follow institutional legal aesthetics. | React 18 SPA, Tailwind Typography, Modular Tabs | Screen layout tested at 1536x730, zero horizontal overflow, clear hierarchy | `TC-021`<br/>Browser subagent verification (`phase11_verification_1791222811114.webp`) | **PASSED** |

---

## 3. Requirements Coverage Metrics

- **Total Functional Requirements Defined**: 14 (100%)
- **Total Functional Requirements Implemented**: 14 (100%)
- **Total Functional Requirements Tested**: 14 (100%)
- **Total Non-Functional Requirements Defined**: 5 (100%)
- **Total Non-Functional Requirements Tested**: 5 (100%)
- **Overall Traceability Coverage**: **100% (19/19 Requirements Verified & Traceable)**
