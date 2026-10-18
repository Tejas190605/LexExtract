# Phase 6 Implementation Plan — Authentication, RBAC & Audit Trail

**Project:** LexExtract — Legal Document Keyword & Entity Extractor  
**Phase:** Phase 6 — Authentication, RBAC & Audit Trail  
**Status:** Planning & Architectural Design  

---

## 1. Executive Summary

Phase 6 implements an enterprise-grade security, identity, access control, and compliance governance layer for LexExtract. While Phases 1–5 focused on document ingestion, natural language processing, keyword ranking, and legal entity extraction, Phase 6 enforces:
1. **User Identity & Cryptographic Authentication:** Secure password hashing (Argon2id via `pwdlib`), stateless signed JSON Web Tokens (`PyJWT`), user registration, login, and `/auth/me` profile inspection.
2. **Role-Based Access Control (RBAC):** Three controlled roles (`USER`, `ANALYST`, `ADMIN`) with strict server-side dependency gates (`get_current_user`, `require_role`, `require_admin`).
3. **Data Ownership & Isolation:** Mandatory document attribution (`Document.owner_id` / `Document.user_id`). Users can only inspect and analyze their own documents; Cross-tenant access attempts are blocked with HTTP 403.
4. **Non-Repudiation Audit Ledger:** Centralized, append-only `AuditLog` service tracking security events (logins, failures, uploads, analyses, unauthorized access attempts, and administrative role modifications).
5. **Administrative Controls & UI:** Admin audit log explorer with filtering/pagination and user account administration (activation/deactivation/role assignment with safeguard against deactivating the last active admin).

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
- **Policy:** Minimum 8 characters. Passwords are never stored in plaintext, never logged, and never included in API responses or audit details.

### 2.2 JWT Token Specifications
- **Format:** Signed RFC 7519 JSON Web Token (`HS256`).
- **Payload Claims:**
  - `sub`: User ID (`str(user.id)`)
  - `email`: User email address
  - `role`: Canonical uppercase role (`USER`, `ANALYST`, `ADMIN`)
  - `exp`: UTC expiration timestamp (default 60 minutes, configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
  - `iat`: UTC issuance timestamp
- **Exclusions:** Passwords, password hashes, and sensitive document data are never embedded in the token.

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
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
```

### 3.2 Document Model Alignment (`backend/app/models/document.py`)
- Retains existing `user_id` foreign key.
- Adds explicit `owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=True)`.
- Synchronizes `owner_id` with `user_id` to guarantee compatibility across existing tests and new authorization checks.

### 3.3 AuditLog Model (`backend/app/models/audit.py`)
```python
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True)
    action = Column(String(50), nullable=False)
    resource_type = Column(String(50), nullable=True)
    resource_id = Column(Integer, nullable=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(20), default="SUCCESS", nullable=False)  # 'SUCCESS', 'FAILURE'
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    ip_address = Column(String(45), nullable=True)
    details = Column(String(500), nullable=True)

    # Relationships
    user = relationship("User", back_populates="audit_logs")
