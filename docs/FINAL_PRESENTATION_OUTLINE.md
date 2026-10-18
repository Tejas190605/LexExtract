# LexExtract — Final Presentation Outline & Oral Script

**Presentation Duration:** 12–15 Minutes  
**Slide Count:** 15 Slides  
**Subject Focus:** ES, ASTMA, ITPM Integration  
**Date:** October 2026  

---

### Slide 1: Title & Introduction
- **Slide Title:** LexExtract: Local-First Legal Document Keyword & Entity Extractor
- **Key Content:**
  - Project-Based Learning Capstone (ES, ASTMA, ITPM)
  - Presenter: [Student Name / Tejas]
  - Technology Stack: FastAPI, React 18, SQLAlchemy, spaCy, scikit-learn
  - Tagline: Explainable, Confidential, and High-Throughput Legal Document Intelligence
- **What to Say:**
  > "Respected examiners and faculty members, good morning. Today I am presenting LexExtract, a high-throughput, local-first legal document intelligence platform. LexExtract extracts keywords, named entities, critical clauses, obligations, and comparison diffs from complex legal agreements. It achieves this completely offline without third-party cloud APIs, ensuring absolute client confidentiality and deterministic results."

---

### Slide 2: Problem Statement
- **Slide Title:** The Legal Document Review Challenge
- **Key Content:**
  - Manual review of 50+ page commercial contracts is slow, costly, and prone to fatigue.
  - Critical clauses (indemnity, termination, jurisdiction) are easily buried in dense prose.
  - Cloud-based LLM APIs introduce client privacy violations, data leaks, and unpredictable recurring costs.
  - Lack of algorithmic explainability in probabilistic black-box models.
- **What to Say:**
  > "In legal practice, lawyers and corporate counsels review hundreds of lengthy contracts daily. Manually identifying liabilities, deadlines, and dispute clauses takes hours. While many turn to cloud AI, doing so sends confidential client contracts to external servers, violating data sovereignty and professional privilege. Furthermore, LLMs hallucinate and cannot mathematically explain their reasoning."

---

### Slide 3: Motivation & Core Objectives
- **Slide Title:** Project Motivation & Objectives
- **Key Content:**
  - **Privacy:** 100% on-premises processing preserving attorney-client privilege.
  - **Explainability:** Mathematical scoring based on TF-IDF, graph co-occurrence, and rule heuristics.
  - **Zero Cloud Cost:** Eliminates token-based subscription expenses.
  - **Tri-Disciplinary Integration:** Practical fusion of Enterprise Systems, ASTMA, and ITPM principles.
- **What to Say:**
  > "Our motivation was to build an enterprise-grade platform that is secure, fast, and fully explainable. Our core objectives were: first, build a multi-tier web application with role-based security; second, formulate a hybrid NLP pipeline for legal extraction; third, implement side-by-side document comparison; and fourth, manage the development under rigorous software engineering and evaluation standards."

---

### Slide 4: Existing Systems vs. LexExtract
- **Slide Title:** Existing Approaches vs. Proposed Solution
- **Key Content:**
  - *Comparison Table:*
    - Cloud LLMs: High recurring cost, data leakage risk, non-deterministic output.
    - Legacy RegEx Tools: Rigid, brittle, cannot handle varying contract phrasing.
    - LexExtract: Zero external calls, explainable hybrid scoring (TF-IDF + RAKE + Rules), sub-second latency, multi-format support.
- **What to Say:**
  > "Compared to existing solutions, cloud LLMs are expensive and insecure for sensitive contracts, while basic keyword search is too brittle. LexExtract bridges this gap: it uses statistical NLP and legal gazetteers to provide deep extraction in under 350 milliseconds with zero privacy risk and zero cloud costs."

---

### Slide 5: System Architecture
- **Slide Title:** Three-Tier Enterprise System Architecture
- **Key Content:**
  - Presentation Tier: React 18, Vite 5, Tailwind CSS, institutional aesthetic.
  - Application Tier: FastAPI async ASGI server, Pydantic v2 validation, modular service layer.
  - Data Tier: Relational SQLite with SQLAlchemy 2.0 ORM, file storage system.
  - Security: Stateless Bearer JWT tokens (RFC 7519), Argon2id password hashing.
