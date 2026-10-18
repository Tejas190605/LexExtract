# LexExtract — Final Acceptance Testing Master Guide

**Document Version:** 1.0.0 (Release Acceptance Testing)  
**Project:** LexExtract — Legal Document Keyword & Entity Extractor  
**Date:** October 2026  

---

## 1. Quick Overview

This guide provides the complete, authoritative operational instructions for conducting the final acceptance testing of LexExtract from the perspective of a **clean first-time user** and an **administrator**.

All test protocols have been prepared in:
- [`docs/FIRST_USER_ACCEPTANCE_TEST.md`](file:///c:/Users/tejas/PBL%20project%20(ES,ASTMA,ITPM)/docs/FIRST_USER_ACCEPTANCE_TEST.md) — Step-by-step first-user experience (Employment Agreement & NDA).
- [`docs/DOCUMENT_COMPARISON_ACCEPTANCE_TEST.md`](file:///c:/Users/tejas/PBL%20project%20(ES,ASTMA,ITPM)/docs/DOCUMENT_COMPARISON_ACCEPTANCE_TEST.md) — Document version comparison (Service Agreement V1 vs. V2).
- [`docs/ADMIN_ACCEPTANCE_TEST.md`](file:///c:/Users/tejas/PBL%20project%20(ES,ASTMA,ITPM)/docs/ADMIN_ACCEPTANCE_TEST.md) — System administration, governance audit logs, and security isolation.
- [`docs/SAMPLE_DOCUMENT_EXPECTED_RESULTS.md`](file:///c:/Users/tejas/PBL%20project%20(ES,ASTMA,ITPM)/docs/SAMPLE_DOCUMENT_EXPECTED_RESULTS.md) — Expected extraction benchmark.
- [`docs/FINAL_MANUAL_TEST_CHECKLIST.md`](file:///c:/Users/tejas/PBL%20project%20(ES,ASTMA,ITPM)/docs/FINAL_MANUAL_TEST_CHECKLIST.md) — Master 35-point acceptance checklist.

---

## 2. Safe Environment Reset Mechanism

Before beginning your acceptance test, run our non-destructive test reset script:

```bash
python backend/scripts/reset_dev_environment.py
```

### What this script does:
1. **Creates a safety backup:** Automatically creates a timestamped backup of your current database (`lexextract.db.bak_<timestamp>`).
2. **Archives prior uploads:** Moves any previously uploaded documents to `storage/uploads_archive_<timestamp>`.
3. **Resets test tables:** Truncates documents, analyses, extracted keywords/entities, and audit logs while preserving database schema and migrations.
4. **Seeds clean ADMIN account:** Creates the development administrator account (`admin` / `Admin@Lex2026!`).
5. **Zero ordinary user records:** Leaves the system ready for you to register the FIRST regular user through the actual registration form.

---

## 3. Starting the Application

### 3.1 Start the FastAPI Backend
Open a terminal and run:
```bash
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn main:app --host 127.0.0.1 --port 8000
```
- API Base URL: `http://127.0.0.1:8000`
- API Health Status: `http://127.0.0.1:8000/health`
- Interactive OpenAPI Docs: `http://127.0.0.1:8000/docs`

### 3.2 Start the React Frontend
Open a second terminal and run:
```bash
cd frontend
npm run dev
```
- Open your browser to: `http://127.0.0.1:5173` (Use an **Incognito / Private Window** to ensure a clean session cache).

---

## 4. Test Accounts

| Account Type | Username | Password | Role | Usage |
| :--- | :--- | :--- | :--- | :--- |
| **System Administrator** | `admin` | `Admin@Lex2026!` | `ADMIN` | Use for governance audit, viewing user directory, and verifying administrative controls. |
| **First Regular User** | `rohan_verma` | `Lawyer@Lex2026!` | `USER` | **Register via UI** at `/register` during Phase B of testing. |
| **Second Regular User (Security Isolation)** | `priya_sen` | `Priya@Lex2026!` | `USER` | **Register via UI** to test cross-tenant isolation and verify User A's documents cannot be accessed by User B. |

---

## 5. Sample Test Documents Location

All curated sample test files are located in the `sample_documents/` directory:

1. `sample_documents/01_Employment_Agreement.docx`:
   - Parties: Meridian Technologies Pvt. Ltd., Priya Sharma
   - Salary: INR 65,000/month, Effective: 1 April 2026 to 31 March 2027
   - Notice: 30 days, Clauses: Confidentiality, IP, Termination, Arbitration, Governing Law.
2. `sample_documents/02_Confidentiality_NDA.docx`:
   - Parties: Nova Labs Pvt. Ltd., Orbit Systems LLP
   - Term: 3 years, Return/Destruction: 10 days.
3. `sample_documents/03_Service_Agreement_V1.docx`:
   - Base service contract (Fee: INR 120,000/mo, Payment: 30 days, Cap: INR 500,000).
4. `sample_documents/04_Service_Agreement_V2.docx`:
   - Revised service contract with 6 negotiated amendments (Fee: INR 145,000/mo, Payment: 15 days, 6-mo auto renewal, 60 days notice, cure period, Cap: INR 750,000).

---

## 6. Recommended Execution Order

Follow this 5-stage sequential order for complete validation:

```
[ STAGE 1: FIRST-USER ACCEPTANCE TEST ]
Follow: docs/FIRST_USER_ACCEPTANCE_TEST.md
1. Register as First User (rohan_verma).
2. Login and verify clean 0-state dashboard.
3. Upload and analyze 01_Employment_Agreement.docx.
4. Inspect Overview, Keywords, Entities, Clauses, Obligations, Dates/Money.
5. Perform in-document search and jump to Document Viewer.
6. Export PDF and JSON reports.
7. Upload and analyze 02_Confidentiality_NDA.docx.
8. Logout and verify back-button session invalidation.
     ↓
[ STAGE 2: DOCUMENT COMPARISON TEST ]
Follow: docs/DOCUMENT_COMPARISON_ACCEPTANCE_TEST.md
1. Ingest 03_Service_Agreement_V1.docx and 04_Service_Agreement_V2.docx.
2. Navigate to Document Comparison (/compare).
3. Select V1 as Base and V2 as Revised.
4. Verify Cosine Similarity score (~85-95%).
5. Verify side-by-side identification of all 6 negotiated changes.
     ↓
[ STAGE 3: SECURITY & MULTI-TENANT ISOLATION ]
Follow: docs/ADMIN_ACCEPTANCE_TEST.md (Section 3)
1. Register second user (priya_sen).
2. Attempt to open First User's document URL (/analysis/1).
3. Verify access is rejected (HTTP 403 Forbidden).
4. Verify First User's documents do not appear in Second User's comparison dropdown.
     ↓
[ STAGE 4: ADMINISTRATOR GOVERNANCE & AUDIT ]
Follow: docs/ADMIN_ACCEPTANCE_TEST.md (Section 2)
1. Log in as admin (admin / Admin@Lex2026!).
2. Open Admin Audit (/admin/audit).
3. Verify immutable event logs (USER_LOGIN, DOCUMENT_UPLOAD, ANALYSIS_EXECUTE).
4. Verify password hashes are NEVER exposed in user directory.
5. Log in as normal user and verify admin URLs are strictly inaccessible.
     ↓
[ STAGE 5: FINAL CHECKLIST SIGN-OFF ]
Follow: docs/FINAL_MANUAL_TEST_CHECKLIST.md
Complete all 35 checklist verification items and record final sign-off.
```

---

## 7. How to Record PASS / FAIL Results

1. Open [`docs/FINAL_MANUAL_TEST_CHECKLIST.md`](file:///c:/Users/tejas/PBL%20project%20(ES,ASTMA,ITPM)/docs/FINAL_MANUAL_TEST_CHECKLIST.md) or the relevant protocol markdown file.
2. Mark verified checkboxes with `[x]`.
3. If any result varies from expectation, document the variance without changing application code:
   ```markdown
   - EXPECTED: ...
   - ACTUAL: ...
   - SOURCE TEXT: ...
   - REASON FOR DIFFERENCE: ...
   ```
4. Sign off the acceptance certificate upon completing all test journeys.
