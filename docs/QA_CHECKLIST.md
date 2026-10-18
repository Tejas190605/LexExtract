# Quality Assurance (QA) Checklist

**Project Title:** LexExtract — Legal Document Keyword & Entity Extractor  
**Subject:** Enterprise Systems (ES) & Information Technology Project Management (ITPM)  
**QA Verification Date:** October 2026  
**Final Test Status:** 119 Passed, 0 Failed, 0 Skipped (100% Pass Rate)  
**Frontend Build Status:** Vite v5.4.21 production bundle built cleanly with 0 errors  

---

## 1. Functional Verification Checklist

| Item | Verification Criteria | Expected Outcome | Actual Result | Status |
| :---: | :--- | :--- | :--- | :---: |
| **FN-01** | User Registration & Login | User registers with valid credentials; receives JWT access token. | JWT generated; user redirected to dashboard. | **PASS** |
| **FN-02** | Invalid Login Handling | Submitting wrong password or unregistered email fails gracefully. | Returns HTTP 401 with clear error message; no stack trace. | **PASS** |
| **FN-03** | Document Ingestion (PDF) | User uploads selectable legal PDF document. | File stored; pages parsed; text extracted into DB. | **PASS** |
| **FN-04** | Document Ingestion (DOCX) | User uploads legal agreement in Microsoft Word format. | Text and structure extracted cleanly. | **PASS** |
| **FN-05** | Document Ingestion (TXT) | User uploads plain legal text file. | Text stored and queued for analysis. | **PASS** |
| **FN-06** | Invalid File Extension Upload | User attempts to upload `.exe`, `.bin`, `.zip`, or unsupported format. | Rejected with HTTP 400 Bad Request; file discarded. | **PASS** |
| **FN-07** | Automated Analysis Execution | Triggering analysis computes TF-IDF, RAKE, Hybrid keywords, and NER. | Extracted keywords and entities persisted with ranks & scores. | **PASS** |
| **FN-08** | Document At-a-Glance | System synthesizes document type, parties, dates, and attention areas. | Insights dashboard displays all summary metrics and warnings. | **PASS** |
| **FN-09** | Important Clauses Detection | Scans for 13 standard legal clause categories with text snippets. | Displays Found/Not Found status, section titles, and text snippets. | **PASS** |
| **FN-10** | Obligations Extraction | Identifies modal duties (`shall`, `must`, `agrees to`) and responsible parties. | Tabular breakdown of party, duty, deadline, and prohibition flag. | **PASS** |
| **FN-11** | Dates & Monetary Facts | Identifies monetary figures and dates with contextual categories. | Displays organized facts with currency indicators and date types. | **PASS** |
| **FN-12** | In-Document Search | User queries term within analyzed document; returns matches with context. | Match count, offsets, and contextual snippets rendered with scores. | **PASS** |
| **FN-13** | Two-Document Comparison | User selects two documents to compare cosine similarity & clause diffs. | Displays similarity %, metadata diffs, and clause alignment status. | **PASS** |
| **FN-14** | Report Export (JSON) | User requests JSON analysis export. | Comprehensive JSON payload generated with disclaimer. | **PASS** |
| **FN-15** | Report Export (PDF) | User requests printable legal analysis report PDF. | Multi-page professional PDF generated via PyMuPDF with header & disclaimer. | **PASS** |
| **FN-16** | Document History & Management | User views historical uploads, downloads, or deletes owned documents. | Documents listed chronologically; cascading deletion cleans DB. | **PASS** |
| **FN-17** | Admin Audit Trail | Administrator views governance audit ledger. | Paginated audit logs displayed with action, timestamp, IP, and status. | **PASS** |

---

## 2. User Interface (UI) & UX Checklist

| Item | Verification Criteria | Expected Outcome | Actual Result | Status |
| :---: | :--- | :--- | :--- | :---: |
| **UI-01** | Visual Design & Theme | Professional legal-tech dark aesthetic with navy slate and amber gold accents. | Clean typography (Inter/Cinzel), subtle card borders, polished icons. | **PASS** |
| **UI-02** | Responsive Layout | Interface adapts seamlessly across desktop (1920x1080) and laptop viewports. | Flexbox/CSS Grid layouts reflow cleanly without horizontal overflow. | **PASS** |
| **UI-03** | Interactive Document Viewer | Highlighting keywords and entities directly inside extracted document text. | Color-coded highlights (blue for keywords, purple for entities) with interactive tooltips. | **PASS** |
| **UI-04** | Tab Navigation | Switching between Keywords, Entities, Clauses, Obligations, and Search tabs. | Instantaneous client-side state transitions without page reloads. | **PASS** |
| **UI-05** | Empty & Loading States | User navigates to pages with no data or during active API fetching. | Friendly empty state placeholders and spinner loaders displayed. | **PASS** |
| **UI-06** | Error Presentation | Network dropouts or API errors surface to user. | Toast notifications and alert banners display friendly error copy; 0 raw stack traces exposed. | **PASS** |

