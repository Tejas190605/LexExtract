# LexExtract — Final Project Presentation (PPT Outline)

## Visual Identity & Design Guidelines
- **Color Palette:**
  - Primary Background: Warm Parchment / Crisp Off-White (`#F8FAFC`)
  - Primary Headers & Accent: Deep Navy Blue (`#1E3A8A`)
  - Accent / Highlights: Muted Gold (`#D97706`) & Deep Burgundy (`#881337`)
  - Text: Dark Charcoal Slate (`#1E293B`)
- **Typography:** Inter / Roboto (Clean sans-serif with high contrast hierarchy)
- **Design Philosophy:** Authoritative Legal-Tech Editorial; clean bullet points, structured comparison tables, and diagram placeholders. No generic stock imagery, no neon gradients, no AI clichés.

---

### SLIDE 1: Title & Project Identity
- **Header:** LEXEXTRACT
- **Sub-header:** Intelligent Legal Document Keyword & Entity Extraction System
- **Context:** Project-Based Learning (PBL) Capstone Project
- **Disciplinary Pillars:**
  - Enterprise Systems (ES)
  - Advanced Social, Text and Media Analytics (ASTMA)
  - IT Project Management (ITPM)
- **Author:** B.Tech Computer Engineering Candidates
- **Institution:** Faculty of Technology & Engineering
- **Date:** Academic Session 2025–2026

---

### SLIDE 2: Project Motivation & Industry Context
- **The Challenge:** Legal practitioners and compliance teams review hundreds of pages of commercial contracts, arbitration pleadings, and judgments daily.
- **The Problem:**
  - High manual billable hours spent on routine clause triage and statutory lookup.
  - Generic NLP normalizers damage statutory citations (e.g. converting `Section 11(6)` to `section 11 6`).
  - Standard NER tools misclassify specialized courts as generic commercial organizations.
- **The Opportunity:** A domain-specific, explainable extraction pipeline providing automated legal concept extraction and reproducible IR evaluation.

---

### SLIDE 3: Problem Statement & Research Gap
- **Technical Bottlenecks in Legal NLP:**
  - **Punctuation Sensitivity:** Legal statutory citations require parenthesis preservation.
  - **Multi-Word Compounds:** Concepts like `liquidated damages` or `ad interim injunction` lose meaning if parsed as single unigrams.
  - **Judicial Hierarchy:** Generic models fail to distinguish Apex Courts, High Courts, and Tribunals from business companies.
- **Existing Market Limitations:**
  - Commercial legal-tech software is proprietary, subscription-locked, and operates as an unexplainable "black box".
  - Absence of lightweight, verifiable academic benchmarks for student evaluation.

---

### SLIDE 4: Project Objectives
- **Decoupled Architecture:** Build a Three-Tier enterprise platform (React 18 + FastAPI + SQLite/PostgreSQL).
- **Citation-Aware Processing:** Ingest PDF and DOCX files while preserving statutory subsections and paragraph structure.
- **Tri-Model Keyword Extraction:** Combine TF-IDF (35%), RAKE graph scoring (35%), and a 1,200-term legal lexicon (30%).
- **Hybrid Legal NER:** Extract 13 legal entity classes using statistical spaCy NER and symbolic legal gazetteers.
- **Security & Governance:** Implement stateless JWT authentication, Argon2id hashing, RBAC, cross-user document isolation, and an immutable audit ledger.
- **Empirical IR Evaluation:** Provide an ASTMA benchmarking engine calculating Precision, Recall, F1, and Top-K metrics over a curated 12-document corpus.

---

### SLIDE 5: System Architecture
- **Three-Tier Architecture:**
  - **Presentation Tier:** React 18 SPA, Vite, Tailwind CSS, Lucide Icons.
  - **Application Tier:** Asynchronous FastAPI REST service, Pydantic validation, Python 3.12+.
  - **Data Tier:** SQLite with SQLAlchemy 2.0 ORM (migration-ready for PostgreSQL), local SHA-256 validated storage.
