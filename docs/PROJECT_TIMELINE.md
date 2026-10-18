# Project Timeline & Milestone Schedule

**Project Title:** LexExtract — Legal Document Keyword & Entity Extractor  
**Subject:** Information Technology Project Management (ITPM)  
**Methodology:** Phased Iterative Waterfall with Continuous Integration  
**Total Development Lifecycle:** 12 Development Phases  

---

## 1. Project Phase Breakdown & Milestone Schedule

| Phase | Milestone Description | Target Focus | Key Deliverables | Status |
| :---: | :--- | :--- | :--- | :---: |
| **Phase 1** | Project Initiation & Requirements | Academic Scope & Setup | Blueprint, Requirements Traceability Matrix, Architecture Design | **Completed** |
| **Phase 2** | Enterprise Architecture & Database | Three-Tier Data Foundation | SQLAlchemy Models, SQLite DB, CRUD routes, Health endpoints | **Completed** |
| **Phase 3** | Document Ingestion Pipeline | Multi-format File Engine | PDF/DOCX/TXT parsers, validation middleware, secure storage | **Completed** |
| **Phase 4** | Keyword Extraction Engine (ASTMA) | Statistical Text Mining | Preprocessor, TF-IDF, RAKE, domain lexicon, composite ranker | **Completed** |
| **Phase 5** | Named Entity Recognition (NER) | Hybrid Entity Tagging | spaCy NER, legal gazetteers, deduplicator, normalizer | **Completed** |
| **Phase 6** | Security, RBAC & Governance | Enterprise Access Control | Argon2id hashing, JWT auth, USER/ADMIN RBAC, audit ledger | **Completed** |
| **Phase 7** | Professional Legal UI & Viewer | Presentation Tier | React 18 frontend, document viewer, keyword/entity highlighter | **Completed** |
| **Phase 8** | ASTMA Benchmarking & Evaluation | Empirical Performance | 12-doc gold standard benchmark, Micro/Macro P/R/F1, ablation | **Completed** |
| **Phase 9** | Final Integration, QA & Deployment | System Hardening | Regression testing, automated test suite (85 tests), live demo | **Completed** |
| **Phase 10**| Submission Package & Viva Prep | Academic Formalization | Comprehensive report, synopsis, PPT outline, viva Q&A | **Completed** |
| **Phase 11**| User-Value Legal Intelligence | Feature Enhancements | Clauses, obligations, facts, in-doc search, compare, PDF/JSON export | **Completed** |
| **Phase 12**| Quality, Testing & Final ITPM Integration | Academic Completeness | 119 automated tests, edge testing, Risk Register, QA Checklist, Final Sign-off | **Completed** |

---

## 2. Milestone Deliverable Dates & Verification Sign-Off

```mermaid
gantt
    title LexExtract PBL Development Timeline
    dateFormat  YYYY-MM-DD
    section Initiation & Architecture
    Phase 1: Project Initiation & Setup           :done, p1, 2026-08-01, 2026-08-07
    Phase 2: Database & Data Tier Foundation      :done, p2, 2026-08-08, 2026-08-14
    Phase 3: Multi-Format Document Ingestion     :done, p3, 2026-08-15, 2026-08-21
    section ASTMA NLP Engine
    Phase 4: Statistical Keyword Extraction       :done, p4, 2026-08-22, 2026-08-29
    Phase 5: Hybrid Named Entity Recognition     :done, p5, 2026-08-30, 2026-09-06
    section Security & Presentation
    Phase 6: Security, RBAC & Audit Ledger       :done, p6, 2026-09-07, 2026-09-13
    Phase 7: React Frontend & Document Viewer    :done, p7, 2026-09-14, 2026-09-21
    section Benchmarking & Value Addition
    Phase 8: ASTMA Benchmark & Empirical Eval    :done, p8, 2026-09-22, 2026-09-27
    Phase 9: System Integration & QA             :done, p9, 2026-09-28, 2026-09-30
    Phase 10: Academic Reports & Viva Prep       :done, p10, 2026-10-01, 2026-10-02
    Phase 11: User-Value Legal Intelligence      :done, p11, 2026-10-03, 2026-10-04
    Phase 12: Quality, Edge Testing & Sign-off   :done, p12, 2026-10-05, 2026-10-05
```

---

## 3. Critical Path Analysis

The project's critical path consisted of sequentially dependent core engineering tasks:

1. **Document Ingestion Engine (WP-1.2.4)** $\rightarrow$ Required for raw text generation.
2. **Legal Text Preprocessing & Cleaning (WP-1.3.1)** $\rightarrow$ Required for accurate tokenization.
3. **ASTMA Hybrid Extraction (WP-1.3.6 & WP-1.3.9)** $\rightarrow$ Required for entity and keyword persistence.
4. **Tenant Access Control & RBAC (WP-1.4.3 & WP-1.4.4)** $\rightarrow$ Required for secure multi-user data isolation.
5. **Interactive Document Viewer & Highlighting (WP-1.5.5)** $\rightarrow$ Required for end-user visual interaction.
6. **Clause & Obligation Extraction (WP-1.8.2 & WP-1.8.3)** $\rightarrow$ Required for legal domain value addition.
7. **Comprehensive Regression & Edge Testing (WP-1.9.3)** $\rightarrow$ Required for quality assurance and 100% pass verification.

---

## 4. Schedule Variance & Control Summary

- **Planned vs. Actual Timeline:** The project executed within its allocated academic schedule, maintaining a steady progression across all 12 planned phases.
- **Resource Allocation:** Zero external cloud billing or GPU infrastructure required; entire system functions deterministically on standard local computing resources.
- **Final Milestone Status:** All 12 project phases successfully closed and verified with active automated test suites.
