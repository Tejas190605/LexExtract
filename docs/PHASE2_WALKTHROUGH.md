# Phase 2 Walkthrough — Backend Core & Database Foundation

**Project Title:** LexExtract – Legal Document Keyword Extractor  
**Phase:** Phase 2 – Backend Core & Database Foundation  
**Status:** Completed & 100% Verified  

---

## 1. Summary of What Was Created & Modified

### Database Module & Configuration
- **`backend/app/core/database.py`**:
  - Configured SQLite connection with `check_same_thread=False` for thread safety.
  - SQLAlchemy `engine` targeting `backend/storage/lexextract.db`.
  - `SessionLocal` sessionmaker.
  - Declarative `Base = declarative_base()`.
  - `get_db()` dependency generator providing session-per-request lifecycle.
  - `init_db()` idempotent schema creator.
  - `check_db_connection()` connectivity probe.
- **`backend/app/core/config.py`**:
  - Added `DATABASE_URL` and `STORAGE_DIR` settings.

### Relational Data Models (6 Core Models)
All 6 models are defined and cleanly exported in `backend/app/models/__init__.py`:
1. **`User` (`backend/app/models/user.py`)**:
   - Fields: `id`, `name`, `email` (unique index), `password_hash` (placeholder for Phase 6), `role`, `is_active`, `created_at`.
   - Relationships: `documents` (cascade="all, delete-orphan"), `audit_logs` (cascade="all, delete-orphan").
2. **`Document` (`backend/app/models/document.py`)**:
   - Fields: `id`, `user_id` (FK), `filename`, `stored_filename`, `file_type`, `file_size`, `file_hash` (SHA-256), `page_count`, `word_count`, `status` (indexed), `uploaded_at`.
   - Relationships: `user`, `analysis_runs` (cascade="all, delete-orphan"), `audit_logs`.
3. **`AnalysisRun` (`backend/app/models/analysis.py`)**:
   - Fields: `id`, `document_id` (FK), `status`, `started_at`, `completed_at`, `processing_time`, `total_keywords`, `total_entities`.
   - Relationships: `document`, `keywords` (cascade="all, delete-orphan"), `entities` (cascade="all, delete-orphan").
4. **`ExtractedKeyword` (`backend/app/models/keyword.py`)**:
   - Fields: `id`, `analysis_run_id` (FK), `keyword`, `category`, `frequency`, `rake_score`, `tfidf_score`, `lexicon_score`, `final_score`.
   - Relationships: `analysis_run`.
5. **`ExtractedEntity` (`backend/app/models/entity.py`)**:
   - Fields: `id`, `analysis_run_id` (FK), `entity_text`, `entity_type`, `frequency`, `page_number`, `start_position`, `end_position`.
   - Relationships: `analysis_run`.
6. **`AuditLog` (`backend/app/models/audit.py`)**:
   - Fields: `id`, `user_id` (FK, nullable), `action`, `document_id` (FK, nullable), `timestamp`, `details`.
   - Relationships: `user`, `document`.

### Pydantic Data Contracts (`backend/app/schemas/`)
- **`user.py`**: `UserBase`, `UserCreate`, `UserResponse`.
  - **CRITICAL SECURITY MEASURE:** `password_hash` is completely excluded from `UserResponse`.
- **`document.py`**: `DocumentBase`, `DocumentCreate`, `DocumentResponse`.
- **`analysis.py`**: `KeywordResponse`, `EntityResponse`, `AnalysisRunResponse`.
- **`evaluation.py`**: `EvaluationMetrics` (placeholder contract for Phase 9).
- **`__init__.py`**: Clean package exports.

### Verification Endpoints & Routing
- **`backend/app/api/v1/endpoints/users.py`**: `GET /api/v1/users/`, `GET /api/v1/users/{id}`.
- **`backend/app/api/v1/endpoints/documents.py`**: `GET /api/v1/documents/`, `GET /api/v1/documents/{id}`.
- **`backend/app/api/v1/endpoints/analysis.py`**: `GET /api/v1/analyses/document/{document_id}`, `GET /api/v1/analyses/{analysis_id}`.
- **`backend/app/api/v1/router.py`**: Mounted users, documents, and analysis routers.
- **`backend/main.py`**:
  - Added async `lifespan` context manager calling `init_db()` upon startup.
  - Enhanced `GET /health` with live `database: connected` status.

### Database Initialization & Seed Script
- **`backend/scripts/init_db.py`**:
  - Initializes schema idempotently.
  - Seeds non-sensitive demo user: `demo@lexextract.local` (`Demo User`, role `user`).
  - Seeds sample document metadata: `sample_commercial_lease.pdf`.
  - Safe to re-run multiple times without duplicate key errors.

---

## 2. Commands Executed

```powershell
# 1. Added SQLAlchemy to requirements.txt & installed
pip install -r requirements.txt

# 2. Executed database initialization & seed script
python scripts/init_db.py

# 3. Verified idempotency by re-executing
python scripts/init_db.py

# 4. Executed full pytest test suite (15 tests)
pytest -v

# 5. Verified frontend production build (no regression)
cd ../frontend
npm run build

# 6. Live API probe using PowerShell
Invoke-RestMethod -Uri http://127.0.0.1:8000/health
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/v1/users
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/v1/documents
```

