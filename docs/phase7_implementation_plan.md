# Phase 7 Implementation Plan — Professional Legal UI, Document Viewer & Interactive Analysis

**Project:** LexExtract — Legal Document Keyword & Entity Extractor  
**Phase:** Phase 7 — Professional Legal UI, Document Viewer & Interactive Analysis  
**Status:** Architecture & Design Specification  

---

## 1. Executive Summary & Objective

Phase 7 delivers a credible, enterprise-grade user interface for LexExtract, transforming it into a high-trust **Legal Technology & Document Intelligence Platform**. Rather than looking like a generic AI SaaS or a template-based startup dashboard, LexExtract's visual and interactive language will mirror sophisticated institutional legal research environments (such as Westlaw, LexisNexis, Relativity, or DISCO).

### Key Architectural Pillars:
1. **Credible Legal Design Language:** Deep Navy (`#0A192F`), Warm Parchment (`#F9F8F5`), Off-White, Burgundy (`#722F37`), and Muted Gold (`#C5A059`) with restrained borders, editorial serif headings, and high-contrast typography.
2. **Institutional Application Shell:** Dual-pane layout featuring an authoritative legal-tech Sidebar with hierarchical navigation (`Dashboard`, `Documents [New Analysis, History]`, `Analysis Results`, `ASTMA Evaluation`, `Administration [Users, Audit Trail]`), persistent top bar with operational status, and responsive tablet/mobile collapsing.
3. **Executive Legal Dashboard:** Powered purely by **real backend data** (`listDocuments()`, document analysis runs, extracted entity summaries, system health), showing authentic document counts, word totals, entity volumes, and a recent document table with immediate actions.
4. **Intake & Upload Workflow:** Drag-and-drop document intake for `.pdf` and `.docx` with instant client-side format/size validation, real file metadata inspection, and indeterminate multi-step processing indicator without artificial progress percentages.
5. **Interactive Dual-Mode Document Viewer:**
   - **Original Document Inspection:** Native PDF inline rendering and download streaming via an authenticated backend file endpoint (`GET /api/v1/documents/{id}/file`).
   - **Structured Legal Text View:** Layout-aware text rendering by page and paragraph with **Safe Keyword & Entity Highlighting** (color-coded, non-destructive, with offset/case-insensitive matching).
   - **Interactive Context Inspector:** Clicking any highlighted keyword or entity immediately reveals its type, confidence score, source provenance (`spacy`, `regex`, `dictionary`, `hybrid`), and occurrence count in a dedicated legal details drawer.
6. **Unified Keyword & Entity Analysis Workspace:**
   - Tabbed results matrix with live search (`Search keywords or entities...`).
   - Keyword table with multi-factor score breakdown (TF-IDF, RAKE, Lexicon, Final Score) and category filters.
   - Entity explorer grouped by genuine backend legal entity types (`COURT`, `ACT`, `SECTION`, `CASE_REFERENCE`, `CONTRACT`, `LEGAL_ROLE`, `PERSON`, `ORGANIZATION`, `DATE`, `MONEY`, etc.).
7. **Document Repository & History Archive:** Filterable, searchable table displaying past documents, analysis statuses, word counts, and direct action triggers (`View Results`, `Open Document`, `Analyze Again`).
8. **Preserved Administrative Governance:** Seamless styling alignment of `AdminAuditPage.jsx`, `LoginPage.jsx`, and `RegisterPage.jsx` preserving all Phase 6 RBAC safeguards and audit trail capabilities.

---

## 2. Design System & Typography

### 2.1 Color Palette
- **Institutional Navy:** `#0A192F` (Primary Header, Active Sidebar, Primary Buttons)
- **Deep Slate Navy:** `#1E293B` (Sidebar background, card headers)
- **Warm Parchment / Canvas:** `#F8F7F4` (Application background, document canvas)
- **Pure Document White:** `#FFFFFF` (Document card surfaces, tables, paper simulation)
- **Editorial Burgundy:** `#722F37` (Accent buttons, statutory highlights, key metric pills)
- **Muted Antique Gold:** `#C5A059` (Legal badges, borders, rating stars, hover highlights)
- **Legal Charcoal:** `#1F2937` (Primary body text, legal prose)
- **Muted Slate:** `#64748B` (Secondary text, metadata labels, footnotes)
- **Subtle Legal Borders:** `#E2E8F0` and `#CBD5E1` (Clean 1px dividing lines, zero blur)

