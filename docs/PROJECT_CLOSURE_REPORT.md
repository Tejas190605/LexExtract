# LexExtract — Final Project Closure & Milestone Sign-Off Report

**Project Title:** LexExtract: Intelligent Legal Document Keyword & Entity Extractor  
**Academic Year:** 2025–2026  
**Milestone:** Phase 10 — Final PBL Submission Package, Report, PPT & Viva Preparation  
**Final Status:** **COMPLETE & VERIFIED (FEATURE-COMPLETE)**

---

## 1. Project Summary

### 1.1 Problem & Motivation
Legal practitioners and compliance analysts spend substantial manual effort reading dense commercial agreements, court judgments, and statutory notices to extract key legal obligations, statutory sections, participating parties, and financial sums. Generic natural language processing tools fail on legal texts because standard normalizers strip essential citation parentheses (e.g. `Section 11(6)`), general-purpose NER models misclassify high courts as generic commercial corporations, and commercial legal-tech systems are closed-source and unexplainable.

### 1.2 Proposed Solution & Architecture
LexExtract is an intelligent legal document processing and information retrieval system built on a decoupled **Three-Tier Enterprise Architecture**:
- **Presentation Tier:** A responsive Single-Page Application (SPA) built with React 18, Vite, and Tailwind CSS.
- **Application Tier:** An asynchronous RESTful API service built with FastAPI, Python 3.12+, and Pydantic validation schemas.
- **Data Tier:** Relational persistence using SQLite via SQLAlchemy 2.0 ORM (migration-ready for PostgreSQL) and local structured file storage with SHA-256 integrity validation.

---

## 2. Implemented Subsystems & Methods

### 2.1 Multi-Format Document Ingestion
- Ingestion of PDF and DOCX documents up to 25 MB with MIME-type validation and SHA-256 integrity hashing.
- Text extraction via PyMuPDF (PDF layout coordinates) and `python-docx` (XML paragraphs and tables).
- Citation-preserving normalization that cleans non-standard whitespace while explicitly maintaining statutory subsection parentheses.

### 2.2 Tri-Model Keyword Extraction Pipeline
- N-gram candidate generation ($1 \le n \le 3$) with boundary-aware sliding windows.
- Stopword filtering with explicit retention of legal connective particles.
- Tri-model scoring combining:
  - **TF-IDF (35%):** Vector space relevance against a legal reference corpus.
  - **RAKE Graph Scoring (35%):** Word co-occurrence graph degree-to-frequency ratios.
  - **Domain Legal Lexicon (30%):** Matches against 1,200+ Indian and Commonwealth legal terms across 7 categories.
- Weighted score fusion and top-20 candidate ranking.

### 2.3 Hybrid Named Entity Recognition (NER)
- Statistical sequence parsing using `spaCy` (`en_core_web_sm`) for general entities (`PERSON`, `ORG`, `DATE`, `MONEY`, `LOCATION`).
- Custom regular expressions and legal gazetteers for 13 specialized legal classes:
  - `COURT`, `STATUTE`, `SECTION`, `ARTICLE`, `CASE_NUMBER`, `LEGAL_ROLE`, `JURISDICTION`, `MONETARY_VALUE`, `DATE`, `ORGANIZATION`, `PERSON`, `CONTRACT_TYPE`, `LOCATION`.
- Longest-match span arbitration giving domain rules precedence over generic statistical tags.

### 2.4 Interactive Document Viewer
- Text canvas mapping character offsets to color-coded span badges.
- Multi-layer visual toggles: All Overlays, Keywords Only (amber), Entities Only (purple/blue/green badges), and Clean Plain Text.

### 2.5 Security, RBAC & Governance
- Stateless RFC 7519 JSON Web Token (JWT) authentication signed with HMAC-SHA256 (`HS256`).
- Argon2id memory-hard password hashing.
- Role-Based Access Control (`USER`, `ANALYST`, `ADMIN`).
- Horizontal document ownership isolation blocking cross-user access with HTTP 403 Forbidden.
- Non-repudiation Governance Audit Ledger recording system actions with client IP and timestamps.

### 2.6 ASTMA Empirical IR Evaluation Engine
- Curated legal benchmark corpus of 12 documents (3,875 words, 129 gold keywords, 157 gold entities).
- Dynamic calculation of Precision, Recall, and F1-score with zero-division boundary safeguards.
- Top-K retrieval cutoff evaluation ($K \in \{5, 10, 20\}$).
- Algorithm ablation studies (TF-IDF vs. RAKE vs. LexExtract Hybrid).
- Taxonomic error analysis separating False Positives, False Negatives, and Entity Category Mismatches.

---