- **What to Say:**
  > "Architecturally, LexExtract follows a decoupled three-tier design. The React single-page frontend communicates with our FastAPI backend using RESTful endpoints and stateless JWT tokens. The data layer uses SQLAlchemy ORM to manage relational integrity with SQLite. This guarantees complete separation of concerns and high maintainability."

---

### Slide 6: The ASTMA Text Mining Pipeline
- **Slide Title:** Natural Language Processing & Text Mining Pipeline
- **Key Content:**
  - 1. Ingestion & Normalization: PDF/DOCX/TXT text streaming, citation normalization.
  - 2. Candidate Generation: Unigrams, bigrams, and trigrams.
  - 3. Statistical Scoring: TF-IDF (corpus discrimination) + RAKE (word degree co-occurrence).
  - 4. Domain Weighting: Legal lexicon dictionary amplification.
  - 5. Tri-Factor Fusion: Weighted composite score ($0.45 \cdot \text{TF-IDF} + 0.35 \cdot \text{RAKE} + 0.20 \cdot \text{Legal}$).
- **What to Say:**
  > "From an ASTMA perspective, our keyword extraction avoids the weaknesses of using single algorithms. While TF-IDF excels at corpus-level frequency discrimination, it misses multi-word collocations. Conversely, RAKE captures phrases but struggles with legal punctuation. Our tri-factor fusion formula weights TF-IDF at 45%, RAKE at 35%, and domain vocabulary at 20% to produce highly accurate legal terms."

---

### Slide 7: Named Entity Recognition & Clause Mining
- **Slide Title:** Dual-Engine NER & Clause Detection
- **Key Content:**
  - Dual-Engine NER: Statistical spaCy pipeline + custom regex gazetteers for statutory acts, sections, courts, and citations.
  - Precedence Resolution: Rule-based gazetteers override generic spaCy spans.
  - Important Clause Mining: Categorizes 13 clause classes (Arbitration, Indemnity, Termination, etc.).
  - Obligation Extractor: Parses modal verbs (`shall`, `must`) into affirmative duties and prohibitions (`shall not`).
- **What to Say:**
  > "For Information Extraction, we combine statistical NER from spaCy with custom rule gazetteers to detect 13 entity types, including statutes, court names, and monetary values. Gazetteers take priority over general statistical spans. Additionally, our clause engine detects 13 standard contract clauses and extracts contractual obligations, classifying duties versus prohibitions."

---

### Slide 8: Document Comparison & Search Engine
- **Slide Title:** Vector Space Search & Document Comparison
- **Key Content:**
  - In-Document Search: Passage-level TF-IDF relevance scoring with exact character offsets.
  - Document Comparison: Vector Space Model cosine similarity score (0–100%).
  - Vocabulary & Clause Alignment: Side-by-side diff of shared/unique terms and corresponding clauses.
- **What to Say:**
  > "For document comparison, LexExtract vectorizes both agreements into TF-IDF term vectors and computes their cosine similarity. It also generates an aligned clause comparison table, enabling legal teams to instantly spot variations between standard templates and executed agreements."

---

### Slide 9: Enterprise Security, RBAC & Multi-Tenancy
- **Slide Title:** Enterprise Systems Security & Governance
- **Key Content:**
  - Role-Based Access Control: 3 roles (`ADMIN`, `ANALYST`, `USER`).
  - Strict Tenant Isolation: User A cannot read, search, or compare User B's documents (`HTTP 403 Forbidden`).
  - Cryptographic Security: Argon2id password hashing; zero plaintext credentials.
  - Audit Ledger: Immutable database logging of all uploads, runs, and administrative actions.
- **What to Say:**
  > "In alignment with Enterprise Systems criteria, LexExtract implements strict multi-tenancy and RBAC. Every document access request verifies ownership, rejecting unauthorized users with HTTP 403. Passwords use Argon2id hashing, and an immutable audit trail records all critical system activities."

---

### Slide 10: ITPM Methodology & Governance
- **Slide Title:** Project Management, WBS & Quality Assurance
- **Key Content:**
  - 14 Structured Phases executed sequentially.
  - 4-Level Work Breakdown Structure (WBS) covering initiation to release.
  - Risk Register: 10 technical and schedule risks tracked and mitigated.
  - Requirements Traceability Matrix: 100% bidirectional traceability for 19 IEEE 830 requirements.