---

## 3. Test & Verification Results

### Automated Pytest Suite (`15 / 15 Passed`)
```
tests/test_database.py::test_tables_created PASSED                       [  6%]
tests/test_database.py::test_user_creation_and_unique_email PASSED       [ 13%]
tests/test_database.py::test_document_referencing_user PASSED            [ 20%]
tests/test_database.py::test_analysis_run_keyword_and_entity_relationship PASSED [ 26%]
tests/test_database.py::test_audit_log_referencing_user PASSED           [ 33%]
tests/test_database.py::test_password_hash_never_exposed_in_user_response PASSED [ 40%]
tests/test_database.py::test_api_health_check_database_status PASSED     [ 46%]
tests/test_database.py::test_api_list_users_omits_password_hash PASSED   [ 53%]
tests/test_database.py::test_api_list_documents PASSED                   [ 60%]
tests/test_database.py::test_api_analysis_not_found PASSED               [ 66%]
tests/test_database.py::test_cascade_delete_document_removes_runs PASSED [ 73%]
tests/test_database.py::test_api_get_single_document_by_id PASSED        [ 80%]
tests/test_health.py::test_root_endpoint PASSED                          [ 86%]
tests/test_health.py::test_health_endpoint PASSED                        [ 93%]
tests/test_api_v1_info_endpoint PASSED                                   [100%]

======================== 15 passed in 2.16s ========================
```

### Live Endpoint Outputs
1. **`GET /health`**:
   ```json
   {
     "status": "healthy",
     "database": "connected",
     "application": "LexExtract",
     "environment": "development",
     "version": "0.1.0"
   }
   ```
2. **`GET /api/v1/users`** (Proves NO password hash exposure):
   ```json
   [
     {
       "id": 1,
       "name": "Demo User",
       "email": "demo@lexextract.local",
       "role": "user",
       "is_active": true,
       "created_at": "2026-10-04T18:08:55"
     }
   ]
   ```
3. **`GET /api/v1/documents`**:
   ```json
   [
     {
       "id": 1,
       "user_id": 1,
       "filename": "sample_commercial_lease.pdf",
       "stored_filename": "doc_seed_sample_lease.pdf",
       "file_type": "pdf",
       "file_size": 1048576,
       "file_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
       "page_count": 5,
       "word_count": 2450,
       "status": "uploaded",
       "uploaded_at": "2026-10-04T18:08:55"
     }
   ]
   ```

### Frontend Build Verification (`frontend/`)
```
✓ 1547 modules transformed.
dist/index.html                   0.94 kB
dist/assets/index-BljnIMbc.css   13.64 kB
dist/assets/index-Ca10dfx9.js   222.11 kB
✓ built in 18.07s (0 errors)
```

---

## 4. Phase 2 Acceptance Criteria Verification Checklist

| Criterion | Target | Status | Verification Evidence |
| :--- | :--- | :---: | :--- |
| **SQLite DB Created** | `backend/storage/lexextract.db` | **VERIFIED** | Present and verified via sqlite3 |
| **SQLAlchemy Engine & Session** | `get_db()` session-per-request | **VERIFIED** | Thread-safe connection & generator dependency |
| **Six Relational Models** | `User`, `Document`, `AnalysisRun`, `Keyword`, `Entity`, `Audit` | **VERIFIED** | Fully defined with FKs and indexes |
| **Foreign Keys & Cascades** | Document delete cascades to runs/keywords/entities | **VERIFIED** | Tested via `test_cascade_delete_document_removes_runs` |
| **Pydantic Schemas** | Response schemas for all models | **VERIFIED** | In `app/schemas/` |
| **Password Hash Never Exposed** | Zero leakage in `UserResponse` | **VERIFIED** | Tested unit-level and API-level |
| **Seed Script** | Repeatable non-sensitive seed | **VERIFIED** | `python scripts/init_db.py` tested twice idempotently |
| **Verification APIs** | Users, Documents, Analysis endpoints | **VERIFIED** | Responding with HTTP 200 and typed JSON |
| **Database Health Probe** | Extended `/health` endpoint | **VERIFIED** | Live output confirms `"database": "connected"` |
| **Database Tests** | Automated pytest coverage | **VERIFIED** | 15/15 passed |
| **Frontend Non-Regression** | Phase 1 UI and Vite build intact | **VERIFIED** | `npm run build` succeeds in 18s |
| **Scope Control** | Zero premature NLP/Auth logic | **VERIFIED** | Confirmed no Phase 3+ code introduced |

---

## 5. How Phase 3 Will Use This Foundation
In **Phase 3 (Document Ingestion & Text Processing)**:
1. File uploads (`.pdf`, `.docx`) will compute SHA-256 hashes and save binary streams to `backend/storage/uploads/`.
2. PyMuPDF and python-docx text extractors will extract page counts and word counts.
3. The extracted metadata will directly instantiate and persist `Document` records in `storage/lexextract.db` using the `get_db()` dependency established in Phase 2.
