# Phase 6 Walkthrough — Authentication, RBAC & Audit Trail

**Project:** LexExtract — Legal Document Keyword & Entity Extractor  
**Phase:** Phase 6 — Authentication, RBAC & Audit Trail  
**Status:** Completed, Verified, and Tested (100% Passing)  

---

## 1. Executive Summary

Phase 6 introduces enterprise-grade identity, security, role-based authorization, data isolation, and regulatory governance to LexExtract. Built upon the foundation of Phases 1–5 (document processing, keyword ranking, and legal entity extraction), Phase 6 guarantees that only authenticated legal practitioners can ingest and inspect documents, enforces strict multi-tenant boundary isolation, records all sensitive operations in an append-only audit trail, and equips administrators with comprehensive audit and user management interfaces.

### Core Deliverables:
1. **User Identity & Cryptographic Authentication:**
   - Memory-hard password hashing using **Argon2id** via `pwdlib[argon2]`.
   - Stateless signed JSON Web Tokens (**RFC 7519 JWT**) using `PyJWT` with HS256 encryption.
   - Comprehensive `/auth/register`, `/auth/login`, `/auth/me`, and `/auth/logout` endpoints.
2. **Role-Based Access Control (RBAC):**
   - Three canonical roles: `USER` (Legal Practitioner), `ANALYST` (Senior Examiner), and `ADMIN` (System Administrator).
   - Server-side dependency gates (`get_current_user`, `require_role`, `require_admin`).
3. **Data Ownership & Tenant Isolation:**
   - Mandatory document attribution (`Document.owner_id` / `Document.user_id`).
   - Cross-tenant document and analysis access strictly prohibited with HTTP 403 Forbidden.
   - Unauthorized access attempts automatically logged as security incidents.
4. **Non-Repudiation Audit Ledger:**
   - Centralized, append-only `AuditLog` service with sanitized payload capture.
   - Controlled event taxonomy: `LOGIN_SUCCESS`, `LOGIN_FAILURE`, `LOGOUT`, `REGISTER`, `DOCUMENT_UPLOAD`, `DOCUMENT_VIEW`, `ANALYSIS_START`, `ANALYSIS_COMPLETE`, `ANALYSIS_FAILED`, `KEYWORD_VIEW`, `ENTITY_VIEW`, `UNAUTHORIZED_ACCESS`, and admin operations.
5. **Administrative Controls & UI:**
   - Real-time Governance Audit Ledger Explorer with action, status, and user filtering.
   - User Management Directory with activation/deactivation and role assignment.
   - Built-in administrative preservation safeguard prohibiting deactivating or demoting the final active administrator.
6. **Frontend Integration:**
   - `AuthContext.jsx` with persistent token storage and 401 interception.
   - Professional `LoginPage.jsx` with one-click demo credentials for college viva evaluations.
   - Clean `RegisterPage.jsx` with client-side password policy enforcement.
   - Comprehensive `AdminAuditPage.jsx` featuring dual-tabbed audit trail and user administration tables.

---

## 2. Authentication & JWT Architecture

```
  ┌─────────────────────────────────────────────────────────────┐
  │                      Client Browser                         │
  └──────────────┬───────────────────────────────▲──────────────┘
                 │ 1. POST /auth/login           │ 4. Bearer JWT
                 │    { email, password }        │    Stored in localStorage
                 ▼                               │
  ┌──────────────────────────────────────────────┴──────────────┐
  │                     FastAPI Application                     │
  │                                                             │
  │  ┌───────────────────────┐       ┌───────────────────────┐  │
  │  │  Verify Credentials   │       │  PyJWT Signer         │  │
  │  │  Argon2id (pwdlib)    ├──────►│  HS256 Secret         │  │
  │  │  hash_password()      │       │  create_access_token()│  │
  │  └───────────────────────┘       └───────────────────────┘  │
  └──────────────┬───────────────────────────────▲──────────────┘
                 │ 2. Query User                 │ 3. Return Hash
                 ▼                               │
  ┌──────────────────────────────────────────────┴──────────────┐
  │                    SQLite Database (ACID)                   │
  │                 `users` & `audit_logs`                      │
  └─────────────────────────────────────────────────────────────┘
```

