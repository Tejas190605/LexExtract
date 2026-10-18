# Phase 7 Walkthrough — Professional Legal UI, Document Viewer & Interactive Analysis

**Project:** LexExtract — Legal Document Keyword & Entity Extractor  
**Status:** COMPLETE & VERIFIED  
**Academic Alignment:** Enterprise Systems (ES), Advanced Software Testing & Mining Architecture (ASTMA), IT Project Management (ITPM)  

---

## 1. Objective

Phase 7 delivers a comprehensive, institutional legal technology user interface and interactive document viewer for **LexExtract**. Rather than resembling a generic AI SaaS or flashy neon dashboard, the interface is engineered to look and behave like an authoritative legal information retrieval platform (comparable to Westlaw, LexisNexis, or Relativity).

Key objectives fulfilled:
1. **Institutional Legal Design System:** Muted, authoritative color scheme (Deep Navy, Warm Parchment, Editorial Burgundy, Muted Gold), editorial serif typography, high-contrast borders, and zero AI gimmicks.
2. **Enterprise Application Shell (`AppShell`):** Persistent two-column desktop layout with a responsive, role-gated sidebar, real-time backend health monitor, and topbar breadcrumbs.
3. **Data-Driven Dashboard:** Executive legal intelligence metrics derived deterministically from real database records (no fake progress, no fake numbers).
4. **Professional Intake Workflow:** Streamlined drag-and-drop document upload with strict format/size validation and indeterminate multi-signal extraction state.
5. **Interactive Document Viewer:** Dual-mode viewing (Canonical Extracted Text with live token highlights vs. Original Streamed PDF / DOCX download), document metadata inspection, and interactive sliding context drawer.
6. **Unified Analysis Results:** Analytical workspace combining ranked keyword inspection, multi-category entity exploration, and query filtering.
7. **Document Repository History:** Searchable, sortable legal archive tracking document title, format, length, upload date, status, extracted keywords, and legal entities.
8. **Security & Governance Continuity:** Seamless preservation of Phase 6 Argon2id password hashing, stateless PyJWT bearer authorization, three-tier RBAC (`USER`, `ANALYST`, `ADMIN`), cross-tenant isolation (HTTP 403), and append-only audit trail.

---

## 2. UI Architecture & Navigation

The frontend is constructed with React 18, Vite, TailwindCSS (configured with institutional legal tokens), and Lucide icons.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        LexExtract TopBar Header                        │
│ Breadcrumb: LexExtract / [Page] │ Engine: Healthy │ RBAC: [Role] │ CTA │
├───────────────────┬────────────────────────────────────────────────────┤
│  Sidebar          │  Main Content Stage                                │
│                   │                                                    │
│  [Brand Header]   │  ┌──────────────────────────────────────────────┐  │
│                   │  │ Active Page Container                        │  │
│  CORE             │  │ (Dashboard / Intake / Results /              │  │
│   • Dashboard     │  │  Viewer / History / Evaluation / Admin)      │  │
│                   │  └──────────────────────────────────────────────┘  │
│  DOCUMENTS        │                                                    │
│   • Intake        │                                                    │
│   • History       │                                                    │
│                   │                                                    │
│  INTELLIGENCE     │                                                    │
│   • Results       │                                                    │
│   • Viewer        │                                                    │
│                   │                                                    │
│  EVALUATION (R)   │                                                    │
│   • ASTMA Bench   │                                                    │
│                   │                                                    │
│  ADMIN (R)        │                                                    │
│   • User Directory│                                                    │
│   • Audit Ledger  │                                                    │
│                   │                                                    │
│  [Practitioner]   │                                                    │
│  Priya Sen (USER) │                                                    │
│  [Sign Out]       │                                                    │
└───────────────────┴────────────────────────────────────────────────────┘
```

### Component Hierarchy
- `App.jsx`: Master orchestrator managing authentication state and route switching.
- `AppShell.jsx`: Responsive layout container uniting `Sidebar`, `TopBar`, and active page views.
- `Sidebar.jsx`: Institutional sidebar with section headers (`CORE`, `DOCUMENTS`, `INTELLIGENCE`, `EVALUATION`, `ADMINISTRATION`), role-based item visibility, and practitioner footer with logout.
- `TopBar.jsx`: Context breadcrumb trail, engine health monitor probe, RBAC pill, and "+ Analyze Document" quick action.
- Common Primitives: `StatusBadge`, `StatCard`, `PageHeader`, `EmptyState`, `LoadingState`, `ErrorState`.
- Viewer Components: `LegalTextHighlighter`, `EntityContextDrawer`.

---

## 3. Design System Specification

| Design Token | Value | Semantic Role |
| :--- | :--- | :--- |
| **Deep Navy** | `#0A192F` | Primary institutional brand, sidebar, table headers, primary buttons |
| **Navy Light** | `#172A45` | Hover states, active sidebar nav items, secondary headers |
| **Warm Parchment** | `#F8F7F4` | Primary page background, subtle paper texture |
| **Dark Parchment** | `#EFECE6` | Table rows, code blocks, badge backgrounds |
| **Editorial Burgundy**| `#722F37` | Analytical emphasis, primary CTAs, critical alerts, keywords |
| **Muted Gold** | `#C5A059` | Subtle borders, active indicator, metadata accents |
| **Charcoal** | `#2D3748` | Primary body typography, high-contrast readable legal text |
| **Charcoal Muted** | `#4A5568` | Secondary captions, timestamps, column descriptions |
| **Editorial Serif**| *Merriweather / Georgia* | Page titles, document headers, legal citations |
| **Interface Sans** | *Inter / System-UI* | Tables, navigation items, buttons, metadata tags |

