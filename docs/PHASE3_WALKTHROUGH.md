# Phase 3 Walkthrough — Document Ingestion & Text Processing

**Project Title:** LexExtract – Legal Document Keyword Extractor  
**Phase:** Phase 3 – Document Ingestion & Text Processing  
**Status:** Completed & 100% Verified  

---

## 1. Phase Objective

The objective of Phase 3 is to implement the end-to-end document ingestion and text processing pipeline for LexExtract:
- Ingest real legal documents in `.pdf` and `.docx` formats.
- Enforce strict validation rules (MIME type, file extension, max 10 MB size, non-empty content).
- Ensure safe server-side storage with UUID-obfuscated filenames and path-traversal prevention.
- Compute SHA-256 cryptographic hashes for document integrity tracking.
- Extract textual streams page-by-page (PyMuPDF for PDF) or paragraph/table-by-paragraph (python-docx for DOCX).
- DOCX files preserve native structure without fabricating page numbers (`page_count = null`).
- Preprocess legal text cleanly (Unicode NFKC ligature fixing, whitespace cleaning, while strictly preserving legal citation constructs such as `Section 10(2)`, `Article 14`, `Rs. 50,000`).
- Persist metadata, preprocessed text, and page segments directly in the SQLite `documents` table.
- Connect the React frontend (`NewAnalysisPage` and `DocumentViewerPage`) to support uploading files and reading extracted prose.

---

## 2. Ingestion & Text Processing Architecture

```
Client (React / API)
        │  POST /api/v1/documents/upload (multipart/form-data)
        ▼
documents.py (FastAPI Endpoint)
        │
        ▼
document_processing_service.py (Pipeline Coordinator)
        │
        ├── 1. document_validator.py  (Check extension, MIME, <=10MB size, non-empty)
        ├── 2. file_storage.py        (UUID filename, path traversal guard, SHA-256 hash)
        ├── 3. document_extractor.py  (Dispatcher)
        │       ├── pdf_extractor.py  (PyMuPDF page-by-page text extraction)
        │       └── docx_extractor.py (python-docx paragraph & table extraction)
        ├── 4. text_preprocessor.py   (Unicode NFKC, legal citations & symbols preservation)
        └── 5. database.py (Session)  (Persist in 'documents' table with status='completed')
```

---

## 3. Dependencies Added

In `backend/requirements.txt`:
- `pymupdf>=1.23.0` (Installed version: `1.28.2`)
- `python-docx>=1.1.0` (Installed version: `1.2.0`)
- `python-multipart>=0.0.9` (Installed version: `0.0.32`)
*(Zero NLP, spaCy, scikit-learn, RAKE, or OCR libraries installed).*

---

## 4. Files Created & Modified

### Files Created
- `backend/app/services/document_validator.py` — File extension, MIME type, emptiness, and size validation.
- `backend/app/services/file_storage.py` — UUID file storage in `storage/uploads/` and SHA-256 hash generation.
- `backend/app/services/pdf_extractor.py` — PyMuPDF text extractor with page segmentation and empty/scanned PDF handling.
- `backend/app/services/docx_extractor.py` — python-docx paragraph/table extractor with `page_count = None`.
- `backend/app/services/document_extractor.py` — Unified extraction dispatcher.
- `backend/app/services/text_preprocessor.py` — Unicode normalizer, whitespace cleaner, and explainable legal tokenizer.
- `backend/app/services/document_processing_service.py` — Master ingestion orchestrator.
- `backend/tests/test_document_ingestion.py` — 13 new unit and integration tests.
- `sample_documents/sample_contract.pdf` — Realistic 2-page commercial lease agreement.
- `sample_documents/sample_legal_notice.docx` — Realistic Section 138 statutory legal notice with table.
- `docs/phase3_implementation_plan.md` — Phase 3 architecture blueprint.

