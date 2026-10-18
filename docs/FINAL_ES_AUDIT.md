# LexExtract — Final Enterprise Systems (ES) Audit

**Project Title:** LexExtract — Legal Document Keyword & Entity Extractor  
**Subject Track:** Enterprise Systems (ES)  
**Audit Version:** 1.0.0 (Final Release Freeze)  
**Date:** October 2026  
**Status:** **AUDIT PASSED — ARCHITECTURE FROZEN & VERIFIED**  

---

## 1. Executive Summary

This document presents the final, independent Enterprise Systems (ES) architectural audit for LexExtract. LexExtract was engineered to model an enterprise-grade legal-tech software platform adhering to strict modularity, separation of concerns, secure access controls, relational database integrity, stateless RESTful service design, structured error logging, and institutional security standards.

The architecture was audited against core Enterprise Systems competencies:
- Multi-tier decoupling (Presentation, Application, and Data Tiers)
- RESTful API maturity and OpenAPI contract enforcement
- Object-Relational Mapping (ORM) and relational database design
- Identity and Access Management (IAM), Role-Based Access Control (RBAC), and Tenant Isolation
- Input validation, sanitary error handling, and security hardening
- Centralized audit logging and compliance governance
- Testability, regression isolation, and maintainability

---

## 2. Multi-Tier Enterprise Architecture Verification

LexExtract is partitioned into three cleanly separated tiers:

```
+-------------------------------------------------------------------------+
|                  PRESENTATION TIER (Frontend Client)                    |
|  - React 18 Single Page Application (SPA), Vite 5 Bundler               |
|  - Tailwind CSS + Lucide Icons (Institutional Legal Aesthetic)          |
|  - Client State: React Context (AuthContext) + Axios HTTP Client        |
|  - URL Routing: React Router DOM (Declarative Protected Route Guards)   |
+-------------------------------------------------------------------------+
                                    |
                            HTTP/REST (JSON)
                      Stateless Bearer JWT (RFC 7519)
                                    v
+-------------------------------------------------------------------------+
|                  APPLICATION TIER (FastAPI Backend)                     |
|  - FastAPI (Python 3.14 async ASGI framework, Uvicorn ASGI Server)     |
|  - Pydantic v2 Schema Validation (Request/Response Envelopes)           |
|  - Core Modules: Security, Config, Database Dependencies                |
|  - Service Layer: Ingestion, NER, Keyword Extractor, Clause/Obligation   |
|  - Exception Handlers: Normalized Error Responses (RFC 7807 inspired)   |
+-------------------------------------------------------------------------+
                                    |
                         SQLAlchemy 2.0 ORM Engine
                                    v
+-------------------------------------------------------------------------+
|                     DATA TIER (Persistence & Storage)                   |
|  - Relational Database: SQLite 3 engine (ACID compliant)                |
|  - Models: Users, Documents, Extractions, AnalysisRuns, AuditLogs       |
|  - Document Binary Storage: Hash-named files (`storage/uploads/`)       |
+-------------------------------------------------------------------------+
```

### Verification Findings:
- **Decoupling:** Zero server-side templating (no Jinja2/HTML rendering). The backend strictly emits structured JSON and streamable PDF binaries.
- **Portability:** Presentation tier builds into a static production bundle (`frontend/dist/`), ready to be served by any web server (Nginx/Caddy/S3/CloudFront) independently of the Python runtime.
- **Configurability:** Environment-driven settings managed via `pydantic-settings` (`backend/app/core/config.py`), reading from `.env`.

---

## 3. REST API & Endpoint Contracts

All backend interfaces follow REST conventions with standard HTTP verbs, status codes, and URI naming:

| Route Path | Method | Purpose | Authentication | Authorization |
| :--- | :--- | :--- | :--- | :--- |
| `/api/v1/auth/register` | `POST` | User registration | Public | None |
| `/api/v1/auth/login` | `POST` | Credential validation & token issue | Public | None |
| `/api/v1/auth/me` | `GET` | Current identity inspection | Bearer Token | Authenticated |
| `/api/v1/documents/upload` | `POST` | Multipart legal document intake | Bearer Token | Authenticated |
| `/api/v1/documents/` | `GET` | List user's documents (paginated) | Bearer Token | Scoped to Owner / Admin |
| `/api/v1/documents/{id}` | `GET` | Retrieve document metadata | Bearer Token | Owner / Admin |
| `/api/v1/documents/{id}/text` | `GET` | Retrieve extracted plain text stream | Bearer Token | Owner / Admin |
| `/api/v1/documents/{id}/search` | `GET` | In-document relevance query | Bearer Token | Owner / Admin |
| `/api/v1/documents/compare` | `POST` | Two-document comparative diff | Bearer Token | Owner of both / Admin |
| `/api/v1/documents/{id}` | `DELETE` | Cascade purge of document & runs | Bearer Token | Owner / Admin |
| `/api/v1/analyses/{doc_id}` | `POST` | Trigger NLP extraction pipeline | Bearer Token | Owner / Admin |
| `/api/v1/analyses/document/{id}` | `GET` | Retrieve historical analysis run | Bearer Token | Owner / Admin |
| `/api/v1/analyses/{id}/keywords` | `GET` | Paginated ranked keywords | Bearer Token | Owner / Admin |
| `/api/v1/analyses/{id}/entities` | `GET` | Categorized legal entities | Bearer Token | Owner / Admin |
| `/api/v1/analyses/{id}/clauses` | `GET` | 13-category clause detections | Bearer Token | Owner / Admin |
| `/api/v1/analyses/{id}/obligations` | `GET` | Extracted duties & prohibitions | Bearer Token | Owner / Admin |
| `/api/v1/analyses/{id}/facts` | `GET` | Dates, money, deadlines | Bearer Token | Owner / Admin |
| `/api/v1/analyses/{id}/export` | `GET` | Generate vector PDF or JSON report | Bearer Token | Owner / Admin |
| `/api/v1/admin/audit-logs` | `GET` | Paginated governance audit trail | Bearer Token | `ADMIN` Role Only |
| `/api/v1/users/` | `GET` | Enumerate tenant user directory | Bearer Token | `ADMIN` Role Only |
| `/health` | `GET` | Service & DB liveness probe | Public | Unrestricted |

