# LexExtract — Administrator & Security Acceptance Test Protocol

**Document Version:** 1.0.0 (Release Acceptance Testing)  
**Target Roles:** System Administrator (`ADMIN`) & Cross-User Security  
**Date:** October 2026  

---

## 1. Overview & Objectives

This protocol guides the manual testing of administrator privileges, governance compliance audit logs, multi-tenant security isolation, session boundary enforcement, and defensive error handling.

---

## 2. Administrator Workflows

### Test A: Admin Authentication
- **Step A.1:**
  - **Action:** Navigate to `http://127.0.0.1:5173/login`. Enter Admin credentials:
    - Username: `admin`
    - Password: `Admin@Lex2026!`
    Click **"Sign In"**.
  - **Expected Result:** Authentication succeeds. Header shows user name `System Administrator` and purple/gold role badge `ADMIN`. The navigation menu contains an additional link: **"Admin Audit"**.
  - **Pass/Fail:** `[ ]`
  - **Observation:**

---

### Test B: Admin Audit & Governance Ledger
- **Step B.1:**
  - **Action:** Click **"Admin Audit"** in the navigation.
  - **Expected Result:** Navigates to `/admin/audit`. The page displays:
    1. System Governance Statistics cards (Total Logged Events, Active Users, Document Actions, System Integrity Status).
    2. Audit Trail Events table with columns: Timestamp (UTC), Action Type, Actor / User ID, Resource Type, Resource ID, Client IP, Status (`SUCCESS`).
  - **Pass/Fail:** `[ ]`
  - **Observation:**

---

### Test C & D: User Directory & Password Protection
- **Step C.1:**
  - **Action:** Inspect the Users table / list in the admin interface.
  - **Expected Result:**
    - Displays registered platform accounts (e.g., `admin`, and any newly registered user accounts such as `rohan_verma`).
    - Columns display ID, Username, Email, Full Name, Role, Account Status (`ACTIVE`), Created Date.
    - **CRITICAL SECURITY CHECK:** Password hashes and plaintext passwords are **NEVER** displayed or present in API response payloads.
  - **Pass/Fail:** `[ ]`
  - **Observation:**

---

### Test E, F & G: Inspect Activity Events
- **Step E.1:**
  - **Action:** Review recent events logged in the Audit Trail after a document upload and analysis run.
  - **Expected Result:**
    - `USER_LOGIN`: Records authentication event for `admin` with client IP.
    - `DOCUMENT_UPLOAD`: Records document upload event with target filename and document ID.
    - `ANALYSIS_EXECUTE`: Records analysis trigger event with document ID and processing status.
  - **Pass/Fail:** `[ ]`
  - **Observation:**

- **Step E.2:**
  - **Action:** Filter or search the audit log table by username (e.g., `rohan_verma`) or action (e.g., `DOCUMENT_UPLOAD`).
  - **Expected Result:** Audit table dynamically updates to show matching log entries.
  - **Pass/Fail:** `[ ]`
  - **Observation:**

---

### Test H: Access-Control Protection (Normal User Cannot Access Admin)
- **Step H.1:**
  - **Action:**
    1. Log out of the admin account.
    2. Log into the regular user account (`rohan_verma` / `Lawyer@Lex2026!`).
    3. Verify that the **"Admin Audit"** link is **NOT** present in the navigation header.
    4. Manually type the admin URL into the browser address bar: `http://127.0.0.1:5173/admin/audit` and press Enter.
  - **Expected Result:**
    - The client-side protected route guard intercepts the attempt.
    - Access is rejected. User is redirected to `/dashboard` or an *"Access Denied / 403 Forbidden"* notice is displayed.
  - **Pass/Fail:** `[ ]`
  - **Observation:**