### Files Modified
- `backend/requirements.txt` — Added `pymupdf`, `python-docx`, `python-multipart`.
- `backend/app/core/config.py` — Configured `MAX_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024` (10 MB).
- `backend/app/models/document.py` — Added `extracted_text` and `pages_json` columns, set `page_count` to nullable.
- `backend/app/schemas/document.py` — Added `DocumentUploadResponse`, `DocumentTextResponse`, `PageContent`.
- `backend/app/schemas/__init__.py` — Exported new schemas.
- `backend/app/services/__init__.py` — Exported all service functions.
- `backend/app/api/v1/endpoints/documents.py` — Implemented `POST /upload` and `GET /{id}/text`.
- `backend/app/core/database.py` — Added backward-compatible column migration in `init_db()`.
- `frontend/src/services/api.js` — Added `uploadDocument` and `getDocumentText`.
- `frontend/src/pages/NewAnalysisPage.jsx` — Implemented upload interface, format badge, and metadata result card.
- `frontend/src/pages/DocumentViewerPage.jsx` — Implemented reader view with document selector and page sections.
- `frontend/src/App.jsx` — Connected navigation from upload success to document reader.
- `README.md` — Updated with Phase 3 status and capabilities.

---

## 5. Workflows Implemented

### 5.1 Document Upload Workflow
1. Client submits `POST /api/v1/documents/upload` with a multipart file.
2. `document_validator.py` checks:
   - Filename present.
   - Non-zero file size.
   - Size $\le 10\text{ MB}$.
   - Extension in `{'.pdf', '.docx'}`.
   - MIME type matches authorized legal document types.
3. `file_storage.py` computes SHA-256 and writes bytes to `storage/uploads/{uuid}.{ext}`.
4. Record inserted in database with status `"processing"`.
5. Extraction and preprocessing executed.
6. Record updated with word count, page count, normalized text, and status `"completed"`.
7. Client receives `HTTP 201 Created` with `DocumentUploadResponse`.

### 5.2 PDF Extraction Workflow
- PyMuPDF opens the PDF document stream.
- Document page count is retrieved natively from PDF catalog.
- Iterates over each page, extracting text with line structure intact.
- If text is completely empty across all pages, flags an informative non-fatal warning: `"PDF contains little or no extractable text. OCR is not enabled in this version."` (Zero server crash).

### 5.3 DOCX Extraction Workflow
- python-docx iterates through document body paragraphs and table rows.
- Table rows are joined using vertical bar separators to preserve relational tabular context.
- `page_count` is explicitly set to `None` to avoid fabricating artificial page counts.

### 5.4 Preprocessing Workflow
- Unicode normalization (NFKC) resolves font ligatures (`fi`, `fl`).
- Reconnects hyphenated line-broken words (`obli-\ngation` $\rightarrow$ `obligation`).
- Collapses excessive blank lines to clean double newlines.
- Rule-based tokenizer preserves statutory constructs (`Section 10(2)`, `Article 14`, `Rs. 50,000`).

---

## 6. Database Changes

Table: `documents` (SQLite)
- `page_count`: Changed constraint to `NULLABLE` (Integer) to accommodate DOCX format.
- `extracted_text`: Added `TEXT NULLABLE` storing the full normalized document prose for Phase 4 keyword algorithms.
- `pages_json`: Added `TEXT NULLABLE` storing JSON serialized array of page objects `[{"page_number": 1, "text": "..."}]`.

---

## 7. API Endpoints Verified

| Method | Endpoint | Status | Description |
| :--- | :--- | :---: | :--- |
| `POST` | `/api/v1/documents/upload` | **201 Created** | Uploads & parses PDF/DOCX document |
| `GET` | `/api/v1/documents/{id}/text` | **200 OK** | Retrieves normalized text and page breakdown |
| `GET` | `/api/v1/documents/{id}` | **200 OK** | Retrieves document metadata (no filesystem path leaked) |
| `GET` | `/api/v1/documents/` | **200 OK** | Lists all ingested documents in the system |

---

## 8. Test Execution Results

Executed `pytest -v` across the entire backend suite (28 / 28 Passed):

