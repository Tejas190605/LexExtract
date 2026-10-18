# Implementation Plan — Phase 2: LexExtract Backend Core + Database

**Project Title:** LexExtract – Legal Document Keyword Extractor  
**Phase:** Phase 2 – Backend Core & Database Foundation  
**Status:** In Progress / Ready for Execution  

---

## 1. Implementation Scope & Boundaries

### In-Scope (Phase 2)
- Integrate SQLAlchemy ORM with SQLite database engine (`backend/storage/lexextract.db`).
- Configure a robust session-per-request pattern via `get_db()` dependency.
- Create 6 normalized, practical relational models:
  1. `User` (with password_hash field placeholder, without auth logic)
  2. `Document` (with file metadata and lifecycle status definitions)
  3. `AnalysisRun` (lifecycle tracking for extraction runs)
  4. `ExtractedKeyword` (schema for RAKE/TF-IDF/Lexicon scores)
  5. `ExtractedEntity` (schema for legal entity offsets and categories)
  6. `AuditLog` (schema for compliance action records)
- Establish explicit foreign key constraints, indexes, and cascading relationships.
- Export all models cleanly from `app/models/__init__.py`.
- Build Pydantic response schemas ensuring `password_hash` is never exposed.
- Implement an idempotent database initialization and non-sensitive seed mechanism (`backend/scripts/init_db.py`).
- Implement minimal verification read endpoints:
  - `GET /api/v1/users`
  - `GET /api/v1/documents`
  - `GET /api/v1/analyses/{document_id}`
- Extend `GET /health` with a live database connectivity probe.
- Add comprehensive pytest database suite (`test_database.py`).
- Verify that Phase 1 frontend and smoke tests remain 100% operational.

### Explicitly Out-of-Scope (Deferred to Later Phases)
- Document processing, OCR, PyMuPDF, python-docx (Phase 3).
- NLP algorithms, RAKE, TF-IDF, legal dictionary matching (Phase 4).
- Legal entity extraction, spaCy, citation regex (Phase 5).
- Authentication, JWT, bcrypt password hashing, RBAC enforcement (Phase 6).
- Audit event generation service (Phase 6).
- Frontend dashboard, charts, upload UI, evaluation UI (Phases 7-9).

---

## 2. Database Design & Relational Schema

```
+-----------------------------------------------------------------------------------+
|                                  DATABASE SCHEMA                                  |
+-----------------------------------------------------------------------------------+

     +-----------------------+                    +-------------------------+
     |         users         |                    |       audit_logs        |
     +-----------------------+                    +-------------------------+
     | PK  id (Int)          |<-------+           | PK  id (Int)            |
     |     name (Str)        |        |           | FK  user_id (Int, Null) |
     | UQ  email (Str, Idx)  |        +-----------|     action (Str)        |
     |     password_hash(Str)|        |           | FK  document_id (Int)   |
     |     role (Str)        |        |           |     timestamp (DateTime)|
     |     is_active (Bool)  |        |           |     details (Str)       |
     |     created_at (DT)   |        |           +-------------------------+
     +-----------------------+        |                       ^
                 | 1                  |                       |
                 |                    +-----------------------+
                 | *                                          |
     +-----------------------+                                |
     |       documents       |                                |
     +-----------------------+                                |
     | PK  id (Int)          |--------------------------------+
     | FK  user_id (Int)     |
     |     filename (Str)    |
     |     stored_filename   |
     |     file_type (Str)   |
     |     file_size (Int)   |
     |     file_hash (Str)   |
     |     page_count (Int)  |
     |     word_count (Int)  |
     |     status (Str, Idx) |
     |     uploaded_at (DT)  |
     +-----------------------+
                 | 1
                 |
                 | *
     +-----------------------+
     |     analysis_runs     |
     +-----------------------+
     | PK  id (Int)          |
     | FK  document_id (Int) |
     |     status (Str)      |
     |     started_at (DT)   |
     |     completed_at (DT) |
     |     processing_time(F)|
     |     total_keywords(I) |
     |     total_entities(I) |
     +-----------------------+
           | 1             | 1
           |               |
           | *             | *
+--------------------+   +-----------------------+
| extracted_keywords |   |  extracted_entities   |
+--------------------+   +-----------------------+
| PK id (Int)        |   | PK id (Int)           |
| FK analysis_run_id |   | FK analysis_run_id    |
|    keyword (Str)   |   |    entity_text (Str)  |
|    category (Str)  |   |    entity_type (Str)  |
|    frequency (Int) |   |    frequency (Int)    |
|    rake_score (F)  |   |    page_number (Int)  |
|    tfidf_score (F) |   |    start_position (I) |
|    lexicon_score(F)|   |    end_position (I)   |
|    final_score (F) |   +-----------------------+
+--------------------+
```