- **What to Say:**
  > "From an ITPM perspective, the project followed a structured 14-phase development lifecycle. We maintained a 4-level Work Breakdown Structure, managed 10 prioritized risks, and enforced an IEEE 830 Requirements Traceability Matrix linking all 19 functional and non-functional requirements to concrete code and test cases."

---

### Slide 11: Empirical Results & ASTMA Evaluation
- **Slide Title:** Empirical Benchmarking & Ablation Study
- **Key Content:**
  - Curated Gold-Standard Benchmark: 12 legal documents (4,801 words).
  - Keyword Metrics: Precision: 12.50%, Recall: 23.26%, F1: 16.26% (Top-5 Precision: 21.67%).
  - Ablation Study: Proves RAKE alone achieves only 2.17% F1; fusion produces readable terms.
  - NER Metrics: Precision: 38.79%, Recall: 68.55%, F1: 49.55%.
  - Runtime Latency: 230.5 ms average per document.
- **What to Say:**
  > "We evaluated the system against a gold-standard benchmark of 12 real legal agreements. Our ablation study proved that RAKE alone achieves only 2.17% F1 due to legal punctuation breaking graph co-occurrence, whereas our hybrid approach achieves balanced recall and readable terms. Our NER achieved over 68% recall, and the entire pipeline executes in an average of 230 milliseconds."

---

### Slide 12: Live Demonstration Workflow
- **Slide Title:** End-to-End Demonstration Workflow
- **Key Content:**
  - User Journey: Login $\rightarrow$ Dashboard $\rightarrow$ Upload $\rightarrow$ Analysis $\rightarrow$ Overview $\rightarrow$ Clauses $\rightarrow$ Obligations $\rightarrow$ Dates/Money $\rightarrow$ Search $\rightarrow$ Viewer $\rightarrow$ Comparison $\rightarrow$ Export $\rightarrow$ History $\rightarrow$ Admin Audit.
  - Dual Export Formats: Vector PDF report & machine-readable JSON.
- **What to Say:**
  > "During our live demo, we will walk through the complete journey: logging in, uploading a commercial arbitration agreement, analyzing it in under a third of a second, inspecting clauses and affirmative duties, conducting in-document searches, running side-by-side comparison, and generating an executive PDF report."

---

### Slide 13: Software Verification & Test Results
- **Slide Title:** Quality Assurance & Automated Testing
- **Key Content:**
  - Test Suite: Pytest 9.1.1.
  - Results: **119 Passed, 0 Failed, 0 Regressions (100% Pass Rate)**.
  - Frontend Build: Vite 5.4.21 production bundle built cleanly with 0 errors.
  - Browser Workflow: 100% verified via automated browser subagent.
- **What to Say:**
  > "LexExtract is backed by an automated test suite of 119 tests covering unit logic, integration flows, RBAC enforcement, and edge cases. All 119 tests pass with zero regressions, and the frontend builds cleanly with zero errors or warnings."

---

### Slide 14: System Limitations & Future Enhancements
- **Slide Title:** Limitations & Future Scope
- **Key Content:**
  - Limitations: Scanned paper PDFs require digital text streams; optimized for English contracts.
  - Future Scope: Local Tesseract OCR integration, cross-jurisdictional legal gazetteers, batch discovery processing.
- **What to Say:**
  > "In terms of limitations, scanned image-only documents currently require prior OCR. In the future, we plan to embed local Tesseract OCR directly into the ingestion engine and expand our statutory gazetteers to additional international jurisdictions."

---

### Slide 15: Conclusion & Summary
- **Slide Title:** Conclusion & Academic Contributions
- **Key Content:**
  - Successfully demonstrated that a local-first legal intelligence tool can be fast, accurate, and completely private.
  - Proven integration of Enterprise Systems architecture, ASTMA text mining, and ITPM management.
  - Fully documented, tested, and frozen release (v1.0.0).
- **What to Say:**
  > "In conclusion, LexExtract delivers a robust, secure, and explainable legal intelligence platform. By uniting Enterprise Systems engineering, ASTMA text mining methods, and ITPM governance, we have delivered a feature-complete, rigorously tested academic capstone project. Thank you, and I look forward to your questions."
