# Work Breakdown Structure (WBS)

**Project Title:** LexExtract — Legal Document Keyword & Entity Extractor  
**Subject:** Information Technology Project Management (ITPM)  
**Methodology:** PMBOK 100% Rule Hierarchical Work Breakdown Structure  

---

```
1.0 LEXEXTRACT LEGAL ANALYTICS PLATFORM
│
├── 1.1 Project Initiation & Requirements Engineering (Phase 1)
│   ├── 1.1.1 Problem Statement & Academic Scope Definition (ES, ASTMA, ITPM)
│   ├── 1.1.2 Functional & Non-Functional Requirements Specification
│   ├── 1.1.3 Requirements Traceability Matrix Formulation
│   └── 1.1.4 Initial Risk Register & Mitigation Strategy
│
├── 1.2 Enterprise Architecture & Backend Foundation (Phase 2 & 3)
│   ├── 1.2.1 Three-Tier Architecture Design (Presentation, Application, Data)
│   ├── 1.2.2 Database Schema Modeling (Users, Documents, Analyses, Keywords, Entities, Audit)
│   ├── 1.2.3 SQLAlchemy ORM Implementation & Relationship Constraints
│   ├── 1.2.4 Multi-Format Document Ingestion Engine (PDF, DOCX, TXT)
│   ├── 1.2.5 File Validation Pipeline (MIME check, size ceiling, header inspection)
│   └── 1.2.6 RESTful API Router Configuration (FastAPI)
│
├── 1.3 NLP & Text Mining Engine (ASTMA) (Phase 4 & 5)
│   ├── 1.3.1 Legal Text Preprocessing & Cleaning (Unicode normalization, line reconnection)
│   ├── 1.3.2 Candidate n-gram Generation & Statutory Citation Retention
│   ├── 1.3.3 TF-IDF Statistical Scorer Implementation
│   ├── 1.3.4 RAKE Graph Co-Occurrence Scorer Implementation
│   ├── 1.3.5 Domain Lexicon Matcher & Legal Weighting
│   ├── 1.3.6 Composite Hybrid Ranking & Score Normalization
│   ├── 1.3.7 Named Entity Recognition (spaCy en_core_web_sm pipeline)
│   ├── 1.3.8 Legal Gazetteer Rules Engine (Courts, Statutes, Corporate Forms)
│   └── 1.3.9 Entity Deduplication & Normalization
│
├── 1.4 Security, RBAC & Governance Tier (Phase 6)
│   ├── 1.4.1 RFC 7519 Stateless JWT Authentication (HS256)
│   ├── 1.4.2 Argon2id Cryptographic Password Hashing
│   ├── 1.4.3 Multi-Role Authorization Middleware (USER, ANALYST, ADMIN)
│   ├── 1.4.4 Tenant Document Isolation Dependency (`check_document_access`)
│   └── 1.4.5 Governance Audit Trail Service & Immutable Event Ledger
│
├── 1.5 Presentation Tier & UI Development (Phase 7)
│   ├── 1.5.1 React 18 + Vite Project Scaffold with Vanilla CSS Design System
│   ├── 1.5.2 Legal-Tech Dark Slate Theme & Typography
│   ├── 1.5.3 Authentication Context & Protected Route Wrappers
│   ├── 1.5.4 Executive Analytics Dashboard
│   ├── 1.5.5 Interactive Document Viewer with In-Text Keyword & Entity Highlighting
│   ├── 1.5.6 Entity & Keyword Explorers with Multi-Metric Sorting
│   └── 1.5.7 Admin Audit Log Viewer Interface
│
├── 1.6 Empirical ASTMA Evaluation & Benchmarking (Phase 8)
│   ├── 1.6.1 Curated 12-Document Legal Benchmark Corpus Preparation
│   ├── 1.6.2 Dual-Annotator Gold Standard Formulation
│   ├── 1.6.3 Quantitative Metric Computation (Micro/Macro Precision, Recall, F1)
│   ├── 1.6.4 Top-K Cutoff Evaluation ($K=5, 10, 20$)
│   ├── 1.6.5 Ablation Engine (TF-IDF vs RAKE vs Hybrid)
│   ├── 1.6.6 Execution Latency Profiling
│   └── 1.6.7 Interactive ASTMA Benchmark Frontend Page
│
├── 1.7 Integration, Deployment & QA (Phase 9 & 10)
│   ├── 1.7.1 Automated Pytest Test Suite Development
│   ├── 1.7.2 Negative & Edge-Case Test Suite
│   ├── 1.7.3 Production Build Packaging (`npm run build`)
│   ├── 1.7.4 Comprehensive Academic Submission Documentation
│   └── 1.7.5 Viva Voce Preparation Package & Slides
│
├── 1.8 Advanced User-Value Legal Intelligence (Phase 11)
│   ├── 1.8.1 Document At-a-Glance Synthesis & Attention Areas
│   ├── 1.8.2 Important Clause Finder (13 Standard Contractual Categories)
│   ├── 1.8.3 Contractual Obligations & Prohibition Extractor
│   ├── 1.8.4 Structured Facts Engine (Dates, Monetary Amounts, Deadlines)
│   ├── 1.8.5 In-Document Semantic Text Search
│   ├── 1.8.6 Two-Document Comparison (Cosine Similarity & Clause Diffing)
│   ├── 1.8.7 Multi-Page Executive Legal Report Generator (JSON & PyMuPDF PDF)
│   └── 1.8.8 Mandatory Legal Advice Disclaimer Integration
│
└── 1.9 Final Quality, Testing, Traceability & ITPM Integration (Phase 12)
    ├── 1.9.1 Requirements Traceability Matrix Verification
    ├── 1.9.2 Comprehensive Test Plan & IEEE 829 Test Cases
    ├── 1.9.3 Negative & Edge-Case Automated Suite (13 new edge tests)
    ├── 1.9.4 Formalized ITPM Risk Register (R-01 to R-10)
    ├── 1.9.5 Quality Assurance (QA) Checklist
    ├── 1.9.6 Requirement Coverage Report (100% Coverage, 119/119 Tests)
    ├── 1.9.7 ASTMA Evaluation Report & Deep Error Analysis
    └── 1.9.8 Final System Verification & Readiness Sign-off
```

---

## 2. WBS Dictionary (Key Work Packages)

- **WP-1.2.4 (Document Ingestion Engine):** Extracts raw text, retains page counts, and builds line offsets from uploaded PDF, DOCX, or TXT documents.
- **WP-1.3.6 (Hybrid Scoring Engine):** Normalizes TF-IDF and RAKE scores to $[0, 1]$, combines them with legal lexicon boosts, and computes composite keyword rank.
- **WP-1.4.3 (RBAC Middleware):** Evaluates user roles stored in signed JWT payloads and guards sensitive administrative and analytical API endpoints.
- **WP-1.8.6 (Document Comparison Engine):** Implements ASTMA TF-IDF vector cosine similarity and compares clauses across two documents with status classifications (`UNCHANGED`, `MODIFIED`, `ADDED`, `REMOVED`).
- **WP-1.9.3 (Edge-Case Test Suite):** Rigorously validates system behavior on empty inputs, unusual punctuation, massive synthetic documents, and unauthorized requests.