---

## 3. Files to Create and Modify

### Files to Modify
- `backend/requirements.txt`: Add `SQLAlchemy>=2.0.0`
- `backend/app/core/config.py`: Add `DATABASE_URL` setting
- `backend/main.py`: Include database lifespan startup check, database health check in `/health`, and mount verification routes
- `backend/app/api/v1/router.py`: Include user, document, and analysis verification routers
- `README.md`: Update with Phase 2 capabilities and database instructions

### Files to Create
- `backend/app/core/database.py`: SQLAlchemy engine, sessionmaker, Base, and `get_db`
- `backend/app/models/user.py`: `User` ORM model
- `backend/app/models/document.py`: `Document` ORM model
- `backend/app/models/analysis.py`: `AnalysisRun` ORM model
- `backend/app/models/keyword.py`: `ExtractedKeyword` ORM model
- `backend/app/models/entity.py`: `ExtractedEntity` ORM model
- `backend/app/models/audit.py`: `AuditLog` ORM model
- `backend/app/models/__init__.py`: Clean model exports
- `backend/app/schemas/user.py`: Pydantic user request/response schemas (no password_hash leak)
- `backend/app/schemas/document.py`: Pydantic document schemas
- `backend/app/schemas/analysis.py`: Pydantic analysis, keyword, entity schemas
- `backend/app/schemas/evaluation.py`: Evaluation placeholder schema
- `backend/app/schemas/__init__.py`: Schema exports
- `backend/app/api/v1/endpoints/users.py`: Minimal read endpoint `GET /api/v1/users`
- `backend/app/api/v1/endpoints/documents.py`: Minimal read endpoint `GET /api/v1/documents`
- `backend/app/api/v1/endpoints/analysis.py`: Minimal read endpoint `GET /api/v1/analyses/{document_id}`
- `backend/scripts/init_db.py`: Standalone CLI script for database creation and idempotent seeding
- `backend/tests/test_database.py`: Unit and integration test suite for database and models
- `docs/PHASE2_WALKTHROUGH.md`: Phase 2 walkthrough and verification report

---

## 4. Verification Plan

1. **Dependency Installation:** Install `SQLAlchemy` into `.venv`.
2. **Schema & Models Verification:** Run `python scripts/init_db.py` to create `storage/lexextract.db` and seed demo records.
3. **Idempotency Check:** Run `python scripts/init_db.py` a second time to ensure no duplicate key errors or data duplication.
4. **Pytest Suite:** Execute `pytest backend/tests -v` covering table creation, constraints, cascades, foreign keys, and schema protections.
5. **Endpoint Verification:** Test live responses:
   - `GET /health` $\rightarrow$ verifies `{"database": "connected"}`
   - `GET /api/v1/users` $\rightarrow$ returns demo user, verifies no `password_hash` in JSON
   - `GET /api/v1/documents` $\rightarrow$ returns seed document metadata
   - `GET /api/v1/analyses/1` $\rightarrow$ returns empty list or analysis object
6. **Frontend Non-Regression:** Verify `npm run build` still passes with 0 errors and Phase 1 UI renders properly.
7. **Persistence Verification:** Verify data remains intact across application restarts.

---

## 5. Acceptance Criteria Checklist

- [ ] `backend/storage/lexextract.db` created using SQLite and SQLAlchemy ORM.
- [ ] Six models implemented with exact specifications: `User`, `Document`, `AnalysisRun`, `ExtractedKeyword`, `ExtractedEntity`, `AuditLog`.
- [ ] Foreign keys, indexes, and cascades configured appropriately.
- [ ] Pydantic response schemas enforce that `password_hash` is never exposed.
- [ ] Idempotent seed script creates demo records without duplication.
- [ ] Minimal verification read endpoints operational.
- [ ] Database health check reflected in `GET /health`.
- [ ] Automated tests pass (`test_health.py` and `test_database.py`).
- [ ] Existing Phase 1 UI and build remain completely unaffected.
- [ ] Zero premature NLP or authentication logic implemented.
- [ ] `docs/PHASE2_WALKTHROUGH.md` documented.
