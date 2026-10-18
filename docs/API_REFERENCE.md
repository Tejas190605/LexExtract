# LexExtract — RESTful API Reference Specification

Interactive OpenAPI Swagger UI is available at `http://127.0.0.1:8000/docs`. ReDoc documentation is available at `http://127.0.0.1:8000/redoc`.

---

## 1. System Health & Diagnostics

### `GET /health`
- **Purpose:** Operational probe verifying service uptime and relational database connectivity.
- **Authentication:** Public (No token required).
- **Response `200 OK`:**
  ```json
  {
    "status": "healthy",
    "database": "connected",
    "application": "LexExtract",
    "environment": "development",
    "version": "0.1.0"
  }
  ```

### `GET /api/v1/`
- **Purpose:** Architecture and API discovery endpoint.
- **Authentication:** Public.
- **Response `200 OK`:**
  ```json
  {
    "status": "online",
    "api_version": "v1",
    "application": "LexExtract",
    "phase": "Phase 9 - Final Integration, Deployment, QA & Project Readiness",
    "architecture": "Three-Tier Enterprise Architecture (Presentation, Application, Data)",
    "security": "Stateless RFC 7519 JWT (HS256) + Argon2id Password Hashing + RBAC + Audit Ledger"
  }
  ```

---

## 2. Authentication & Identity (`/api/v1/auth`)

### `POST /api/v1/auth/register`
- **Purpose:** Register a new user account (defaults to `USER` role).
- **Authentication:** Public.
- **Request Body (`application/json`):**
  ```json
  {
    "email": "lawyer@firm.com",
    "username": "counsel_advocate",
    "full_name": "Advocate Sharma",
    "password": "SecurePassword2026!"
  }
  ```
- **Response `201 Created`:**
  ```json
  {
    "id": 4,
    "email": "lawyer@firm.com",
    "username": "counsel_advocate",
    "full_name": "Advocate Sharma",
    "role": "USER",
    "is_active": true,
    "created_at": "2026-10-05T12:00:00Z"
  }
  ```
- **Error Responses:** `400 Bad Request` (Duplicate email/username), `422 Unprocessable Entity` (Password < 8 characters).

### `POST /api/v1/auth/login`
- **Purpose:** Authenticate credentials and issue a signed RFC 7519 JWT access token.
- **Authentication:** Public.
- **Request Body (`application/x-www-form-urlencoded` or JSON):**
  ```json
  {
    "username": "demo@lexextract.local",
    "password": "User@Lex2026!"
  }
  ```