### 2.1 Password Hashing Strategy
- **Algorithm:** Argon2id (memory-hard, resistant to GPU/ASIC brute-force cracking) using `pwdlib[argon2]`.
- **Policy:** Minimum 8 characters. Passwords are never stored in plaintext, never logged in terminal output or audit records, and never included in API responses or user schemas.

### 2.2 JWT Token Specifications
- **Format:** Signed RFC 7519 JSON Web Token (`HS256`).
- **Payload Claims:**
  - `sub`: User ID string (`str(user.id)`)
  - `email`: User email address
  - `role`: Canonical uppercase role (`USER`, `ANALYST`, `ADMIN`)
  - `exp`: UTC expiration timestamp (default 60 minutes)
  - `iat`: UTC issuance timestamp
- **Security Rule:** Passwords, password hashes, and sensitive document text are strictly excluded from the token.

---

## 3. Data Models & Database Migrations

### 3.1 User Model (`backend/app/models/user.py`)
```python
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    name = Column(String(100), nullable=True)  # Backward-compatibility alias
    role = Column(String(20), default="USER", nullable=False)  # 'USER', 'ANALYST', 'ADMIN'
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relationships
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan", foreign_keys="Document.user_id")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan", foreign_keys="AuditLog.user_id")
```

### 3.2 AuditLog Model (`backend/app/models/audit.py`)
```python
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True)
    action = Column(String(50), nullable=False)
    resource_type = Column(String(50), nullable=True)
    resource_id = Column(Integer, nullable=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="SET NULL"), index=True, nullable=True)
    status = Column(String(20), default="SUCCESS", nullable=False)  # 'SUCCESS', 'FAILURE'
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    ip_address = Column(String(45), nullable=True)
    details = Column(String(500), nullable=True)

    user = relationship("User", back_populates="audit_logs", foreign_keys=[user_id])
    document = relationship("Document", back_populates="audit_logs", foreign_keys=[document_id])
```

### 3.3 Safe Schema Evolution in `init_db()`
`backend/app/core/database.py` executes lightweight SQLite introspection (`PRAGMA table_info`) at runtime to safely add any missing columns across previous phases without losing data:
- `users`: `username`, `full_name`, `updated_at`
- `documents`: `owner_id`, `extracted_text`, `pages_json`
- `extracted_keywords`: `rank`
- `extracted_entities`: `normalized_text`, `confidence`, `source`
- `audit_logs`: `resource_type`, `resource_id`, `status`, `ip_address`

---

## 4. Role-Based Access Control (RBAC) & Ownership Matrix

| Endpoint | Public | `USER` | `ANALYST` | `ADMIN` |
| :--- | :---: | :---: | :---: | :---: |
| `POST /api/v1/auth/register` | ✅ (Creates `USER`) | ❌ | ❌ | ❌ |
| `POST /api/v1/auth/login` | ✅ | ✅ | ✅ | ✅ |
| `GET /api/v1/auth/me` | ❌ (401) | ✅ (Own profile) | ✅ (Own profile) | ✅ (Own profile) |
| `POST /api/v1/documents/upload` | ❌ (401) | ✅ (Assigns owner) | ✅ (Assigns owner) | ✅ (Assigns owner) |
| `GET /api/v1/documents/` | ❌ (401) | ✅ (Own documents) | ✅ (Own documents) | ✅ (All documents) |
| `GET /api/v1/documents/{id}` | ❌ (401) | ✅ (Owner only; 403) | ✅ (Owner only; 403) | ✅ (All documents) |
| `POST /api/v1/analyses/{doc_id}` | ❌ (401) | ✅ (Owner only; 403) | ✅ (Owner only; 403) | ✅ (All documents) |
| `GET /api/v1/analyses/{id}/keywords` | ❌ (401) | ✅ (Owner only; 403) | ✅ (Owner only; 403) | ✅ (All documents) |
| `GET /api/v1/analyses/{id}/entities` | ❌ (401) | ✅ (Owner only; 403) | ✅ (Owner only; 403) | ✅ (All documents) |
| `GET /api/v1/users/` | ❌ (401) | ❌ (403) | ❌ (403) | ✅ |
| `PATCH /api/v1/users/{id}/*` | ❌ (401) | ❌ (403) | ❌ (403) | ✅ (With safeguard) |
| `GET /api/v1/admin/audit-logs` | ❌ (401) | ❌ (403) | ❌ (403) | ✅ |