### 2.2 Typography
- **Headings & Display:** Editorial Serif (`font-serif`: Georgia, Cambria, Times New Roman) conveying formal institutional authority.
- **Data Tables & Controls:** Clean, high-legibility Sans-Serif (`font-sans`: Inter, system-ui) with uppercase tracked labels (`tracking-wider`, `text-xs font-semibold`).
- **Statutory Codes & Tokens:** Clean Monospace (`font-mono`) for hashes, IDs, and raw text coordinates.

---

## 3. UI Component Architecture

```
frontend/src/
├── components/
│   ├── layout/
│   │   ├── AppShell.jsx           # Main wrapper (TopBar + Sidebar + Content area)
│   │   ├── TopBar.jsx             # System status, breadcrumb trail, backend health
│   │   └── Sidebar.jsx            # Hierarchical legal navigation & user profile
│   ├── common/
│   │   ├── PageHeader.jsx         # Uniform title, subtitle, and primary actions
│   │   ├── StatCard.jsx           # Clean institutional KPI card (no fake charts)
│   │   ├── StatusBadge.jsx        # Semantic status pills (Analyzed, Uploaded, Failed)
│   │   ├── EmptyState.jsx         # Professional legal empty state with CTA
│   │   ├── LoadingState.jsx       # Skeleton/spinner with descriptive legal messages
│   │   └── ErrorState.jsx         # User-friendly error card with retry/back options
│   └── viewer/
│       ├── LegalTextHighlighter.jsx # Text highlighter for keywords & entities
│       └── EntityContextDrawer.jsx  # Inspection panel for clicked entity/keyword
├── pages/
│   ├── DashboardPage.jsx          # Real KPIs, recent docs, primary upload CTA
│   ├── NewAnalysisPage.jsx        # Document intake, file validation, analysis trigger
│   ├── AnalysisResultsPage.jsx    # Dual-tabbed results, search, filters, score detail
│   ├── DocumentViewerPage.jsx     # Split-screen text/PDF viewer with highlighting
│   ├── DocumentHistoryPage.jsx    # Searchable archive of all practitioner documents
│   ├── EvaluationPage.jsx         # ASTMA IR evaluation benchmarking
│   ├── AdminAuditPage.jsx         # Preserved governance audit ledger & user admin
│   ├── LoginPage.jsx              # Redesigned with demo quick-fill credentials
│   └── RegisterPage.jsx           # Consistent practitioner registration
```

---

## 4. Backend API Extensions (Minimal & Safe)

To power the Document Viewer and ensure zero mock/placeholder data:
1. **Document File Streaming Endpoint (`GET /api/v1/documents/{document_id}/file`):**
   - Location: `backend/app/api/v1/endpoints/documents.py`
   - Authorization: Enforces `check_document_access(doc, current_user, db)`.
   - Behavior: Serves the uploaded PDF or DOCX file with `Content-Disposition: inline; filename="..."` and proper MIME types (`application/pdf`, `application/vnd.openxmlformats-officedocument.wordprocessingml.document`).
   - Security: Prevents directory traversal, validates stored file existence, and records `DOCUMENT_VIEW` in `AuditLog`.
2. **Entity Schema Enriched with Coordinate Offsets:**
   - Location: `backend/app/schemas/analysis.py` (`EntityItem`)
   - Adds `id`, `start_position`, `end_position`, and `page_number` to enable accurate in-text highlighting.

---

## 5. Navigation & Role-Based Visibility