## 3. Verification & Validation Metrics

| Quality Dimension | Target Baseline | Measured Result | Status |
| :--- | :--- | :--- | :---: |
| **Backend Test Suite** | 100% of automated tests passing | 98 passed, 0 failed in 27.34s | **PASS** |
| **Frontend Production Build** | Zero compilation or bundling errors | 1,559 modules built in 32.23s | **PASS** |
| **Document Ownership Isolation** | Cross-user access blocked | Confirmed HTTP 403 Forbidden | **PASS** |
| **Keyword Evaluation ($F_1$)** | Empirical benchmark measurement | Macro $F_1 = 0.160$, Micro $F_1 = 0.163$ | **VERIFIED** |
| **Entity Evaluation ($F_1$)** | Empirical benchmark measurement | Macro $F_1 = 0.489$, Micro $F_1 = 0.495$ | **VERIFIED** |
| **Top-5 Keyword Precision** | Validate ranked candidate ordering | Precision@5 = **0.217** | **VERIFIED** |
| **Average Processing Latency** | Sub-2.0 second per-document processing | **824.0 ms per document** | **PASS** |
| **Browser E2E Automation** | 15-step user journey verification | 100% verified with recorded session | **PASS** |

---

## 4. Academic Subject Integration

- **ASTMA (Advanced Social, Text and Media Analytics):** Citation-preserving normalization, n-gram extraction, TF-IDF statistical scoring, RAKE graph co-occurrence, Named Entity Recognition, contingency tables ($TP, FP, FN$), Precision, Recall, $F_1$, Top-K cutoffs, ablation studies, and error analysis.
- **ES (Enterprise Systems):** Three-Tier architecture, asynchronous RESTful APIs, relational persistence via SQLAlchemy ORM, schema migrations, stateless JWT security, Argon2id hashing, and horizontal isolation.
- **ITPM (IT Project Management):** 9-phase Work Breakdown Structure, risk register, requirements traceability matrix, continuous regression testing, and non-repudiation audit logging.

---

## 5. System Limitations & Future Work

### Limitations
1. **No OCR Engine:** Scanned image-only PDFs require digital text streams.
2. **Benchmark Scope:** 12-document curated benchmark represents a project-scale dataset.
3. **Exact Normalized Matching:** Evaluation uses exact normalized matching; near-synonyms count as False Negatives.
4. **Academic Demonstration Scope:** Designed for academic evaluation; does not offer legal advice.

### Future Work
1. Integrate Tesseract OCR for scanned physical briefs.
2. Fine-tune contextual legal language models (e.g., Legal-BERT).
3. Implement embedding-based semantic similarity scoring to complement exact-match evaluation.
4. Build interactive dependency graphs mapping cross-statutory citations.

---

## 6. Final Project Closure Sign-Off

```
========================================================================================
                      LEXEXTRACT PROJECT CLOSURE SIGN-OFF (PHASE 10)
========================================================================================

  Phase 1: Architecture, Core Blueprint & Repository Scaffolding           [COMPLETE]
  Phase 2: Database Schema, Models & Data Repositories                    [COMPLETE]
  Phase 3: Document Ingestion, PDF/DOCX Parsing & Text Preprocessing      [COMPLETE]
  Phase 4: Tri-Model Keyword Extraction Pipeline (TF-IDF + RAKE + Lexicon)[COMPLETE]
  Phase 5: Legal Named Entity Recognition (spaCy + Legal Gazetteers)      [COMPLETE]
  Phase 6: Authentication, RBAC, Document Isolation & Audit Ledger        [COMPLETE]
  Phase 7: Professional Legal UI, Document Viewer & Results Explorer      [COMPLETE]
  Phase 8: ASTMA IR Evaluation Engine, Benchmark Dataset & Ablation       [COMPLETE]
  Phase 9: Final Integration, Deployment Preparation & Full QA            [COMPLETE]
  Phase 10: Final PBL Submission Package, Report, PPT & Viva Preparation  [COMPLETE]

  TOTAL AUTOMATED BACKEND TESTS PASSING : 98 / 98 (100%)
  FRONTEND PRODUCTION COMPILATION STATUS: 1,559 MODULES COMPILED (0 ERRORS)
  CROSS-USER DATA ISOLATION STATUS      : HTTP 403 FORBIDDEN ENFORCED
  ASTMA EVALUATION BENCHMARK STATUS     : EMPIRICAL & FULLY REPRODUCIBLE
  FINAL SUBMISSION PACKAGE STATUS       : 20 ACADEMIC DELIVERABLES PRODUCED
========================================================================================
```

**PHASE 10 COMPLETE**  
**THERE IS NO PHASE 11**