---

## 3. Security & Access Control Checklist

| Item | Verification Criteria | Expected Outcome | Actual Result | Status |
| :---: | :--- | :--- | :--- | :---: |
| **SEC-01** | Stateless Authentication | API requests authenticated via RFC 7519 JWT Bearer tokens (HS256). | Protected routes reject requests without valid Bearer token (401). | **PASS** |
| **SEC-02** | Password Hashing | Passwords hashed using industry-standard Argon2id algorithm. | Zero plain-text passwords stored; rainbow table resilient. | **PASS** |
| **SEC-03** | Tenant Document Isolation | User A cannot access User B's documents, analyses, or reports. | Database query filters enforce ownership; unauthorized ID returns 403. | **PASS** |
| **SEC-04** | Role-Based Access Control | Non-admin users cannot access `/api/v1/admin/*` endpoints or pages. | Intercepted by `require_admin` dependency; returns HTTP 403 Forbidden. | **PASS** |
| **SEC-05** | Input Sanitization & Escaping | Malicious input containing SQL quotes or regex injection. | SQLAlchemy parameterized queries prevent SQLi; regex escaped safely. | **PASS** |
| **SEC-06** | Audit Trail Immutability | Critical security events (login, upload, delete, export) logged permanently. | Inserted into `audit_logs` table with timestamp, user ID, action, and IP. | **PASS** |

---

## 4. Performance & Scalability Checklist

| Item | Verification Criteria | Target Benchmark | Measured Performance | Status |
| :---: | :--- | :---: | :---: | :---: |
| **PRF-01** | Standard Document Processing | $< 1.0\text{ s}$ per document | **$230.5\text{ ms}$** average on 12 benchmark contracts | **PASS** |
| **PRF-02** | Keyword Pipeline Latency | $< 500\text{ ms}$ | **$148.9\text{ ms}$** average | **PASS** |
| **PRF-03** | Entity Pipeline Latency | $< 300\text{ ms}$ | **$81.6\text{ ms}$** average | **PASS** |
| **PRF-04** | In-Document Text Search | $< 100\text{ ms}$ | **$< 15\text{ ms}$** execution time | **PASS** |
| **PRF-05** | Two-Document Comparison | $< 500\text{ ms}$ | **$< 75\text{ ms}$** execution time | **PASS** |
| **PRF-06** | Multi-Page PDF Generation | $< 2.0\text{ s}$ | **$< 250\text{ ms}$** via PyMuPDF vector rendering | **PASS** |
| **PRF-07** | Frontend Bundle Size | $< 500\text{ kB}$ gzip | **$104.8\text{ kB}$** gzip JS bundle | **PASS** |

---

## 5. Data Tier Integrity Checklist

| Item | Verification Criteria | Expected Outcome | Actual Result | Status |
| :---: | :--- | :--- | :--- | :---: |
| **DAT-01** | Foreign Key Cascading | Deleting a document removes associated analyses, keywords, and entities. | Clean cascading delete prevents orphan rows in child tables. | **PASS** |
| **DAT-02** | Connection Pooling | Concurrent requests do not lock SQLite database file. | `StaticPool` in testing and connection pooling in production run cleanly. | **PASS** |
| **DAT-03** | Schema Migration Readiness | Data models use strict SQLAlchemy declarative mappings. | Fully portable to PostgreSQL or MySQL via `DATABASE_URL` config change. | **PASS** |

---

## 6. NLP & ASTMA Quality Checklist

| Item | Verification Criteria | Expected Outcome | Actual Result | Status |
| :---: | :--- | :--- | :--- | :---: |
| **NLP-01** | Explainable IR Algorithms | Algorithms adhere to open mathematical formulas (TF-IDF, RAKE). | Zero opaque cloud LLM dependencies; fully verifiable code. | **PASS** |
| **NLP-02** | Empirical Benchmarking | Ground truth evaluation on 12 curated legal documents. | Repeatable evaluation runner generates Micro/Macro P, R, F1. | **PASS** |
| **NLP-03** | Source Text Traceability | Extracted clauses, obligations, and facts retain original text context. | Each record tracks `source_section`, `source_page`, and snippet. | **PASS** |
| **NLP-04** | Legal Disclaimer Enforcement | Reports, UI insights, and exports clearly state assistive nature. | Non-legal advice disclaimer embedded in all JSON, PDF, and UI views. | **PASS** |