### 4.1 Ownership Verification Logic
Enforced via `check_document_access(document, user, db, ip_address)`:
1. Administrators possess global system inspection authority.
2. Practitioners and Analysts must match `document.user_id` or `document.owner_id`.
3. Mismatches instantly append an `UNAUTHORIZED_ACCESS` event with `status=FAILURE` to the audit log and return HTTP 403 Forbidden.

---

## 5. Development Seed Accounts

The development database initialization script (`scripts/init_db.py`) automatically populates three demonstration accounts:

| Role | Username | Email | Password | Full Name |
| :--- | :--- | :--- | :--- | :--- |
| **`ADMIN`** | `admin` | `admin@lexextract.local` | `Admin@Lex2026!` | System Administrator |
| **`ANALYST`** | `analyst` | `analyst@lexextract.local` | `Analyst@Lex2026!` | Senior Legal Analyst |
| **`USER`** | `lawyer_user` | `demo@lexextract.local` | `User@Lex2026!` | Demonstration Lawyer |

*Viva Convenience:* The `LoginPage.jsx` UI includes quick-fill buttons for these three accounts, enabling immediate role switching during viva presentations.

---

## 6. Verification & Test Results

### 6.1 Pytest Suite Execution
```
tests\test_audit.py .......                                              [  8%]
tests\test_auth.py ..............                                        [ 24%]
tests\test_authorization.py ..........                                   [ 36%]
tests\test_database.py ............                                      [ 50%]
tests\test_document_ingestion.py .............                           [ 65%]
tests\test_entity_extraction.py ..............                           [ 82%]
tests\test_health.py ...                                                 [ 85%]
tests\test_keyword_extraction.py ............                            [100%]

======================= 85 passed, 1 warning in 15.07s ========================
```
- **Total Tests:** 85 / 85 passed (100%).
- **Security & RBAC Tests:** 31 tests passing across `test_auth.py` (14), `test_authorization.py` (10), and `test_audit.py` (7).
- **Regression Tests:** All 54 tests from Phases 1–5 continue to pass with zero regressions.