---

## 4. Feature Implementation Details

### 4.1 Executive Dashboard (`DashboardPage.jsx`)
- **Real Aggregate Metrics:** Queries `listDocuments()` and `listDocumentAnalyses()` to calculate real counts:
  - Total Documents Ingested
  - Analyses Completed
  - Keywords Extracted
  - Legal Entities Found
- **Recent Ingested Documents Table:** Lists the 5 most recent documents with filename, format, upload date, status, and direct actions to "View" or "Results".
- **Empty State:** Clean prompt when 0 documents exist with "+ Analyze a Document" primary action.

### 4.2 Document Intake Workflow (`NewAnalysisPage.jsx`)
- **Validation Engine:** Rejects unsupported extensions (only `.pdf` and `.docx` accepted), zero-byte files, and oversized documents (>25MB).
- **Indeterminate Progress State:** Professional, multi-stage legal processing indicator without simulated percentage counters:
  1. *Uploading binary payload to secure storage*
  2. *Extracting canonical UTF-8 text and structure*
  3. *Executing hybrid RAKE and TF-IDF keyword ranking*
  4. *Detecting legal entities via spaCy & gazetteer*
  5. *Persisting analysis run to relational ledger*

### 4.3 Interactive Analysis Results (`AnalysisResultsPage.jsx`)
- **Executive Summary:** Document title, repository ID, processing time (seconds), total keywords, and total entities.
- **Dual Analytical Views:**
  - **Keywords Explorer:** Ranked table showing Rank, Keyword, Final Score, Category, and individual score breakdowns (TF-IDF, RAKE, Lexicon). Includes category filters (`All`, `contract`, `procedure`, `court`, `criminal`).
  - **Entity Explorer:** Category pills (`ALL`, `COURT`, `STATUTE`, `SECTION`, `PERSON`, `ORGANIZATION`, `DATE`, `MONEY`, `CASE_REFERENCE`), confidence scores (`0.75`–`0.98`), and source provenance (`regex`, `spacy`, `dictionary`, `hybrid`).
- **Global Search:** Instant frontend filter across keyword strings, entity text, and normalized forms.
- **Locate In Document:** Quick action jumping directly into the Document Viewer for the active document.

### 4.4 Interactive Document Viewer (`DocumentViewerPage.jsx`)
- **Dual-Mode Inspection:**
  - **Extracted Legal Text Mode:** Page-by-page rendering using `LegalTextHighlighter`. Features non-destructive regex slicing preserving legal citations.
  - **Original Document Stream Mode:** For PDFs, embeds native browser `<iframe src="/api/v1/documents/{id}/file" />` with a direct download button. For DOCX, explains structured text rendering and offers raw binary download.
