# LexExtract — Individual Engineering Contribution Matrix

This document details the software components, algorithms, and documentation developed across the nine implementation phases of the LexExtract project.

---

## 1. Summary of Contributions

| Engineering Subsystem | Description of Work | Key Deliverables / Artifacts |
| :--- | :--- | :--- |
| **Three-Tier Architecture & APIs** | Designed and developed the decoupled architecture and RESTful service layer. | FastAPI backend, Pydantic schemas, central API v1 router, CORS middleware. |
| **Document Ingestion & Parsing** | Engineered multi-format parsers with citation-preserving preprocessing. | Integration of PyMuPDF and `python-docx`; regex normalizer preserving statutory parentheses. |
| **Tri-Model Keyword Extraction** | Implemented weighted fusion combining statistical, graph, and lexicon techniques. | In-house RAKE algorithm, TF-IDF vectorizer, 1,200-word domain lexicon, min-max score normalizer. |
| **Hybrid Legal NER Pipeline** | Built combined statistical and symbolic named entity recognition. | spaCy pipeline integration, 13 legal gazetteers/regex patterns, span deduplication. |
| **Interactive Presentation Tier** | Developed single-page application and token-offset highlighting. | React 18 SPA, Tailwind CSS legal design system, Document Viewer highlighting engine. |
| **Security & Access Control** | Implemented cryptographic authentication, RBAC, and data isolation. | Argon2id password hashing, JWT session manager, RBAC route dependencies, cross-user 403 isolation. |
| **Governance Audit Ledger** | Built immutable non-repudiation security logging. | SQLAlchemy `AuditLog` model, audit recording service, admin audit page. |
| **ASTMA IR Evaluation Engine** | Developed empirical benchmarking suite and metrics calculator. | Curated 12-document benchmark corpus, contingency matrix calculator ($P, R, F_1$), Top-K and ablation analysis. |
| **Automated Testing Suite** | Authored and maintained comprehensive regression test coverage. | 98 passing Pytest tests across 8 test suites; E2E browser automation scripts. |
| **Project Management & Documentation** | Produced full project documentation, risk registers, and guides. | WBS, RTM, Risk Register, Deployment Guide, Final Report, and Viva preparation. |

---

## 2. Detailed Technical Breakdown

### 2.1 Backend Engineering & API Services
- Authored the asynchronous FastAPI application in `backend/main.py`.
- Implemented modular API routers for `/auth`, `/documents`, `/analyses`, `/evaluation`, and `/admin`.
- Engineered database initialization routines with self-healing column migrations for SQLite.
- Configured connection pooling and concurrency flags (`check_same_thread=False`).

### 2.2 NLP & Text Mining Pipelines
- Built custom preprocessors that collapse whitespace while preserving citations like `Section 11(6)` and `Article 226(1)`.
- Implemented the RAKE graph co-occurrence scoring algorithm from mathematical principles without heavy external dependencies.
- Integrated scikit-learn's `TfidfVectorizer` with a reference legal corpus.
- Curated a dictionary of 1,200+ Indian and Commonwealth legal terms across 7 legal domains.
- Engineered hybrid NER combining spaCy's statistical model with custom regular expressions for 13 legal entity classes.

### 2.3 Presentation Tier & Interactive Viewer
- Built a modular React 18 SPA using functional components and hooks (`useState`, `useEffect`, `useMemo`, `useCallback`).
- Configured a professional legal-tech color palette (Navy Blue `#1E3A8A`, Slate `#334155`, Warm Parchment `#F8FAFC`, Burgundy `#881337`, Muted Gold `#D97706`).
- Developed the Document Viewer with multi-layer highlighting toggles (All Overlays, Keywords, Entities, Plain Text).
- Built real-time filterable explorers for extracted keywords and entities.

### 2.4 Empirical Evaluation & Benchmarking
- Created a 12-document curated legal benchmark corpus (3,875 words) with paired human-readable JSON annotations containing 129 gold keywords and 157 gold entities.
- Implemented contingency matrix calculation ($TP, FP, FN$) with zero-division safeguards.
- Implemented Top-K cutoff evaluation ($K \in \{5, 10, 20\}$) and algorithm ablation studies.
- Engineered error analysis categorization separating False Positives, False Negatives, and Entity Category Mismatches.

### 2.5 Security, Testing & Governance
- Implemented Argon2id password hashing and stateless RFC 7519 JWT sessions.
- Built horizontal document isolation guards returning HTTP 403 Forbidden on foreign access attempts.
- Authored 98 automated backend tests covering unit, integration, and API scenarios.
- Executed full browser automation testing covering the 15-step practitioner and admin user journeys.
