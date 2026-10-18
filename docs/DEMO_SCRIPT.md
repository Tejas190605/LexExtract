# LexExtract — Final Project Demonstration Script (Viva Guide)

**Demonstration Duration:** 8–10 Minutes  
**Demonstrators:** Development Team  
**Audience:** Academic Evaluators, Professors & External Examiners  
**Application URL:** `http://localhost:5173` (Frontend) | `http://127.0.0.1:8000` (Backend API)

---

## 1. Step-by-Step Viva Presentation Workflow

### Step 1: System Introduction & Architecture (Minute 0:00 – 1:30)
- **Action:** Open browser at `http://localhost:5173/login`.
- **Narration:**
  > *"Respected evaluators, we present **LexExtract**, an intelligent, domain-adapted Information Extraction and Retrieval system for unstructured legal documents. Built on a Three-Tier Enterprise Architecture, LexExtract couples a React 18 / Tailwind CSS presentation tier with an asynchronous FastAPI application tier and SQLAlchemy relational persistence. It enforces stateless RFC 7519 JWT authentication, strict Role-Based Access Control, and institutional non-repudiation audit logging."*

### Step 2: Authentication & Operational Dashboard (Minute 1:30 – 2:30)
- **Action:** Click the preset button **"Demo (User / Lawyer)"** (`demo@lexextract.local` / `User@Lex2026!`), then click **"Sign In to Portal"**.
- **Observation:** Arrive at `/dashboard`.
- **Narration:**
  > *"Upon authentication, we arrive at the Legal Analytics Dashboard. Here, practitioners can view operational statistics: total documents cataloged, words processed, completed analyses, and legal entities identified. The recent briefs table provides immediate status tracking."*

### Step 3: Document Intake & Preprocessing (Minute 2:30 – 4:00)
- **Action:** Click **"New Intake & Upload"** in the sidebar. Drag or browse to `sample_documents/sample_contract.pdf` (or `sample_legal_notice.docx`). Click **"Ingest & Process Document"**.
- **Observation:** Instant upload with word count and page count calculated.
- **Narration:**
  > *"Our document ingestion engine employs layout-aware multi-format parsing. PyMuPDF handles complex PDF streams, while python-docx processes Microsoft Word documents. Unlike generic parsers, our preprocessor preserves critical legal syntax—specifically statutory subsection parentheses like Section 11(6)—avoiding destructive stripping."*

### Step 4: NLP Pipeline Execution & Intelligence Explorer (Minute 4:00 – 5:30)
- **Action:** Click **"Run Analysis"**. Inspect the Analysis Results page (`/analysis/:id`).
- **Observation:**
  - Badges show total keywords (e.g. 20) and extracted entities (e.g. 30).
  - Select category filter **"Procedure"** or search for `"notice"`.
  - Click the **"Extracted Legal Entities"** tab; filter by `COURT` or `ORGANIZATION`.
- **Narration:**
  > *"Our extraction engine does not rely on simple frequency counting. For keywords, we implement a tri-model weighted fusion combining TF-IDF (35%), RAKE co-occurrence graph scoring (35%), and a 1,200-term legal lexicon (30%). For entities, we fuse statistical spaCy NER with symbolic legal gazetteers and regex matchers to isolate specialized categories such as Courts, Statutes, Sections, and Case Numbers."*

### Step 5: Interactive Document Viewer with Token Highlighting (Minute 5:30 – 7:00)
- **Action:** Click **"Open In Document Viewer"** (`/documents/:id`).
- **Observation:**
  - Document text renders in the primary pane.
  - Cycle through the layer modes: **All Overlays**, **Keywords Only**, **Entities Only**, and **Clean Plain Text**.
- **Narration:**
  > *"The interactive Document Viewer maps token offsets directly to the underlying legal text. Users can toggle visualization layers to highlight keywords in amber and typed entities in category-specific badges (e.g., Purple for Courts, Blue for Statutes, Green for Monetary Values)."*

### Step 6: ASTMA Empirical Evaluation & Benchmark Console (Minute 7:00 – 8:30)
- **Action:** Log out and log in as Admin (`admin@lexextract.local` / `Admin@Lex2026!`). Click **"ASTMA Benchmark"** in the sidebar (`/evaluation`).
- **Action:** Click **"Run Benchmark"**.
- **Observation:** Benchmark executes across 12 legal documents in ~10 seconds. Live scorecards update showing Precision ($P$), Recall ($R$), and $F_1$ scores for keywords and entities, alongside algorithm ablation tables and Top-K retrieval cutoffs.
- **Narration:**
  > *"For academic evaluation under ASTMA, we built an empirical evaluation engine that benchmarks extraction pipelines against a curated ground-truth corpus of 12 legal documents containing 129 gold keywords and 157 gold entities. We calculate unmanipulated Precision, Recall, and F1 scores with zero-division safeguards. Notice the ablation study: our hybrid model outperforms standalone TF-IDF and RAKE, and the Top-K table demonstrates higher precision in the top-5 candidate rankings."*

### Step 7: Governance Audit Ledger & Conclusion (Minute 8:30 – 10:00)
- **Action:** Click **"Governance Audit Ledger"** in the sidebar (`/admin/audit`).
- **Observation:** Table of immutable security events showing actions (`LOGIN`, `DOCUMENT_UPLOAD`, `ANALYSIS_COMPLETE`, `BENCHMARK_RUN`), actor IDs, client IPs, and timestamps.
- **Narration:**
  > *"Finally, the Governance Audit Ledger provides tamper-evident tracking of all critical operations, satisfying enterprise security requirements. In conclusion, LexExtract delivers a robust, tested, and empirically evaluated legal information extraction platform with 98 passing backend tests and a production-ready frontend."*