- **Highlighting Controls:** Layer selector allows toggling between `All Overlays`, `Keywords Only`, `Entities Only`, and `Clean Plain Text`.
- **Entity Context Drawer (`EntityContextDrawer.jsx`):** Clicking any highlighted token opens a sliding inspector displaying:
  - Raw extracted entity text
  - Normalized canonical text
  - Entity category badge
  - Extraction confidence score
  - Source provenance (`spacy`, `regex`, `dictionary`, `hybrid`)
  - Full sentence occurrence context

### 4.5 Document Repository Archive (`DocumentHistoryPage.jsx`)
- Full repository table displaying:
  - Document Title & Repository ID
  - Format (`PDF` / `DOCX`)
  - Word Count & File Size
  - Upload Timestamp
  - Analysis Status (`Analyzed`, `Uploaded`, `Processing`, `Failed`)
  - Extracted Keywords count
  - Detected Legal Entities count
  - Actions: "View", "Results", "+ Analyze"
- Real-time search by document name or ID.
- Status dropdown filter (`All`, `Analyzed`, `Uploaded`, `Processing`, `Failed`).
- Sort controls (`Newest Uploads`, `Oldest First`, `Document Title A-Z`).

### 4.6 ASTMA Evaluation Workspace (`EvaluationPage.jsx`)
- Adheres strictly to scientific integrity: **zero fabricated charts or artificial precision/recall metrics**.
- States clearly: *"Evaluation workspace will appear here once benchmark data is available."*
- Explains the ASTMA Information Retrieval evaluation protocol: Precision ($P = \frac{TP}{TP + FP}$), Recall ($R = \frac{TP}{TP + FN}$), and F1 Harmonic Mean.

### 4.7 Enterprise Security & Administration (`AdminAuditPage.jsx`)
- Visual refinement to harmonize with the Phase 7 legal design system.
- Tab 1: **Governance Audit Ledger** with multi-parameter filtering (Action, Status, User ID), refresh control, and pagination.
- Tab 2: **User Management & RBAC** with real-time role adjustments (`USER`, `ANALYST`, `ADMIN`) and account activation/deactivation controls.

---

## 5. API Additions

To support streaming and previewing documents in the interactive viewer while preserving strict Phase 6 document ownership boundaries, the following endpoint was added:

### `GET /api/v1/documents/{document_id}/file`
- **Purpose:** Streams the original uploaded document for inline PDF viewing or file download.
- **Authorization:** Protected with `get_current_user` and `check_document_access`. Non-admin users cannot stream documents belonging to other users (returns `HTTP 403 Forbidden`).
- **Audit Logging:** Records `DOCUMENT_VIEW` in the append-only audit trail with `download=true/false` context and client IP.
- **Response:** `FileResponse` with `application/pdf` or `application/vnd.openxmlformats-officedocument.wordprocessingml.document`.

---

## 6. Verification & Test Results

### 6.1 Backend Pytest Regression Suite
Complete backend test suite executed:
```
platform win32 -- Python 3.14.3, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\tejas\PBL project (ES,ASTMA,ITPM)\backend

tests\test_audit.py .......                                              [  8%]
tests\test_auth.py ..............                                        [ 24%]
tests\test_authorization.py ..........                                   [ 36%]
tests\test_database.py ............                                      [ 50%]
tests\test_document_ingestion.py .............                           [ 65%]
tests\test_entity_extraction.py ..............                           [ 82%]
tests\test_health.py ...                                                 [ 85%]
tests\test_keyword_extraction.py ............                            [100%]

======================= 85 passed, 1 warning in 16.93s ========================
```
**Result:** 85/85 tests passing. Zero regressions across authentication, RBAC, audit logging, ingestion, keyword extraction, and entity extraction.