- **Response `200 OK`:**
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
      "id": 1,
      "email": "demo@lexextract.local",
      "username": "lawyer_user",
      "full_name": "Demonstration Lawyer",
      "role": "USER",
      "is_active": true
    }
  }
  ```
- **Error Responses:** `401 Unauthorized` (Invalid credentials or inactive account).

### `GET /api/v1/auth/me`
- **Purpose:** Retrieve the authenticated user's profile.
- **Authentication:** Bearer JWT required.
- **Response `200 OK`:** User profile object.
- **Error Responses:** `401 Unauthorized` (Missing, invalid, or expired token).

---

## 3. Document Ingestion & Storage (`/api/v1/documents`)

### `POST /api/v1/documents/upload`
- **Purpose:** Upload, validate, and extract text from a legal brief (.pdf or .docx).
- **Authentication:** Bearer JWT required.
- **Request Body (`multipart/form-data`):**
  - `file`: Binary file stream (max 25 MB).
- **Response `201 Created`:**
  ```json
  {
    "id": 12,
    "filename": "commercial_lease.pdf",
    "file_type": "pdf",
    "file_size": 1048576,
    "page_count": 5,
    "word_count": 2450,
    "status": "uploaded",
    "created_at": "2026-10-05T12:05:00Z"
  }
  ```
- **Error Responses:** `400 Bad Request` (Empty file, corrupt stream, or unsupported file type).

### `GET /api/v1/documents/`
- **Purpose:** List documents owned by the authenticated user (or all documents if admin).
- **Authentication:** Bearer JWT required.
- **Response `200 OK`:** Array of document summary objects.

### `GET /api/v1/documents/{id}`
- **Purpose:** Retrieve document metadata.
- **Authentication:** Bearer JWT required (enforces ownership isolation).
- **Response `200 OK`:** Document metadata object.
- **Error Responses:** `403 Forbidden` (User does not own document), `404 Not Found`.

### `GET /api/v1/documents/{id}/text`
- **Purpose:** Retrieve full extracted plain text and page segment array.
- **Authentication:** Bearer JWT required (enforces ownership isolation).
- **Response `200 OK`:**
  ```json
  {
    "document_id": 12,
    "filename": "commercial_lease.pdf",
    "word_count": 2450,
    "extracted_text": "COMMERCIAL LEASE AGREEMENT...",
    "pages": [
      {"page_number": 1, "text": "..."},
      {"page_number": 2, "text": "..."}
    ]
  }
  ```
- **Error Responses:** `403 Forbidden`, `404 Not Found`.

### `GET /api/v1/documents/{id}/file`
- **Purpose:** Download or stream the original binary file.
- **Authentication:** Bearer JWT or query param `?token=...`.
- **Response `200 OK`:** Binary file stream (`application/pdf` or `.docx`).
- **Error Responses:** `403 Forbidden`, `404 Not Found`.

---

## 4. NLP Analysis, Keywords & Entities (`/api/v1/analyses`)

### `POST /api/v1/analyses/{document_id}`
- **Purpose:** Trigger the hybrid keyword and legal entity extraction pipeline.
- **Authentication:** Bearer JWT required (enforces ownership isolation).
- **Response `200 OK`:**
  ```json
  {
    "analysis_id": 8,
    "document_id": 12,
    "status": "completed",
    "total_keywords": 20,
    "total_entities": 32,
    "processing_time": 0.824
  }
  ```
- **Error Responses:** `400 Bad Request` (Document has no extracted text), `403 Forbidden`, `404 Not Found`.

### `GET /api/v1/analyses/{analysis_id}`
- **Purpose:** Retrieve analysis run summary and metadata.
- **Authentication:** Bearer JWT required (enforces ownership isolation).
- **Response `200 OK`:** Analysis summary object.

### `GET /api/v1/analyses/{analysis_id}/keywords`
- **Purpose:** Retrieve ranked legal keywords with optional category and limit filters.
- **Authentication:** Bearer JWT required (enforces ownership isolation).
- **Query Parameters:**
  - `category` (optional): Filter by domain category (`Contract`, `Litigation`, etc.).
  - `limit` (default: 20): Maximum keywords to return (1–100).
- **Response `200 OK`:**
  ```json
  {
    "analysis_id": 8,
    "total": 20,
    "keywords": [
      {
        "id": 101,
        "keyword": "liquidated damages",
        "final_score": 0.8421,
        "category": "Contract",
        "frequency": 4,
        "rank": 1,
        "tfidf_score": 0.78,
        "rake_score": 0.88,
        "lexicon_score": 1.0
      }
    ]
  }
  ```

### `GET /api/v1/analyses/{analysis_id}/entities`
- **Purpose:** Retrieve extracted typed legal entities with optional type and limit filters.
- **Authentication:** Bearer JWT required (enforces ownership isolation).
- **Query Parameters:**
  - `type` (optional): Filter by legal entity category (`COURT`, `STATUTE`, etc.).
  - `limit` (default: 50): Maximum entities to return (1–200).
- **Response `200 OK`:**
  ```json
  {
    "analysis_id": 8,
    "total": 32,
    "entities": [
      {
        "id": 201,
        "entity_text": "Supreme Court of India",
        "normalized_text": "supreme court of india",
        "entity_type": "COURT",
        "confidence": 0.98,
        "source": "hybrid",
        "start_position": 142,
        "end_position": 164
      }
    ]
  }
  ```

---

## 5. ASTMA Evaluation & Benchmarking (`/api/v1/evaluation`)

### `GET /api/v1/evaluation/summary`
- **Purpose:** Retrieve overall summary metrics across the 12-document benchmark corpus.
- **Authentication:** Role `ANALYST` or `ADMIN` required.
- **Response `200 OK`:**
  ```json
  {
    "corpus_size": 12,
    "total_words": 3875,
    "avg_doc_processing_time_ms": 824.0,
    "keyword_metrics": {
      "macro_precision": 0.125,
      "macro_recall": 0.2237,
      "macro_f1": 0.1599,
      "micro_precision": 0.125,
      "micro_recall": 0.2326,
      "micro_f1": 0.1626
    },
    "entity_metrics": {
      "macro_precision": 0.3833,
      "macro_recall": 0.6899,
      "macro_f1": 0.4893
    }
  }
  ```

### `GET /api/v1/evaluation/documents`
- **Purpose:** Retrieve per-document evaluation records.
- **Authentication:** Role `ANALYST` or `ADMIN` required.
- **Response `200 OK`:** Array of 12 document evaluation records.

### `GET /api/v1/evaluation/errors`
- **Purpose:** Retrieve classified False Positives, False Negatives, and Type Mismatches.
- **Authentication:** Role `ANALYST` or `ADMIN` required.
- **Response `200 OK`:** Error taxonomy object.

### `POST /api/v1/evaluation/run`
- **Purpose:** Execute a live ASTMA benchmark evaluation across all 12 documents.
- **Authentication:** Role `ANALYST` or `ADMIN` required (`USER` returns HTTP 403 Forbidden).
- **Response `200 OK`:** Complete benchmark evaluation report.

---

## 6. Institutional Governance & Administration (`/api/v1/admin`)

### `GET /api/v1/admin/audit-logs`
- **Purpose:** Retrieve paginated non-repudiation audit records.
- **Authentication:** Role `ADMIN` required (`USER` and `ANALYST` return HTTP 403 Forbidden).
- **Query Parameters:** `limit` (default: 50), `offset` (default: 0), `action`, `status`.
- **Response `200 OK`:**
  ```json
  {
    "total": 173,
    "limit": 50,
    "offset": 0,
    "logs": [
      {
        "id": 173,
        "user_id": 1,
        "action": "ANALYSIS_COMPLETE",
        "resource_type": "ANALYSIS",
        "resource_id": 8,
        "status": "SUCCESS",
        "details": "Analysis completed: 20 keywords, 32 entities in 0.824s",
        "ip_address": "127.0.0.1",
        "timestamp": "2026-10-05T12:10:00Z"
      }
    ]
  }
  ```
