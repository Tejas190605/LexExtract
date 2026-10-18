# LexExtract — Enterprise Systems (ES) Academic Syllabus Mapping

**Subject:** Enterprise Systems (ES)  
**Curriculum Domain:** Enterprise Architecture, Asynchronous Services, Relational Persistence & Security  
**Implementation System:** LexExtract Legal Document Analysis Engine

---

## 1. Executive Curriculum Alignment

This document details the mapping between the academic syllabus of **Enterprise Systems (ES)** and the architectural, cryptographic, and data-layer implementations in LexExtract.

---

## 2. Topic-by-Topic Syllabus Mapping

### 2.1 Multi-Tier Enterprise Architecture
- **Syllabus Concept:** Three-Tier Architecture, client-server decoupling, presentation, application logic, and persistence tier separation.
- **Where It Appears:** Complete system topology; [`docs/SYSTEM_ARCHITECTURE.md`](file:///c:/Users/tejas/PBL%20project%20(ES,ASTMA,ITPM)/docs/SYSTEM_ARCHITECTURE.md).
- **Why It Is Relevant:** Decouples presentation logic from computational processing, allowing independent scaling, testing, and deployment.
- **How It Works in LexExtract:**
  - **Presentation Tier:** React 18 SPA built with Vite and Tailwind CSS.
  - **Application Tier:** Asynchronous FastAPI REST service handling NLP, evaluation, and security.
  - **Data Tier:** SQLite relational persistence via SQLAlchemy 2.0 ORM and local file storage with SHA-256 integrity validation.

---

### 2.2 Asynchronous RESTful Web Services & Middleware
- **Syllabus Concept:** REST architectural principles, HTTP methods, status codes, asynchronous I/O event loops, and CORS middleware.
- **Where It Appears:** `backend/main.py`, `backend/app/api/v1/router.py`, endpoint routers.
- **Why It Is Relevant:** Prevents long-running file uploads and NLP processing from blocking concurrent client requests.
- **How It Works in LexExtract:**
  FastAPI uses Python's `asyncio` event loop. File uploads are streamed asynchronously (`await file.read()`). Endpoints return standard HTTP status codes (`200 OK`, `201 Created`, `400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`, `422 Unprocessable Entity`). CORS middleware strictly whitelists trusted presentation origins (`http://localhost:5173`).

---

### 2.3 Object-Relational Mapping (ORM) & Relational Schema Design
- **Syllabus Concept:** Relational database modeling, foreign keys, cascade deletes, indices, and ORM mapping.
- **Where It Appears:** `backend/app/models/`, `backend/app/core/database.py`.
- **Why It Is Relevant:** Abstracts low-level SQL syntax into type-safe object representations and decouples business logic from specific database engines.
- **How It Works in LexExtract:**
  Six normalized SQLAlchemy 2.0 models (`User`, `Document`, `AnalysisRun`, `ExtractedKeyword`, `ExtractedEntity`, `AuditLog`) enforce foreign key integrity and cascade deletions (`cascade="all, delete-orphan"`). Self-healing startup migrations dynamically add missing columns without data loss.

---

### 2.4 Cryptographic Security & Stateless Identity Management
- **Syllabus Concept:** Token-based authentication, symmetric key cryptography, password hashing, and salt generation.
- **Where It Appears:** `backend/app/core/security.py`, `backend/app/api/v1/endpoints/auth.py`.
- **Why It Is Relevant:** Protects user credentials and enables stateless authentication without server-side session memory overhead.
- **How It Works in LexExtract:**
  - **Password Hashing:** Passwords are encrypted using Argon2id (`pwdlib[argon2]`), a memory-hard hashing algorithm resistant to GPU cracking. Passwords are never stored in plaintext.
  - **Stateless Tokens:** RFC 7519 JSON Web Tokens (JWT) signed with HMAC-SHA256 (`HS256`) encode user ID and role claims with a 60-minute expiration period.

---

### 2.5 Role-Based Access Control (RBAC) & Least Privilege
- **Syllabus Concept:** Authorization models, role hierarchies, least-privilege access, and dependency injection guards.
- **Where It Appears:** `backend/app/core/roles.py`, `backend/app/core/deps.py`.
- **Why It Is Relevant:** Prevents unauthorized users from triggering resource-intensive operations or accessing administrative features.
- **How It Works in LexExtract:**
  Defines three discrete roles:
  - `USER`: Regular practitioner; uploads and analyzes personal documents.
  - `ANALYST`: Can access the ASTMA Evaluation Console and execute benchmarks.
  - `ADMIN`: Full system super-access, user management, and audit log inspection.
  Enforced via FastAPI dependency injection guards (`require_role`, `require_admin`).

---

### 2.6 Horizontal Data Isolation & Defense-in-Depth
- **Syllabus Concept:** Multi-tenant data segregation, preventing horizontal privilege escalation, and access control lists.
- **Where It Appears:** `backend/app/core/deps.py:check_document_access()`.
- **Why It Is Relevant:** Prevents a malicious authenticated user from viewing or deleting another user's confidential legal documents by guessing document IDs.
- **How It Works in LexExtract:**
  Every document, text extraction, analysis, and file download request executes an ownership verification check:
  $$\text{Access Granted } \iff (\text{doc.owner\_id} == \text{current\_user.id}) \lor (\text{current\_user.role} == \text{'ADMIN'})$$
  Cross-user access attempts return HTTP 403 Forbidden and record an `UNAUTHORIZED_ACCESS` entry in the audit ledger.

---

### 2.7 Non-Repudiation Security & Institutional Audit Logging
- **Syllabus Concept:** System observability, immutable audit trails, non-repudiation, and security compliance.
- **Where It Appears:** `backend/app/models/audit.py`, `backend/app/services/audit_service.py`, `backend/app/api/v1/endpoints/admin.py`.
- **Why It Is Relevant:** Provides a permanent, tamper-evident record of user and administrative actions for regulatory compliance.
- **How It Works in LexExtract:**
  The `AuditLog` table permanently records operations (`LOGIN`, `DOCUMENT_UPLOAD`, `ANALYSIS_START`, `ANALYSIS_COMPLETE`, `UNAUTHORIZED_ACCESS`) with actor ID, status (`SUCCESS` / `FAILURE`), client IP address, and timestamp. Passwords, secret keys, and JWT tokens are strictly redacted from audit records.