### 6.2 Frontend Production Build
Executed `npm run build` in `frontend/`:
```
vite v5.4.21 building for production...
✓ 1559 modules transformed.
dist/index.html                   0.94 kB │ gzip:  0.54 kB
dist/assets/index-CJgLRn7G.css   31.72 kB │ gzip:  6.07 kB
dist/assets/index-CkawjgCy.js   337.42 kB │ gzip: 94.24 kB
✓ built in 17.88s
```
**Result:** Clean build with 0 TypeScript/ESLint errors and 0 missing imports.

### 6.3 Programmatic E2E Verification Suite (`verify_phase7_e2e.py`)
Executed full multi-tenant flow against live daemon:
1. `GET /health` and `GET /api/v1/` returned 200 OK.
2. Frontend dev server verified running on `http://localhost:5173`.
3. Practitioner authenticated with JWT issued for `demo@lexextract.local` (Role: `USER`).
4. Uploaded legal brief `Delhi_HC_Commercial_Suit_402.pdf` (39 words).
5. Document text and structured pages retrieved successfully.
6. File stream endpoint (`/file`) served raw PDF payload (642 bytes, `application/pdf`).
7. Analysis executed producing 20 keywords and 8 legal entities (e.g. `HIGH COURT OF DELHI` [COURT, 0.98 confidence], `Section 11` [SECTION, 0.95 confidence], `Arbitration and Conciliation Act` [ACT, 0.95 confidence]).
8. Cross-role boundary enforcement verified: Practitioner attempt to query `/api/v1/admin/audit-logs` and `/api/v1/users/` blocked with `HTTP 403 Forbidden`.
9. Administrator authenticated with JWT issued for `admin@lexextract.local` (Role: `ADMIN`).
10. Governance audit ledger inspected (64 immutable events recorded).
11. System user directory inspected (5 registered practitioners).

---

## 7. Academic Mapping

This implementation maps directly to concepts established in `LEXEXTRACT_BLUEPRINT.md`:

### 1. Enterprise Systems (ES)
- **Three-Tier Enterprise Architecture:** Clear separation between Presentation Tier (React/Tailwind AppShell), Logic Tier (FastAPI/spaCy NLP Services), and Data Tier (SQLAlchemy/SQLite relational store).
- **Stateless Bearer Authentication & Non-Repudiation:** Cryptographic PyJWT tokens paired with an immutable audit ledger (`audit_logs`) tracking resource access with client IP addresses.
- **Enterprise Tenant Isolation:** Document ownership verification (`check_document_access`) ensures strict data boundaries across enterprise practitioners.

### 2. Advanced Software Testing & Mining Architecture (ASTMA)
- **Text Mining Visual Overlays:** Visual representation of multi-word statistical n-grams (RAKE), corpus-frequency weights (TF-IDF), and statutory domain lexicons.
- **Hybrid Named Entity Mining:** Entity exploration visualizes rule-based extraction (regular expression grammars for Section/Case references) and statistical transformer/spacy NER for Person and Organization mentions.
- **Information Retrieval Evaluation Methodology:** Precision, Recall, and F1-score mathematical definitions provided for viva defense.

### 3. IT Project Management (ITPM)
- **Role-Based Governance (RBAC):** Principle of Least Privilege enforcing role hierarchy (`USER` < `ANALYST` < `ADMIN`).
- **Defensive Engineering & Error Resilience:** Standardized error boundaries (`ErrorState`, `EmptyState`, `LoadingState`) preventing blank screens or unhandled exceptions.
- **Traceability & Phase Boundaries:** Strict milestone tracking where Phase 7 delivers the complete user interface without prematurely commencing Phase 8.

---

## 8. Limitations & Phase 8 Boundary

- **Character Offset Coordinate Navigation:** Highlighting in Phase 7 operates via safe token matching and regex boundary identification. Page-level bounding-box pixel coordinates and synchronized PDF highlight overlays are scheduled for **Phase 8**.
- **OCR Engine:** Image-only scanned PDFs require searchable text layers; optical character recognition is deferred.
- **Benchmark Corpus Execution:** Automated precision/recall scoring against gold-standard annotated documents will be activated in **Phase 9**.

---

## 9. Conclusion

Phase 7 is **COMPLETE AND VERIFIED**.
Phase 8 has **NOT BEEN STARTED**.
