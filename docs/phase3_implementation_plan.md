# Implementation Plan — Phase 3: LexExtract Document Ingestion & Text Processing

**Project Title:** LexExtract – Legal Document Keyword Extractor  
**Phase:** Phase 3 – Document Ingestion & Text Processing  
**Status:** In Progress / Ready for Execution  

---

## 1. Phase Objective & Architectural Scope

The objective of Phase 3 is to construct the first real functional pipeline of **LexExtract**:
- Allow users to upload legal documents in `.pdf` and `.docx` format.
- Validate file extension, MIME/content type, emptiness, and file size (max 10 MB).
- Store files securely in `backend/storage/uploads/` using sanitized UUID storage names (path traversal protection).
- Compute SHA-256 cryptographic hashes for document integrity and tracking.
- Extract textual content page-by-page (PyMuPDF for PDF) or paragraph/table-by-paragraph (python-docx for DOCX).
- DOCX files will have `page_count = null` rather than fabricated page counts.
- Preprocess text cleanly (Unicode normalization, line breaks, whitespace cleaning, while strictly preserving legal citation structures such as "Section 10(2)", "Article 14", "Rs. 50,000", dates, and party designations).
- Store extracted text and document metadata in the existing `Document` relational database table.
- Expose structured REST API endpoints:
  - `POST /api/v1/documents/upload`
  - `GET /api/v1/documents/{id}/text`
  - `GET /api/v1/documents/{id}`
- Connect frontend minimally: allow file upload on `NewAnalysisPage` with real-time feedback, and display extracted text in `DocumentViewerPage`.

### Strict Scope Control (Deferred to Later Phases)
- NO NLP keyword algorithms (RAKE, TF-IDF, legal dictionary) -> Phase 4.
- NO legal entity recognition (regex citations, spaCy NER) -> Phase 5.
- NO authentication, JWT, or RBAC -> Phase 6 (uploaded docs temporarily linked to demo user).
- NO OCR (scanned PDFs with no text return a clear non-fatal notification without server crash).

---

## 2. Ingestion & Processing Pipeline

```
  [ Client File Upload (multipart/form-data) ]
                        │
                        ▼
  ┌───────────────────────────────────────────┐
  │  1. Document Validator Service             │
  │     - Extension check (.pdf, .docx)       │
  │     - Content/MIME type verification      │
  │     - Non-empty check (> 0 bytes)         │
  │     - Max size validation (<= 10 MB)      │
  └─────────────────────┬─────────────────────┘
                        │ Valid File
                        ▼
  ┌───────────────────────────────────────────┐
  │  2. File Storage Service                  │
  │     - Generate safe UUID filename         │
  │     - Stream to backend/storage/uploads/  │
  │     - Compute SHA-256 hash                │
  └─────────────────────┬─────────────────────┘
                        │
                        ▼
  ┌───────────────────────────────────────────┐
  │  3. Unified Document Extractor            │
  │     ├── PDF: PyMuPDF (page-by-page text)  │
  │     └── DOCX: python-docx (paragraphs/tbl)│
  └─────────────────────┬─────────────────────┘
                        │ Raw Text Stream + Pages
                        ▼
  ┌───────────────────────────────────────────┐
  │  4. Text Preprocessor Service             │
  │     - Unicode & whitespace normalization  │
  │     - Preserve legal structures & symbols │
  │     - Calculate accurate word count       │
  └─────────────────────┬─────────────────────┘
                        │ Preprocessed Text + Metadata
                        ▼
  ┌───────────────────────────────────────────┐
  │  5. Database Persistence                  │
  │     - Status: 'uploaded' -> 'completed'   │
  │     - Save Document record in SQLite      │
  │     - Association with Demo User (id=1)   │
  └─────────────────────┬─────────────────────┘
                        │
                        ▼
     [ HTTP 201 Created: DocumentResponse ]
```

---

## 3. Dependencies

- **`pymupdf`**: High-performance PDF parser preserving page numbers and text blocks.
- **`python-docx`**: Word document parser for paragraphs and table texts.
- **`python-multipart`**: Form-data parsing for FastAPI file uploads.
- *(No NLP, spaCy, scikit-learn, RAKE, or OCR dependencies).*

---

## 4. Database Schema Adjustments

In `backend/app/models/document.py`:
- Make `page_count` nullable (`Column(Integer, nullable=True)`), so DOCX documents store `NULL` instead of fabricated page numbers.
- Add `extracted_text = Column(Text, nullable=True)` to store the cleaned full text directly for Phase 4 consumption.
- Add `pages_json = Column(Text, nullable=True)` to store page-by-page structured text for the document reader.

---