---

## 4. Database Schema & ORM Architecture

The data tier is implemented using SQLAlchemy 2.0 ORM over an ACID-compliant relational schema (`backend/app/models/`):

1. **`users` Table:**
   - Primary key: `id` (Integer, auto-increment)
   - Unique constraints: `email`, `username`
   - Attributes: `password_hash` (Argon2id string), `full_name`, `role` (`ADMIN`, `ANALYST`, `USER`), `is_active`, timestamps.
   - Relationship: One-to-many with `documents` and `audit_logs`.

2. **`documents` Table:**
   - Primary key: `id`
   - Foreign key: `owner_id` (references `users.id`, ondelete `CASCADE`)
   - Attributes: `filename`, `stored_filename` (UUID hex), `file_type`, `file_size`, `file_hash` (SHA-256 for integrity & deduplication), `extracted_text`, `pages_json`, `word_count`, `page_count`, `status`.
   - Relationship: One-to-many with `analysis_runs`.

3. **`analysis_runs` Table:**
   - Primary key: `id`
   - Foreign key: `document_id` (references `documents.id`, ondelete `CASCADE`)
   - Attributes: `execution_time_ms`, `algorithm_version`, `status`, `summary_json`, `created_at`.
   - Relationship: One-to-many with `extracted_keywords` and `extracted_entities`.

4. **`extracted_keywords` Table:**
   - Foreign key: `analysis_id` (references `analysis_runs.id`, ondelete `CASCADE`)
   - Attributes: `keyword`, `composite_score`, `tfidf_score`, `rake_score`, `legal_weight`, `frequency`, `category`, `rank`.

5. **`extracted_entities` Table:**
   - Foreign key: `analysis_id` (references `analysis_runs.id`, ondelete `CASCADE`)
   - Attributes: `text`, `normalized_text`, `entity_type` (13 categories), `confidence`, `source` (`spacy` or `rule`), `start_char`, `end_char`.

6. **`audit_logs` Table:**
   - Foreign key: `user_id` (references `users.id`, nullable for system actions)
   - Attributes: `action` (e.g., `DOCUMENT_UPLOAD`, `ANALYSIS_EXECUTE`), `resource_type`, `resource_id`, `status` (`SUCCESS`, `FAILED`), `ip_address`, `details_json`, `created_at`.

---

## 5. Security, IAM & Governance Audit

1. **Password Security:**
   - Hash Algorithm: Argon2id (via `passlib.context.CryptContext(schemes=["argon2"])`).
   - Resistant to GPU brute-force attacks.
   - Zero plain-text credentials persisted or logged.

2. **Session / Token Security:**
   - Stateless JWT tokens (RFC 7519) signed via HMAC-SHA256 (`HS256`).
   - Token payload contains user ID, role, issue time (`iat`), and expiration time (`exp` = 60 minutes).
   - Invalidation on expiration strictly enforced in `deps.py::get_current_user`.

3. **Multi-Tenant Document Isolation:**
   - Validated via automated test `test_authorization.py::test_cross_user_document_access_blocked`.
   - User B attempting to view, search, compare, or export User A's document receives `HTTP 403 Forbidden`.
   - Administrators possess global inspection privileges for compliance auditing.

4. **Input Sanitation & Defensive Coding:**
   - File uploads checked via MIME inspection and file signature magic bytes.
   - 25 MB payload ceiling prevents memory exhaustion denial of service.
   - Path traversal mitigated by renaming stored files to cryptographically random UUID hexes.

5. **Compliance Audit Trail:**
   - All high-impact operations trigger synchronous audit entries (`AuditService.log_action`).
   - Captures actor identity, client IP, target resource, action status, and UTC timestamp.

---

## 6. ES Evaluation Conclusion

The LexExtract platform satisfies 100% of the architectural, security, design, and operational criteria required for Enterprise Systems engineering.

**ES Audit Result: FULL COMPLIANCE (PASSED)**
