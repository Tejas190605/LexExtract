# LexExtract — Feature-to-Subject Cross-Disciplinary Matrix

**Project Title:** LexExtract — Legal Document Keyword & Entity Extractor  
**Subject Mapping:** Enterprise Systems (ES) • Advanced Statistical & Text Mining Analysis (ASTMA) • IT Project Management (ITPM)  
**Standard:** Comprehensive academic cross-mapping verifying genuine implementation of core curriculum principles  

---

## 1. Feature-to-Subject Matrix

| System Feature / Capability | Enterprise Systems (ES) | ASTMA (NLP / Text Mining) | IT Project Management (ITPM) | Implementation Details & Artifact References |
| :--- | :---: | :---: | :---: | :--- |
| **User Registration & Login** | **✓** | | | Stateless RFC 7519 JWT (HS256) auth + Argon2id password hashing (`app/core/security.py`, `LoginPage.jsx`). |
| **Multi-Role RBAC** | **✓** | | | USER, ANALYST, and ADMIN role permissions enforced via FastAPI dependencies (`app/core/deps.py`). |
| **Tenant Document Isolation** | **✓** | | | Cross-user horizontal access blocks returning HTTP 403 Forbidden (`test_authorization.py`). |
| **Governance Audit Ledger** | **✓** | | | Non-repudiation tracking of logins, uploads, deletions, and exports in `audit_logs` table (`AdminAuditPage.jsx`). |
| **Three-Tier Architecture** | **✓** | | | Decoupled React 18 presentation tier, FastAPI business logic tier, and SQLAlchemy ORM data tier. |
| **Document Ingestion (PDF/DOCX/TXT)** | **✓** | **✓** | | PyMuPDF text coordinate layout extraction + python-docx XML traversal with MIME-type validation. |
| **Citation-Preserving Preprocessor** | | **✓** | | Normalizes whitespace, reconnects hyphenated line-breaks, and preserves section citations like `Section 11(6)`. |
| **Tri-Model Keyword Extraction** | | **✓** | | Hybrid fusion combining TF-IDF (35%), RAKE graph co-occurrence (35%), and domain lexicon heuristics (30%). |
| **Hybrid Legal NER** | | **✓** | | 13 legal entity classes extracted via statistical spaCy NER combined with deterministic statutory gazetteers. |
| **Important Clause Detection** | | **✓** | | Classifies clauses across 13 controlled contractual categories with confidence ratings and source passages. |
| **Obligations & Duties Extraction** | | **✓** | | Analyzes modal auxiliary verbs (`shall`, `must`) to extract affirmative duties, prohibitions, and deadlines. |
| **Structured Facts Extraction** | | **✓** | | Identifies multi-currency amounts (INR, USD, EUR, GBP), execution dates, and notice timeline durations. |
| **In-Document Information Retrieval Search**| **✓** | **✓** | | Passage-level text indexing and relevance ranking using ASTMA TF-IDF with direct Document Viewer jump. |
| **Interactive Document Viewer** | **✓** | **✓** | | Multi-layer visual text stream with color-coded highlighting badges for legal terms and typed entities. |
| **Two-Document Comparison (Diff Engine)** | **✓** | **✓** | | High-dimensional TF-IDF vector cosine similarity + side-by-side clause alignment (`UNCHANGED`, `MODIFIED`). |
| **Executive Report Export (PDF & JSON)** | **✓** | | | Multi-page vector PDF generated via PyMuPDF vector engine + raw structured JSON with legal disclaimer. |
| **ASTMA Empirical Evaluation Runner** | | **✓** | | Real-time benchmarking against 12-doc gold-standard corpus calculating Micro/Macro $P, R, F_1$ and ablation. |
| **Work Breakdown Structure (WBS)** | | | **✓** | 100% rule hierarchical decomposition covering all 12 project phases (`docs/WBS.md`). |
| **Milestone Timeline & Critical Path** | | | **✓** | Phased milestone schedule tracking critical path engineering deliverables (`docs/PROJECT_TIMELINE.md`). |
| **PMBOK Risk Register (R-01 to R-10)** | | | **✓** | Formal 10-point Risk Register with probability, impact, mitigations, and contingencies (`docs/RISK_REGISTER.md`). |
| **Requirements Traceability Matrix (RTM)** | | | **✓** | Bidirectional mapping from 19 requirements to active code modules and automated test IDs (`docs/REQUIREMENTS_TRACEABILITY_MATRIX.md`). |
| **Software Test Plan & Test Cases** | **✓** | **✓** | **✓** | IEEE 829 Software Test Plan (`docs/TEST_PLAN.md`) and Test Cases `TC-001` through `TC-025` (`docs/TEST_CASES.md`). |
| **Automated Testing Suite (119 Tests)** | **✓** | **✓** | **✓** | 119 passing automated Pytest cases with 0 failures covering unit, integration, security, and edge cases. |
| **Quality Assurance (QA) Checklist** | **✓** | **✓** | **✓** | 6-tier verification covering Functional, UI/UX, Security, Performance, Data Tier, and NLP Quality (`docs/QA_CHECKLIST.md`). |
| **Requirement Coverage Reporting** | | | **✓** | Exact empirical coverage computation showing 100% requirement coverage and 100% test pass rate (`docs/REQUIREMENT_COVERAGE_REPORT.md`). |

---

## 2. Subject Contribution Summary

- **Enterprise Systems (ES) Contribution:** Provides the industrial-strength foundation: scalable client-server microservices, secure authentication, multi-tenant isolation, role governance, database relationship management, and regulatory compliance audit logging.
- **ASTMA Contribution:** Powers the analytical intelligence: domain-specific text preprocessing, graph and statistical keyword scoring, linguistic and rule-based entity recognition, contractual clause classification, and rigorous empirical evaluation.
- **IT Project Management (ITPM) Contribution:** Ensures engineering rigor, predictability, and academic accountability: structured scope planning, active risk mitigation, bidirectional requirements traceability, IEEE 829 testing standards, and quantitative verification.