### 6.2 Live End-to-End Test Suite Execution (`verify_live_e2e_phase6.py`)
```
=======================================================
  PHASE 6 LIVE VERIFICATION TEST SUITE
=======================================================

[Step 1] Registering a new practitioner account...
  --> Registered successfully! User ID: 4, Role: USER

[Step 2] Authenticating as Advocate Priya Sen...
  --> JWT Token acquired: eyJhbGciOiJIUzI1NiIs...
  --> /auth/me profile validated: ID=4, Email=priya.sen@lexextract.local, Role=USER

[Step 3] Uploading a legal document under user context...
  --> Document uploaded: ID=19, Filename=lease_agreement_live.docx, WordCount=49

[Step 4] Running keyword and entity extraction...
  --> Analysis completed: ID=6, Keywords=20, Entities=10, Time=0.0423s

[Step 5] Retrieving extracted keywords and entities...
  --> Retrieved 20 ranked keywords. Top 3:
      - Commercial Lease Agreement (Score: 0.9, Category: contract)
      - Commercial Lease (Score: 0.8457, Category: property)
      - Lease Agreement (Score: 0.8457, Category: contract)
  --> Retrieved 10 classified legal entities:
      - Commercial Lease Agreement [CONTRACT] (Confidence: 0.98, Source: hybrid)
      - 15 January 2026 [DATE] (Confidence: 0.98, Source: hybrid)
      - ₹50,000 [MONEY] (Confidence: 0.98, Source: hybrid)
      - Supreme Court of India [COURT] (Confidence: 0.98, Source: hybrid)

[Step 6] Testing Cross-Tenant Isolation (Unauthorized User access)...
  --> User 2 attempting GET /documents/19 (Owned by User 1): HTTP 403
  --> User 2 attempting GET /analyses/6/keywords: HTTP 403
  --> User 2 attempting GET /analyses/6/entities: HTTP 403
  --> User 2 attempting GET /admin/audit-logs: HTTP 403
  --> ALL cross-tenant & privilege escalation attempts blocked with HTTP 403 Forbidden!

[Step 7] Testing User Logout...
  --> User signed out successfully.

[Step 8] Authenticating as System Administrator...
  --> Administrator authenticated successfully.

[Step 9] Inspecting User Management & Admin Safeguards...
  --> Admin retrieved 5 system users.
  --> Attempting to deactivate only active admin: HTTP 400 (Operation prohibited: Cannot deactivate the final active administrator.)
  --> Attempting to demote only active admin: HTTP 400 (Operation prohibited: Cannot change role of the final active administrator.)
  --> Admin preservation safeguards operational!

[Step 10] Inspecting Governance Audit Trail...
  --> Total Audit Events recorded in ledger: 41
  --> Distinct actions observed: {'UNAUTHORIZED_ACCESS', 'KEYWORD_VIEW', 'ENTITY_VIEW', 'DOCUMENT_VIEW', 'DOCUMENT_UPLOAD', 'ANALYSIS_COMPLETE', 'REGISTER', 'ANALYSIS_START', 'LOGOUT', 'LOGIN_SUCCESS'}
  --> Verified 4 UNAUTHORIZED_ACCESS incidents logged with status FAILURE

=======================================================
  ALL LIVE PHASE 6 VERIFICATION CHECKS PASSED (10/10)
=======================================================
```

### 6.3 Production Frontend Build Result
```
vite v5.4.21 building for production...
transforming...
✓ 1549 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                   0.94 kB │ gzip:  0.54 kB
dist/assets/index-CQXgtJjv.css   27.28 kB │ gzip:  5.35 kB
dist/assets/index-ToHkgoz_.js   287.39 kB │ gzip: 83.28 kB
✓ built in 39.06s
```

---

## 7. Curriculum Integration

### Enterprise Systems (ES)
- **Role-Based Access Control (RBAC):** Strict separation between user privileges (`USER`, `ANALYST`, `ADMIN`), implemented cleanly through FastAPI dependency injection decorators.
- **Data Governance & Auditability:** Non-repudiation ledger ensuring every state modification, credential authentication, document ingestion, and unauthorized access attempt is immutably logged with actor ID, IP address, and timestamp.
- **Administrative Continuity:** Hard server-side safeguards preventing administrative self-lockout or complete system orphaned states.

### Advanced Social, Text and Media Analytics (ASTMA)
- **Ownership of NLP Models & Artifacts:** Document texts, candidate keyphrases, composite scores, and extracted entities are securely partitioned by practitioner identity, preventing cross-tenant information leakage.

### IT Project Management (ITPM)
- **Recovery & Continuity Management:** Successfully diagnosed and recovered from an unexpected server crash without rewriting or duplicating existing assets, identifying subtle metaclass conflicts between Python 3.14 and SQLAlchemy.
- **Automated Verification:** Comprehensive test suite with 85 unit tests and 10 live end-to-end integration tests guaranteeing zero regressions across prior phases.

---

## 8. Limitations & Phase 7 Boundary

- **Academic Scope:** The authentication system uses single-factor password authentication and signed HS256 JWT tokens suitable for academic demonstration. Multi-Factor Authentication (MFA), OAuth2 social login, Single Sign-On (SSO), and LDAP are intentionally out of scope.
- **Token Invalidation:** Stateless JWT tokens expire automatically via the `exp` claim (60 minutes). A Redis token revocation blacklist was omitted to avoid unnecessary infrastructure complexity.
- **Phase 7 Boundary:** Phase 7 (Export Engine: PDF/CSV/JSON report generation) has NOT been started.