- **Security Model:**
  - Stateless RFC 7519 JWT sessions (`HS256`).
  - Argon2id password hashing.
  - Document ownership guards blocking cross-user inspection (HTTP 403 Forbidden).
- *[Visual: Three-Tier Component Diagram from docs/SYSTEM_ARCHITECTURE.md]*

---

### SLIDE 6: Document Ingestion & Citation Preprocessing
- **Multi-Format Ingestion:**
  - PDF: PyMuPDF (`fitz`) parses text blocks and page coordinates.
  - DOCX: `python-docx` traverses XML paragraphs and data tables.
- **Integrity Validation:** MIME-type validation and SHA-256 cryptographic hashing to detect duplicate uploads.
- **Citation Preservation:**
  - Normalizes whitespace without stripping statutory notation.
  - Preserves subsection notation (e.g., `Section 11(6)` and `Article 226(1)`).
  - Extended legal stopword filtering retaining legally discriminative prepositions (`whereas`, `hereinafter`, `pursuant to`).

---

### SLIDE 7: Tri-Model Keyword Extraction Engine
- **Candidate Generation:** N-gram sliding windows ($n \in \{1, 2, 3\}$) bounded by punctuation.
- **Tri-Model Scoring:**
  - **TF-IDF (35%):** Evaluates term relevance against a reference legal collection.
  - **RAKE Graph Scoring (35%):** Analyzes word co-occurrence matrices across syntactic delimiters ($\text{deg}(w)/\text{freq}(w)$).
  - **Domain Lexicon (30%):** Matches terms against a curated dictionary of 1,200+ legal terms across 7 categories.
- **Weighted Rank Fusion:**
  $$\text{Final Score} = 0.35 \cdot S_{\text{TF-IDF}} + 0.35 \cdot S_{\text{RAKE}} + 0.30 \cdot S_{\text{Lexicon}}$$
- **Output:** Top-20 ranked keywords stored with normalized scores and domain categories.

---

### SLIDE 8: Hybrid Named Entity Recognition (NER)
- **Statistical Foundation:** `spaCy` (`en_core_web_sm`) detects standard entities (`PERSON`, `ORG`, `DATE`, `MONEY`, `LOCATION`).
- **Domain Legal Rules & Gazetteers:** Custom regex and dictionary matchers detect:
  - `COURT`: Supreme Court of India, State High Courts, Tribunals.
  - `STATUTE` & `SECTION`: Acts of Parliament, Sections, Subsections.
  - `CASE_NUMBER`: Writ Petitions, Commercial Suits, Company Appeals.
  - `LEGAL_ROLE`: Petitioner, Respondent, Appellant, Lessor, Lessee.
  - `JURISDICTION`: Seat of Arbitration, Territorial Jurisdiction.
- **Precedence Arbitration:** Domain rules take precedence over generic statistical tags with character offset tracking for visual highlighting.

---

### SLIDE 9: Interactive UI & Document Viewer
- **Operational Dashboard:** Real-time metrics tracking cataloged briefs, words processed, completed analyses, and entities identified.
- **Keyword & Entity Explorers:** Category filtering, dynamic search bar, and confidence badges.
- **Interactive Document Viewer:**
  - Color-coded visual highlighting mapped to token offsets.
  - Multi-layer visual toggles: All Overlays, Keywords Only, Entities Only, Clean Plain Text.
- **Repository History:** Complete brief catalog with file metadata, status chips, and download actions.
- *[Visual: Screenshots of Document Viewer and Analysis Results]*

---

### SLIDE 10: ASTMA Empirical Evaluation & Benchmark
- **Curated Benchmark Corpus:** 12 documents, 3,875 words, 129 gold keywords, 157 gold entities across 6 legal genres.
- **IR Evaluation Methodology:**
  - Standard formulas: Precision ($P$), Recall ($R$), and F1-score ($F_1$).
  - Zero-division arithmetic safety: Returns `0.0` when denominators equal zero.
  - Joint entity matching: Requires match on **both text and entity category**.
