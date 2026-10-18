# LexExtract — Comprehensive Manual Acceptance Test Checklist

**Version:** 1.0.0 (Release Testing)  
**Project:** LexExtract — Legal Document Keyword & Entity Extractor  
**Date:** October 2026  

Use this master checklist to systematically verify every major functional, security, and UI component of the platform during final acceptance testing.

---

## 1. Authentication & Identity
- [ ] **Register:** New user successfully registers with valid details (Full Name, Email, Username, Password).
- [ ] **Login:** Registered user logs in and receives authentication token.
- [ ] **Logout:** User logs out; authentication tokens are removed; browser is redirected to `/login`.
- [ ] **Invalid Login:** Supplying an incorrect password or non-existent username displays an error message without throwing unhandled exceptions.
- [ ] **Registration Validation:** Submitting incomplete registration fields or non-matching passwords shows inline validation.

---

## 2. Document Management
- [ ] **Upload:** Uploading valid `.pdf`, `.docx`, and `.txt` documents succeeds.
- [ ] **Validation:** File size ceiling (25 MB) and file format restrictions are strictly enforced.
- [ ] **Text Extraction:** Document text is correctly extracted and segmented into pages/paragraphs.
- [ ] **Analysis Execution:** Triggering analysis computes NLP extractions in under 500 ms.
- [ ] **History:** Uploaded documents appear in Repository History with accurate file size, word count, and timestamp.
- [ ] **Cascade Deletion:** Deleting a document from history purges all associated analysis runs and extractions.

---

## 3. Natural Language Processing & Text Mining
- [ ] **Keywords:** Hybrid extraction computes ranked keywords with composite, TF-IDF, and RAKE scores.
- [ ] **Entities:** Named Entity Recognition categorizes terms across 13 legal categories (Acts, Sections, Courts, Parties, Locations).
- [ ] **Clauses:** Identifies standard contractual clauses (Confidentiality, Termination, Indemnity, Arbitration, Governing Law) with confidence scores.
- [ ] **Obligations:** Separates affirmative duties (*shall*, *must*) from prohibitions (*shall not*, *must not*).
- [ ] **Dates:** Extracts execution dates, effective dates, and expiration dates.
- [ ] **Money:** Identifies monetary values across multiple currencies (INR ₹, USD $, EUR €, GBP £).
- [ ] **Deadlines:** Detects contractual timeframes (e.g., *30 days notice*, *within 10 days*).

---

## 4. Information Retrieval & Document Viewer
- [ ] **In-Document Search:** Querying for terms returns passage relevance scores and match counts.
- [ ] **Result Highlighting / Source:** Clicking search results or "Jump to Viewer" navigates directly to the target passage.
- [ ] **Document Viewer:** Formatted full document renders smoothly with layer toggles (*Keywords Only, Clean Plain Text, Original Stream*).

---

## 5. Document Comparison
- [ ] **Select Documents:** Dropdown allows selecting two documents from the user's repository.
- [ ] **Compare Execution:** Side-by-side comparison generates aligned clause views and vocabulary differences.
- [ ] **Changed Values:** Highlights modified commercial terms (fees, deadlines, caps).
- [ ] **Added Information:** Identifies newly introduced provisions (e.g., renewal, cure mechanisms).
- [ ] **Removed Information:** Identifies omitted or modified clauses.
- [ ] **Cosine Similarity:** Computes Vector Space Model cosine similarity percentage (0–100%).

---

## 6. Executive Reporting
- [ ] **PDF Export:** Generates multi-page vector PDF report with institutional formatting.
- [ ] **Report Opens:** Downloaded PDF opens cleanly in standard viewers (Adobe, Chrome, Edge) with zero corruption.
- [ ] **Report Content Correct:** PDF contains document metadata, overview, clauses, obligations, keywords, entities, and legal disclaimer.
- [ ] **JSON Export:** Downloads valid, formatted JSON schema for downstream data integration.

---

## 7. Administrator Governance
- [ ] **Admin Login:** System Administrator authenticates with `admin` / `Admin@Lex2026!`.
- [ ] **User Management / View:** Admin interface displays user directory with roles and active status.
- [ ] **Audit Logs:** Immutable audit log displays actor, action type, resource ID, IP address, and timestamp.
- [ ] **Protected Admin Routes:** Non-admin users are strictly blocked from accessing `/admin/audit` and `/api/v1/admin/*`.

---

## 8. Security & Multi-Tenancy
- [ ] **User Isolation:** User B is blocked from viewing, searching, or comparing User A's documents (`HTTP 403 Forbidden`).
- [ ] **RBAC Enforcement:** Role-based permissions are enforced across all API routes.
- [ ] **Protected APIs:** Unauthenticated requests to protected endpoints return `HTTP 401 Unauthorized`.
- [ ] **No Password Exposure:** Plaintext passwords and hashes are never exposed in user responses or audit logs.

---

## 9. User Interface & Aesthetics
- [ ] **Navigation:** Top navigation bar and subtabs allow seamless switching between views without full-page reloads.
- [ ] **Responsive Layout:** UI adapts cleanly across desktop and laptop viewports with zero horizontal clipping.
- [ ] **Empty States:** Friendly empty states display on blank tables and zero-result searches.
- [ ] **Error States:** Informative error notifications display when operations fail.
- [ ] **No Console Errors:** Browser developer tools console remains free of unhandled runtime errors.
- [ ] **Legal Disclaimer:** Institutional non-legal advice statement is clearly displayed on footers, results pages, and exported reports.

---

## Verification Sign-Off

- **Lead QA Engineer / Evaluator:** ___________________________  
- **Date Completed:** _______________________________________  
- **Total Checklist Items:** 35  
- **Items Passed:** _____ / 35  
- **Acceptance Determination:** `[ ] ACCEPTED FOR SUBMISSION` / `[ ] REJECTED`  