- **Step H.2 (Direct API Route RBAC Check):**
  - **Action:** In browser developer tools or a terminal, attempt to query the admin API endpoint using regular user credentials:
    ```bash
    curl -H "Authorization: Bearer <USER_TOKEN>" http://127.0.0.1:8000/api/v1/admin/audit-logs
    ```
  - **Expected Result:** Server responds with `HTTP 403 Forbidden` (`detail: "Insufficient permissions. Admin role required."`).
  - **Pass/Fail:** `[ ]`
  - **Observation:**

---

## 3. Multi-Tenant Cross-User Security Testing

### Test S.1: Document Ownership Isolation
- **Step S.1:**
  - **Setup:**
    1. User A (`rohan_verma`) logs in and uploads `01_Employment_Agreement.docx`. Note the document ID (e.g., Document ID `1`).
    2. User A logs out.
    3. User B registers or logs in as a different user:
       - Username: `priya_sen`
       - Password: `Priya@Lex2026!`
  - **Action:** User B attempts to access User A's document directly by typing the URL:
    `http://127.0.0.1:5173/analysis/1` or `http://127.0.0.1:5173/viewer?docId=1`
  - **Expected Result:**
    - Access is denied.
    - System shows an error notice (*"Document not found or access denied"*) or returns to dashboard.
    - Backend returns `HTTP 403 Forbidden` or `HTTP 404 Not Found`. User A's document text, clauses, and entities are never revealed to User B.
  - **Pass/Fail:** `[ ]`
  - **Observation:**

- **Step S.2: Cross-User Comparison Isolation:**
  - **Action:** User B opens Document Comparison (`/compare`). Check the dropdown selection of documents.
  - **Expected Result:**
    - The document selection dropdown lists ONLY User B's documents.
    - User A's documents do not appear in the dropdown.
  - **Pass/Fail:** `[ ]`
  - **Observation:**

---

## 4. Session & Logout Security Testing

### Test L.1: Logout Session Cleansing
- **Action:**
  1. Log into LexExtract.
  2. Click **"Logout"**.
  3. Click the browser's **Back** button.
  4. Attempt to refresh the page or click links.
- **Expected Result:**
  - All cached authorization tokens are cleared from `localStorage`.
  - Back navigation bounces immediately to `/login`.
  - No protected document or dashboard content is displayed.
- **Pass/Fail:** `[ ]`
- **Observation:**

---

## 5. Defensive Input & Error Handling Testing

| Test Case | Test Input / Action | Expected System Behavior | Pass / Fail |
| :--- | :--- | :--- | :---: |
| **Unsupported File Format** | Upload an unsupported file (e.g., `.exe`, `.jpg`, `.zip`) | Rejection before or during upload with clear message: *"Unsupported file format. Please upload PDF, DOCX, or TXT."* | `[ ]` |
| **Oversized File** | Upload a file exceeding 25 MB | Upload rejected with message: *"File exceeds maximum allowed size (25 MB)."* HTTP 413. | `[ ]` |
| **Corrupted File** | Upload a 0-byte or corrupted `.docx` or `.pdf` | System catches parsing exception gracefully: *"Unable to extract text from file. Please ensure file is valid and readable."* Zero raw Python stack trace shown to user. | `[ ]` |
| **Empty Search Query** | In Search tab, submit an empty query string or whitespace | System prompts user to enter a query; does not trigger empty query crash. | `[ ]` |
| **Zero Match Search** | In Search tab, search for non-existent gibberish term (e.g., `xyzzy12345`) | System displays friendly empty state: *"No matching passages found for query 'xyzzy12345'."* | `[ ]` |
| **Duplicate Upload** | Upload the identical document twice in succession | System accepts the file with unique internal storage identifier without overwriting or crashing existing records. | `[ ]` |
| **Missing Form Fields** | Attempt registration with missing email or password confirmation mismatch | Inline client validation prevents submission with descriptive feedback. | `[ ]` |

---

## 6. Admin & Security Sign-Off

- **Tester Name:** ___________________________  
- **Test Date:** _____________________________  
- **Overall Result:** `[ ] PASS` / `[ ] FAIL`  
- **Comments:**  
  _________________________________________________________________________