## 5. Files to Create & Modify

### Files to Create
- `backend/app/services/document_validator.py`: File validation logic.
- `backend/app/services/file_storage.py`: Secure storage and SHA-256 hashing.
- `backend/app/services/pdf_extractor.py`: PyMuPDF extractor with empty text detection.
- `backend/app/services/docx_extractor.py`: python-docx extractor.
- `backend/app/services/document_extractor.py`: Unified extractor dispatcher.
- `backend/app/services/text_preprocessor.py`: Text cleaner and explainable legal tokenizer.
- `backend/app/services/document_processing_service.py`: Pipeline coordinator.
- `backend/tests/test_document_ingestion.py`: Comprehensive test suite for Phase 3.
- `sample_documents/sample_contract.pdf`: Realistic sample contract.
- `sample_documents/sample_legal_notice.docx`: Realistic sample legal notice.
- `docs/PHASE3_WALKTHROUGH.md`: Phase 3 verification report.

### Files to Modify
- `backend/requirements.txt`: Add `pymupdf`, `python-docx`, `python-multipart`.
- `backend/app/core/config.py`: Update `MAX_UPLOAD_SIZE_BYTES` to 10 MB.
- `backend/app/models/document.py`: Add `extracted_text` and `pages_json`, make `page_count` nullable.
- `backend/app/schemas/document.py`: Update `DocumentResponse`, add `DocumentTextResponse` and `UploadResponse`.
- `backend/app/api/v1/endpoints/documents.py`: Add `POST /upload` and `GET /{id}/text`.
- `frontend/src/services/api.js`: Add `uploadDocument` and `getDocumentText`.
- `frontend/src/pages/NewAnalysisPage.jsx`: Real upload form with progress, success status, and error display.
- `frontend/src/pages/DocumentViewerPage.jsx`: Retrieve and display extracted document text.
- `README.md`: Document Phase 3 capabilities and roadmap.

---

## 6. API Contracts

### 6.1 `POST /api/v1/documents/upload`
- **Request:** `multipart/form-data` with field `file`.
- **Response (201 Created):**
  ```json
  {
    "id": 1,
    "filename": "lease_agreement.pdf",
    "file_type": "pdf",
    "file_size": 183420,
    "page_count": 8,
    "word_count": 2147,
    "status": "completed",
    "message": "Document processed successfully."
  }
  ```

### 6.2 `GET /api/v1/documents/{id}/text`
- **Response (200 OK):**
  ```json
  {
    "document_id": 1,
    "filename": "lease_agreement.pdf",
    "page_count": 8,
    "word_count": 2147,
    "text": "Full extracted and preprocessed legal text...",
    "pages": [
      { "page_number": 1, "text": "Page 1 text..." }
    ]
  }
  ```

---

## 7. Test Plan

1. **Upload Validation Tests:**
   - Valid PDF upload succeeds.
   - Valid DOCX upload succeeds.
   - Unsupported file type (.txt, .exe) rejected with HTTP 400.
   - Oversized file (>10 MB) rejected with HTTP 413.
   - Empty file (0 bytes) rejected with HTTP 400.
2. **Text Extraction & Preprocessing Tests:**
   - PDF page count and text extracted correctly.
   - DOCX paragraphs and tables extracted correctly, `page_count is None`.
   - Word count calculated accurately.
   - Scanned PDF with no text handled gracefully with informative message.
   - Corrupt PDF / DOCX handled without crashing server.
3. **Database & API Tests:**
   - Record created in `documents` table with valid SHA-256 hash.
   - `GET /api/v1/documents/{id}` returns correct metadata.
   - `GET /api/v1/documents/{id}/text` returns extracted text and pages.
   - Physical storage path is not leaked in API responses.
4. **Frontend Verification:**
   - `npm run build` passes with zero errors.
   - UI upload flow works in browser.

---

## 8. Acceptance Criteria Checklist

- [ ] `pymupdf`, `python-docx`, `python-multipart` installed.
- [ ] Safe file storage with UUID naming and SHA-256 hashing.
- [ ] PyMuPDF text extractor preserves page numbering.
- [ ] python-docx extractor preserves paragraphs/tables, page_count is None.
- [ ] Text preprocessor preserves legal citation formats ("Section 10(2)", "Article 14", "Rs. 50,000").
- [ ] `POST /api/v1/documents/upload` works with validation and error handling.
- [ ] `GET /api/v1/documents/{id}/text` retrieves extracted text.
- [ ] Frontend upload page and basic text viewer functional.
- [ ] Fictional sample PDF and DOCX documents created in `sample_documents/`.
- [ ] All tests pass without regression to Phase 1 or Phase 2.