| View | Path / ID | Roles Permitted | Navigation Hierarchy |
| :--- | :--- | :---: | :--- |
| **Dashboard** | `dashboard` | `USER`, `ANALYST`, `ADMIN` | Top-level |
| **New Analysis** | `new_analysis` | `USER`, `ANALYST`, `ADMIN` | Under `Documents` |
| **Document History** | `history` | `USER`, `ANALYST`, `ADMIN` | Under `Documents` |
| **Analysis Results** | `results` | `USER`, `ANALYST`, `ADMIN` | Top-level |
| **Document Viewer** | `viewer` | `USER`, `ANALYST`, `ADMIN` | Top-level / Contextual |
| **ASTMA Evaluation** | `evaluation` | `ANALYST`, `ADMIN` | Specialized Analytical |
| **System Users** | `admin_users` | `ADMIN` only | Under `Administration` |
| **Audit Ledger** | `admin_audit` | `ADMIN` only | Under `Administration` |

---

## 6. Document Viewer & Highlighting Logic

### 6.1 Safe Highlighting Strategy
- In legal research software, misaligned highlights undermine practitioner confidence.
- Highlighting supports both exact character offset slicing (when coordinates match) and regex token boundary matching (`\b<term>\b`) to highlight:
  - **Keywords:** Amber/Gold subtle underline and tint (`bg-amber-100 text-amber-900 border-b border-amber-400`).
  - **Courts:** Purple tint (`bg-purple-100 text-purple-900 border-b border-purple-400`).
  - **Statutes / Sections:** Blue tint (`bg-blue-100 text-blue-900 border-b border-blue-400`).
  - **Monetary Values:** Emerald tint (`bg-emerald-100 text-emerald-900 border-b border-emerald-400`).
  - **Dates:** Slate/Gray tint (`bg-slate-200 text-slate-800 border-b border-slate-400`).
  - **Persons / Parties:** Rose/Burgundy tint (`bg-rose-100 text-rose-900 border-b border-rose-400`).

### 6.2 Interactive Entity Selection
Clicking any highlight in the text or clicking an entity chip in the results table synchronizes the state:
- Highlights the term with an active focus ring.
- Opens the **Entity Context Drawer** displaying:
  - Normalized Title & Category
  - Extraction Source (`Rule-based Regex`, `spaCy Statistical NER`, `Domain Gazetteer`, `Hybrid Consensus`)
  - Mathematical Confidence Score (e.g. `0.98`)
  - Page and paragraph occurrence context

---

## 7. Testing & Verification Strategy

1. **Backend Tests:** Run complete regression suite (`pytest tests/`), ensuring all 85 existing tests pass + any new file streaming tests pass.
2. **Frontend Production Build:** Execute `npm run build` and ensure clean Vite bundling without warnings.
3. **Live Verification Script:** Extend E2E script to verify document file streaming and coordinate schema integrity.
4. **Browser Verification:**
   - Authenticated login as lawyer, analyst, and admin.
   - Sidebar navigation and role restriction enforcement.
   - Dashboard statistics derived from live database records.
   - Document upload, text ingestion, and keyword/entity analysis execution.
   - Document Viewer split-screen inspection with active highlighting.
   - Document History archive search, filtering, and direct result navigation.
   - Admin audit trail and user management functionality.

---

## 8. Phase 7 Acceptance Criteria

- [ ] Professional application shell with top bar and collapsible legal-tech sidebar.
- [ ] Role-restricted menu items adhering to backend authorization.
- [ ] Real-data executive dashboard (genuine document counts, word counts, entity totals, and recent documents table).
- [ ] Professional document intake with file validation and clear processing feedback.
- [ ] Tabbed analysis results matrix with live search and category filters.
- [ ] Split-screen document viewer with layout-aware text streaming and inline PDF support.
- [ ] Non-destructive keyword and entity highlighting with interactive detail drawer.
- [ ] Searchable, filterable document history archive.
- [ ] Zero fake data, zero fake progress percentages, zero fake charts.
- [ ] Responsive layouts for desktop and tablet screens.
- [ ] All 85+ backend tests pass with zero regressions.
- [ ] Clean production frontend build (`vite build`).
- [ ] Verified in live browser.
- [ ] Phase 8 is NOT started.