```
tests/test_database.py::test_tables_created PASSED                       [  3%]
tests/test_database.py::test_user_creation_and_unique_email PASSED       [  7%]
tests/test_database.py::test_document_referencing_user PASSED            [ 10%]
tests/test_database.py::test_analysis_run_keyword_and_entity_relationship PASSED [ 14%]
tests/test_database.py::test_audit_log_referencing_user PASSED           [ 17%]
tests/test_database.py::test_password_hash_never_exposed_in_user_response PASSED [ 21%]
tests/test_database.py::test_api_health_check_database_status PASSED     [ 25%]
tests/test_database.py::test_api_list_users_omits_password_hash PASSED   [ 28%]
tests/test_database.py::test_api_list_documents PASSED                   [ 32%]
tests/test_database.py::test_api_analysis_not_found PASSED               [ 35%]
tests/test_database.py::test_cascade_delete_document_removes_runs PASSED [ 39%]
tests/test_database.py::test_api_get_single_document_by_id PASSED        [ 42%]
tests/test_document_ingestion.py::test_legal_text_normalization_preserves_citations PASSED [ 46%]
tests/test_document_ingestion.py::test_legal_tokenizer PASSED            [ 50%]
tests/test_document_ingestion.py::test_word_count_calculation PASSED     [ 53%]
tests/test_document_ingestion.py::test_file_validator_rules PASSED       [ 57%]
tests/test_document_ingestion.py::test_upload_valid_pdf PASSED           [ 60%]
tests/test_document_ingestion.py::test_upload_valid_docx PASSED          [ 64%]
tests/test_document_ingestion.py::test_upload_unsupported_extension PASSED [ 67%]
tests/test_document_ingestion.py::test_upload_empty_file PASSED          [ 71%]
tests/test_document_ingestion.py::test_upload_oversized_file PASSED      [ 75%]
tests/test_document_ingestion.py::test_get_document_metadata_and_text_endpoints PASSED [ 78%]
tests/test_document_ingestion.py::test_corrupt_pdf_handled_gracefully PASSED [ 82%]
tests/test_document_ingestion.py::test_corrupt_docx_handled_gracefully PASSED [ 85%]
tests/test_document_ingestion.py::test_nonexistent_document_text_returns_404 PASSED [ 89%]
tests/test_health.py::test_root_endpoint PASSED                          [ 92%]
tests/test_health.py::test_health_endpoint PASSED                        [ 96%]
tests/test_api_v1_info_endpoint PASSED                                   [100%]

======================== 28 passed in 1.56s ========================
```

---

## 9. Live Browser Subagent Verification

Browser automated verification performed on `http://127.0.0.1:5173`:
1. **New Analysis Page:** Successfully rendered upload interface with drag/file selection, format labels ("PDF or DOCX · Maximum 10 MB"), and ingest action.
2. **Document Viewer Page:** Loaded document selector displaying all uploaded documents (`#1 sample_commercial_lease.pdf`, `#2 sample_contract.pdf`, `#3 sample_legal_notice.docx`).
3. **Text Reader Rendering:** Displayed extracted text sections page-by-page with word counts and editorial styling.
4. **Console Log:** 0 runtime or console errors.

---

## 10. Phase 3 Acceptance Criteria Checklist

| Criterion | Target | Status | Verification Evidence |
| :--- | :--- | :---: | :--- |
| **PDF Upload & Parsing** | PyMuPDF page-by-page text | **VERIFIED** | `sample_contract.pdf` uploaded (2 pages, 262 words) |
| **DOCX Upload & Parsing** | python-docx paragraphs/tables | **VERIFIED** | `sample_legal_notice.docx` uploaded (256 words) |
| **Page Count Null for DOCX**| Do not fabricate page numbers | **VERIFIED** | `page_count` is `None` in database and API |
| **Invalid Files Rejected** | Extensions, empty, >10MB | **VERIFIED** | Tested via unit and API integration tests |
| **Safe Storage & Hash** | UUID filename & SHA-256 | **VERIFIED** | Stored in `storage/uploads/`, hash recorded |
| **Text Preprocessing** | Preserve legal citations | **VERIFIED** | Tested `Section 10(2)`, `Article 14`, `Rs. 50,000` |
| **Extracted Text API** | `GET /documents/{id}/text` | **VERIFIED** | Responding with HTTP 200 and page breakdown |
| **Frontend Upload UI** | Real upload & result cards | **VERIFIED** | Tested live in browser |
| **Frontend Document Viewer**| Read extracted text | **VERIFIED** | Tested live in browser |
| **OCR Decision** | Informative warning, no crash | **VERIFIED** | Handled in `pdf_extractor.py` without Tesseract |
| **Phase 1 & 2 Non-Regression**| Health & DB endpoints intact | **VERIFIED** | All 15 prior tests still pass |
| **Phase 4 Scope Control** | Zero premature NLP / RAKE | **VERIFIED** | Confirmed no Phase 4+ code introduced |

---

## 11. Next Step
Phase 3 is 100% complete and verified. Execution is paused awaiting instruction to proceed to **Phase 4 (Keyword Extraction Engine: RAKE, TF-IDF, Legal Lexicon, and Hybrid Ranking)**.