- **Empirical Results (Unmanipulated):**
  - **Keywords:** Macro $P = 0.125$, Macro $R = 0.224$, Macro $F_1 = 0.160$.
  - **Entities:** Macro $P = 0.383$, Macro $R = 0.690$, Macro $F_1 = 0.489$.

---

### SLIDE 11: Top-K Ranking & Ablation Analysis
- **Top-K Retrieval Cutoffs (Keywords):**
  - **Top-5:** Precision = **0.217** (confirms high-confidence terms rank highest).
  - **Top-10:** Precision = 0.158, Recall = 0.140, $F_1 = 0.148$.
  - **Top-20:** Precision = 0.125, Recall = **0.224**, $F_1 = 0.160$.
- **Algorithm Ablation Study:**
  - **TF-IDF Alone:** $F_1 = 0.179$ (strong for single words; misses multi-word compounds).
  - **RAKE Alone:** $F_1 = 0.022$ (extracts broad phrases with high false positives).
  - **LexExtract Hybrid:** $F_1 = 0.163$ (balances phrase extraction with legal constraints).
- **Processing Performance:** Average processing latency of **824.0 ms per document**.

---

### SLIDE 12: Testing, Security & Quality Assurance
- **Automated Regression Suite:** **98 / 98 tests passing (100%)** in 27.34s.
  - Auth & JWT (14 tests), Authorization & RBAC (10 tests), Database (12 tests), Ingestion (13 tests), Keywords (12 tests), Entities (14 tests), Evaluation (13 tests), Health & Audit (10 tests).
- **Frontend Build:** 1,559 modules compiled cleanly with Vite (0 errors).
- **Security Verification:**
  - Cross-user document and analysis access blocked with HTTP 403 Forbidden.
  - Sensitive password hashes and secret keys excluded from all API responses.
  - Immutable audit ledger recording 170+ operational and security events.

---

### SLIDE 13: Academic Subject Mapping
- **ASTMA (Advanced Social, Text and Media Analytics):** Citation-aware preprocessing, n-gram extraction, RAKE co-occurrence graph scoring, TF-IDF, Named Entity Recognition, contingency tables ($TP, FP, FN$), Precision, Recall, $F_1$, Top-K cutoffs, ablation studies, and error analysis.
- **ES (Enterprise Systems):** Three-Tier architecture, asynchronous REST API, relational persistence, schema migrations, stateless JWT security, Argon2id hashing, and horizontal isolation.
- **ITPM (IT Project Management):** 9-phase Work Breakdown Structure, risk register, requirements traceability matrix, continuous regression testing, and non-repudiation audit logging.

---

### SLIDE 14: System Limitations & Future Scope
- **Current Limitations:**
  - Scanned PDF images require digital text streams (no OCR included).
  - Benchmark corpus consists of 12 curated documents (project-scale).
  - Evaluation uses exact normalized matching rather than semantic embeddings.
  - Academic analysis system; does not offer legal advice.
- **Future Scope:**
  - Integration of Tesseract OCR for scanned historical briefs.
  - Contextual transformer embeddings (e.g., Legal-BERT fine-tuning).
  - Interactive citation graphs visualizing cross-statutory dependencies.
  - Production deployment to managed cloud containers and PostgreSQL.

---

### SLIDE 15: Conclusion & Technical Sign-Off
- **Key Deliverables Achieved:**
  - Production-grade Three-Tier legal information extraction platform.
  - Domain-adapted keyword and entity extraction pipelines.
  - Interactive document viewer with token-span highlighting.
  - Verifiable ASTMA evaluation benchmark with unmanipulated metrics.
  - 98 automated backend tests passing with 100% success.
- **Project Status:** **Feature-Complete, Verified, and Submission-Ready.**
- **Thank you! We welcome questions from the evaluation committee.**
