# LexExtract — Application Screenshot Catalog & Visual Index

This catalog indexes key graphical views of the LexExtract application, describing the layout, functional purpose, and verified user interactions for each screen.

---

### Figure 5.1 — User Authentication & Identity Portal (`/login`)
- **Title:** Practitioner Authentication Portal
- **Route:** `http://localhost:5173/login`
- **Functional Purpose:** Provides secure user authentication using email and password.
- **Key Visual Elements:**
  - Split-pane layout with legal-tech branding on the left and login form on the right.
  - Role switcher chips (`Demo (User / Lawyer)`, `Analyst`, `Admin`) for demonstration.
  - Form validation with error alert banners for invalid credentials.
- **What It Demonstrates:** Stateless RFC 7519 JWT session issuance and Argon2id password verification.

---

### Figure 5.2 — Legal Operational Analytics Dashboard (`/dashboard`)
- **Title:** Legal Operations Dashboard
- **Route:** `http://localhost:5173/dashboard`
- **Functional Purpose:** Serves as the primary operational hub for practitioners upon login.
- **Key Visual Elements:**
  - Four top-level metric cards: Cataloged Briefs, Total Words Processed, Completed Analyses, and Extracted Legal Entities.
  - Quick Action cards: "New Document Intake" and "ASTMA Evaluation Benchmark".
  - Recent Briefs Table displaying document names, word counts, upload timestamps, and action buttons.
- **What It Demonstrates:** Dynamic data aggregation across relational database records.

---

### Figure 5.3 — Document Intake & Preprocessing Zone (`/documents`)
- **Title:** Document Ingestion & Validation Canvas
- **Route:** `http://localhost:5173/documents`
- **Functional Purpose:** Handles drag-and-drop file upload for PDF and DOCX legal documents.
- **Key Visual Elements:**
  - Drag-and-drop dropzone with MIME-type format indicators (`.pdf`, `.docx` up to 25 MB).
  - Client-side size and extension validation guards.
  - Ingestion progress indicators and immediate metadata extraction cards (word count, page count, SHA-256 hash).
- **What It Demonstrates:** Layout-aware text extraction and citation-preserving normalization.

---

### Figure 5.4 — Analysis Results Overview (`/analysis/:id`)
- **Title:** Legal Intelligence Analysis Header & Summary
- **Route:** `http://localhost:5173/analysis/:id`
- **Functional Purpose:** Displays processing latency and extraction statistics for an analyzed brief.
- **Key Visual Elements:**
  - Top header badges displaying total keywords extracted, total entities extracted, and processing latency in seconds.
  - Action buttons: "Open in Document Viewer" and "Re-run Analysis".
  - Tab navigation switching between "Top Legal Keywords" and "Extracted Legal Entities".
- **What It Demonstrates:** Completion of the tri-model keyword scoring and hybrid NER pipeline.

---

### Figure 5.5 — Top Legal Keyword Explorer (`/analysis/:id` — Tab 1)
- **Title:** Ranked Keyword Explorer & Domain Filters
- **Route:** `http://localhost:5173/analysis/:id`
- **Functional Purpose:** Allows practitioners to explore and filter ranked keywords extracted from the document.
- **Key Visual Elements:**
  - Category filter chips (`All`, `Contract`, `Litigation`, `Corporate`, `Property`, `Statutory`, `IP`, `Constitutional`).
  - Search input with real-time text matching.
  - Ranked keyword cards displaying final composite score, domain category badge, frequency, and rank.
- **What It Demonstrates:** The tri-model weighted fusion formula ($0.35 \text{ TF-IDF} + 0.35 \text{ RAKE} + 0.30 \text{ Lexicon}$).

---

### Figure 5.6 — Legal Entity Explorer (`/analysis/:id` — Tab 2)
- **Title:** Typed Legal Entity Explorer & Confidence Scoring
- **Route:** `http://localhost:5173/analysis/:id`
- **Functional Purpose:** Displays named entities categorized across 13 specialized legal classes.
- **Key Visual Elements:**
  - Entity category filter dropdown (`COURT`, `STATUTE`, `SECTION`, `CASE_NUMBER`, `LEGAL_ROLE`, `MONETARY_VALUE`, etc.).
  - Entity cards showing normalized text, category badge, extraction source tag (`spacy`, `regex`, `gazetteer`, `hybrid`), and confidence score (e.g., $0.98$).