```

### 3.4 Idempotent SQLite Migration in `init_db()`
Updates `backend/app/core/database.py` with `PRAGMA table_info` introspection to add any missing columns (`username`, `full_name`, `updated_at` to `users`; `owner_id` to `documents`; `resource_type`, `resource_id`, `status`, `ip_address` to `audit_logs`) without data loss.

---

## 4. Role-Based Access Control (RBAC) & Ownership Matrix

| Feature / Endpoint | Public / Unauth | Role: `USER` | Role: `ANALYST` | Role: `ADMIN` |
| :--- | :---: | :---: | :---: | :---: |
| `POST /auth/register` | ✅ (Creates USER) | ❌ | ❌ | ❌ |
| `POST /auth/login` | ✅ | ✅ | ✅ | ✅ |
| `GET /auth/me` | ❌ (401) | ✅ (Own info) | ✅ (Own info) | ✅ (Own info) |
| `POST /documents/upload` | ❌ (401) | ✅ (Assigns owner) | ✅ (Assigns owner) | ✅ (Assigns owner) |
| `GET /documents/` | ❌ (401) | ✅ (Own documents) | ✅ (Own documents) | ✅ (All documents) |
| `GET /documents/{id}` | ❌ (401) | ✅ (If owner; 403 if not) | ✅ (If owner; 403 if not) | ✅ (All documents) |
| `POST /analyses/{doc_id}`| ❌ (401) | ✅ (If owner; 403 if not) | ✅ (If owner; 403 if not) | ✅ (All documents) |
| `GET /analyses/{id}/keywords`| ❌ (401) | ✅ (If owner; 403 if not) | ✅ (If owner; 403 if not) | ✅ (All documents) |
| `GET /analyses/{id}/entities`| ❌ (401) | ✅ (If owner; 403 if not) | ✅ (If owner; 403 if not) | ✅ (All documents) |
| `GET /users` & `{id}` | ❌ (401) | ❌ (403) | ❌ (403) | ✅ |
| `PATCH /users/{id}/*` | ❌ (401) | ❌ (403) | ❌ (403) | ✅ (With safety guard) |
| `GET /admin/audit-logs` | ❌ (401) | ❌ (403) | ❌ (403) | ✅ |

### 4.1 Ownership Verification Logic
```python
def check_document_access(document: Document, user: User, db: Session, action: str = "DOCUMENT_VIEW") -> Document:
    # 1. Administrators have global system inspection authority
    if user.role.upper() == Role.ADMIN:
        return document
    
    # 2. Check ownership match
    if document.user_id == user.id or (document.owner_id and document.owner_id == user.id):
        return document
        
    # 3. Unauthorized access attempt -> Log & Raise 403
    AuditService.record_audit_event(
        db=db,
        action=AuditAction.UNAUTHORIZED_ACCESS,
        user_id=user.id,
        resource_type="DOCUMENT",
        resource_id=document.id,
        status="FAILURE",
        details=f"User {user.email} denied access to document {document.id} owned by user {document.user_id}"
    )
    raise HTTPException(status_code=403, detail="You do not have permission to access this legal document.")
```

---

## 5. Audit Logging Architecture (`audit_service.py`)

### Controlled Audit Event Taxonomy:
- `LOGIN_SUCCESS`, `LOGIN_FAILURE`, `LOGOUT`, `REGISTER`
- `DOCUMENT_UPLOAD`, `DOCUMENT_VIEW`, `DOCUMENT_DELETE`
- `ANALYSIS_START`, `ANALYSIS_COMPLETE`, `ANALYSIS_FAILED`
- `KEYWORD_VIEW`, `ENTITY_VIEW`
- `USER_CREATED`, `USER_ROLE_CHANGED`, `USER_ACTIVATED`, `USER_DEACTIVATED`
- `UNAUTHORIZED_ACCESS`

### Security Safeguards:
- Append-only architecture: no REST API endpoint allows deletion or modification of audit records.
- Automatic sanitization: credentials, tokens, and full legal texts are strictly excluded.
- Contextual logging: user ID, client IP address, resource type/ID, status (`SUCCESS` / `FAILURE`), and brief operational details.

---

## 6. Seed Accounts & Development Credentials

The database initialization script (`scripts/init_db.py`) will seed three development test actors:

| Role | Username | Email | Password | Full Name |
| :--- | :--- | :--- | :--- | :--- |
| **`ADMIN`** | `admin` | `admin@lexextract.local` | `Admin@Lex2026!` | System Administrator |
| **`ANALYST`** | `analyst` | `analyst@lexextract.local` | `Analyst@Lex2026!` | Senior Legal Analyst |
| **`USER`** | `lawyer_user` | `demo@lexextract.local` | `User@Lex2026!` | Demonstration Lawyer |

*Security Warning:* These are development demonstration credentials. They are clearly separated from production configuration.

---

## 7. Frontend Integration Strategy

1. **`AuthContext.jsx`:**
   - Manages state: `user`, `token`, `isAuthenticated`, `role`, `loading`.
   - Methods: `login(emailOrUsername, password)`, `register(data)`, `logout()`.
   - Reads token from `localStorage` on boot; validates via `/auth/me`.
2. **`api.js` Request Interceptor:**
   - Automatically attaches `Authorization: Bearer <token>` to all authenticated requests.
   - Intercepts `401 Unauthorized` responses and triggers session clearance and redirection to login.
3. **`LoginPage.jsx`:**
   - Professional legal styling with quick-fill demo buttons for `Admin`, `Analyst`, and `Lawyer/User` to streamline college viva defense.
4. **`RegisterPage.jsx`:**
   - Full Name, Username, Email, Password, Confirm Password with client-side length and equality validation. Normal registrations are strictly assigned `role = USER`.
5. **`AdminAuditPage.jsx`:**
   - Real-time audit log explorer with action filter, status filter, and pagination controls.
   - Integrated User Administration table allowing activation, deactivation, and role changes with safeguard against self-locking the last active admin.

---

## 8. Testing Strategy

### Unit & Security Test Suites:
- `backend/tests/test_auth.py`:
  - Password hashing and verification via Argon2id.
  - JWT creation, claims decoding, expiration rejection, invalid signature handling.
  - Registration: success, duplicate email rejection, duplicate username rejection, password length validation.
  - Login: success, invalid password rejection, unknown user rejection, inactive user rejection.
  - `/auth/me` profile inspection and credential exclusion.
- `backend/tests/test_authorization.py`:
  - Unauthenticated access to protected endpoints returns 401.
  - `USER` accessing admin endpoints (`/users`, `/admin/audit-logs`) returns 403.
  - `ANALYST` accessing admin endpoints returns 403.
  - Document ownership: user accessing another user's document returns 403.
  - Analysis ownership: user accessing another user's analysis keywords/entities returns 403.
  - `ADMIN` accessing system documents and analyses succeeds.
- `backend/tests/test_audit.py`:
  - Audit logging on login success/failure, registration, document upload, analysis execution, and unauthorized access attempts.
  - Verification that passwords, tokens, and raw document texts are never recorded in `AuditLog.details`.
  - Verification that audit logs cannot be deleted or modified via API.
- **Regression Testing:** Ensure all 54 existing tests (Database, Ingestion, Health, Keywords, Entities) continue to pass.

---

## 9. Acceptance Criteria

- [ ] `PyJWT` and `pwdlib[argon2]` installed and functional.
- [ ] User passwords securely hashed with Argon2id.
- [ ] JWT tokens issued with expiration and proper claims.
- [ ] `/auth/register` creates `USER` without exposing passwords.
- [ ] `/auth/login` validates credentials and returns Bearer token.
- [ ] `/auth/me` returns current user details.
- [ ] Roles `USER`, `ANALYST`, `ADMIN` enforced across endpoints.
- [ ] Document ownership enforced; cross-tenant document and analysis access blocked with 403.
- [ ] Audit logs recorded for authentication, uploads, analyses, unauthorized access, and admin actions.
- [ ] Admin audit log API and UI operational with real pagination and filters.
- [ ] Admin user management operational with safeguard protecting the last admin.
- [ ] All 54 previous backend tests pass + new security tests pass.
- [ ] Frontend builds cleanly and browser verification passes end-to-end demo flow.
- [ ] Phase 7 has NOT been started.