- **What It Demonstrates:** Hybrid NER combining statistical linguistic models with symbolic legal gazetteers.

---

### Figure 5.7 — Interactive Legal Document Viewer (`/documents/:id`)
- **Title:** Interactive Document Viewer with Multi-Layer Token Highlighting
- **Route:** `http://localhost:5173/documents/:id`
- **Functional Purpose:** Provides full document text display with synchronized visual highlight overlays.
- **Key Visual Elements:**
  - Sticky control toolbar with layer toggle buttons: `All Overlays`, `Keywords Only`, `Entities Only`, `Clean Plain Text`.
  - Color-coded text highlighting: Amber for keywords; Purple, Blue, and Green badges for typed entities.
  - Page-by-page document navigation for multi-page PDF briefs.
- **What It Demonstrates:** Character-offset mapping of extracted entities directly to the original legal text.

---

### Figure 5.8 — Institutional Repository History (`/history`)
- **Title:** Brief Repository & Historical Archive
- **Route:** `http://localhost:5173/history`
- **Functional Purpose:** Provides practitioners with a searchable archive of previously ingested documents.
- **Key Visual Elements:**
  - Searchable brief table with columns for Document Name, Format, File Size, Word Count, Upload Date, and Status.
  - Action buttons for downloading original binary files and opening existing analyses.
- **What It Demonstrates:** Relational persistence and document ownership filtering.

---

### Figure 5.9 — ASTMA Empirical Evaluation Console (`/evaluation`)
- **Title:** Information Retrieval Evaluation & Benchmarking Console
- **Route:** `http://localhost:5173/evaluation`
- **Functional Purpose:** Enables legal analysts and examiners to execute reproducible benchmark evaluations against ground truth.
- **Key Visual Elements:**
  - Corpus summary banner (12 legal documents, 3,875 words, 129 gold keywords, 157 gold entities).
  - Macro and Micro scorecards for Precision, Recall, and F1-score with educational formula cards.
  - Algorithm Ablation Comparison Table (TF-IDF vs. RAKE vs. LexExtract Hybrid).
  - Top-K Cutoff Performance Table (Top-5, Top-10, Top-20).
  - Document-level breakdown table and "Run Benchmark" button with live loading state.
- **What It Demonstrates:** Unmanipulated empirical IR evaluation with zero-division arithmetic safeguards.

---

### Figure 5.10 — Taxonomic Error Analysis Inspector (`/evaluation` — Tabs)
- **Title:** Error Analysis & Classification Inspector
- **Route:** `http://localhost:5173/evaluation` (Error Analysis Section)
- **Functional Purpose:** Provides granular inspection of extraction failure modes for academic analysis.
- **Key Visual Elements:**
  - Tabbed error inspection: "Keyword Errors (FP / FN)" and "Entity Errors (FP / FN / Category Mismatches)".
  - Partitioned tables displaying False Positives (over-generated phrases), False Negatives (omitted concepts), and Entity Category Mismatches.
- **What It Demonstrates:** Transparent failure mode analysis and academic explainability.

---

### Figure 5.11 — Governance Audit Ledger (`/admin/audit`)
- **Title:** Institutional Governance Audit Ledger
- **Route:** `http://localhost:5173/admin/audit`
- **Functional Purpose:** Provides administrators with an immutable audit trail of system events for compliance.
- **Key Visual Elements:**
  - Paginated audit log table displaying Action enums (`LOGIN`, `DOCUMENT_UPLOAD`, `ANALYSIS_START`, `ANALYSIS_COMPLETE`, `UNAUTHORIZED_ACCESS`).
  - Metadata columns for User ID, Target Resource, Status (`SUCCESS` / `FAILURE`), Client IP address, and Timestamp.
  - Filter controls for Action type and Status.
- **What It Demonstrates:** Enterprise non-repudiation security and least-privilege governance.
