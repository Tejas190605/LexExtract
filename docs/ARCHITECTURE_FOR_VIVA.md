# LexExtract — Architecture Explanation for Viva Voce

**Project Title:** LexExtract — Legal Document Keyword & Entity Extractor  
**Audience:** Academic Examiners, Project Evaluators & Viva Voce Panel  
**Purpose:** Clear, simple, end-to-end explanation of system architecture and subject mappings  

---

## 1. High-Level Architectural Flowchart

```
┌────────────────────────────────────────────────────────┐
│                         USER                           │
│     (Legal Practitioner / Data Analyst / Administrator)│
└───────────────────────────┬────────────────────────────┘
                            │ Interacts via Browser
                            ▼
┌────────────────────────────────────────────────────────┐
│                    REACT FRONTEND                      │
│   • React 18 Single-Page Application (SPA)             │
│   • Built with Vite for rapid bundling (105 kB gzip)   │
│   • Vanilla CSS Legal-Tech Dark Slate Design System    │
│   • Interactive Document Viewer with Token Highlighting│
└───────────────────────────┬────────────────────────────┘
                            │ HTTPS / REST API / Bearer JWT
                            ▼
┌────────────────────────────────────────────────────────┐
│                   REST API / FASTAPI                   │
│   • High-performance asynchronous Python web framework │
│   • Pydantic v2 request/response validation schemas    │
│   • Automated OpenAPI Documentation (/docs Swagger UI) │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│                 AUTHENTICATION + RBAC                  │
│   • Stateless RFC 7519 JSON Web Tokens (HS256)         │
│   • Argon2id cryptographic password hashing            │
│   • Multi-Role Access Control (USER, ANALYST, ADMIN)   │
│   • Strict Tenant Isolation (blocks cross-user access) │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│                  DOCUMENT INGESTION                    │
│   • Multi-format intake: PDF, Word DOCX, Plain TXT     │
│   • PyMuPDF (fitz) text coordinate & layout extraction │
│   • python-docx XML paragraph traversing               │
│   • Multi-tier validation: 25 MB ceiling, MIME types   │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│                  TEXT PREPROCESSING                    │
│   • Unicode normalization (NFKC)                       │
│   • Hyphenated line-break reconnection                 │
│   • Citation preservation (Section 11(6), Art. 226)    │
│   • Clean tokenization without damaging legal syntax   │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│                      NLP PIPELINE                      │
│   ├── 1. TF-IDF Scorer (Term Frequency - Inv Doc Freq) │
│   ├── 2. RAKE Scorer (Graph Co-Occurrence Degree/Freq) │
│   ├── 3. Tri-Model Hybrid Keyword Fusion (0.35/0.35/0.3)│
│   ├── 4. Named Entity Recognition (spaCy + Gazetteers) │
│   ├── 5. Clause Extraction (13 Standard Contract Types)│
│   ├── 6. Obligation Extractor (Modal Verbs/Prohibitions│
│   ├── 7. Structured Facts (Dates, Currencies, Deadlines│
│   └── 8. Information Retrieval (TF-IDF Passage Search) │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│                 SQLALCHEMY / DATABASE                  │
│   • Relational persistence via SQLAlchemy 2.0 ORM      │
│   • SQLite (Development) / PostgreSQL (Enterprise Ready│
│   • Tables: users, documents, analyses, keywords,      │
│     entities, audit_logs                               │
│   • Foreign key cascading deletes                      │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│                    RESULTS / REPORT                    │
│   • Document At-a-Glance Executive Summary             │
│   • Interactive Filterable Keyword & Entity Tables     │
│   • Side-by-side Two-Document Comparison (Cosine Sim)  │
│   • Multi-Page Printable PDF via PyMuPDF Vector Engine │
│   • Structured JSON Export                             │
│   • Institutional Legal Advice Disclaimer Banner       │
└────────────────────────────────────────────────────────┘
```

---

## 2. Where Core Academic Concepts Appear in the Architecture

### 2.1 Enterprise Systems (ES) Concepts
| Architectural Layer | Implementation in LexExtract | Academic Concept |
| :--- | :--- | :--- |
| **System Decoupling** | Three distinct tiers (React frontend, FastAPI backend, SQLAlchemy DB) | Three-Tier Architecture |
| **Authentication** | RFC 7519 JSON Web Tokens (HS256) | Stateless Security & Tokenization |
| **Cryptography** | Argon2id password hashing via `pwdlib[argon2]` | Modern Cryptographic Security |
| **Access Control** | Role-based permissions (`USER`, `ANALYST`, `ADMIN`) | Multi-Role Access Governance (RBAC) |
| **Data Protection** | `check_document_access` dependency returning HTTP 403 on tenant breach | Tenant Isolation / Horiz. Escalation Prevention |
| **Accountability** | Immutable `audit_logs` recording action, user, IP, timestamp | Non-Repudiation Governance Audit Trail |
| **Data Access** | SQLAlchemy 2.0 ORM with connection pooling & foreign key cascades | Object-Relational Mapping (ORM) |

---

### 2.2 Advanced Statistical & Text Mining Analysis (ASTMA) Concepts
| Architectural Layer | Implementation in LexExtract | Academic Concept |
| :--- | :--- | :--- |
| **Preprocessing** | Citation-preserving tokenizer, Unicode NFKC, line-reconnector | Legal Text Normalization & Tokenization |
| **Candidate Mining** | n-gram candidate generation (unigrams, bigrams, trigrams) | n-Gram Sliding Window Extraction |
| **Statistical Weighting**| Corpus frequency matrix using `TfidfVectorizer` | Term Frequency-Inverse Document Frequency |
| **Graph Mining** | Word degree to word frequency ratio over co-occurrence graphs | RAKE (Rapid Automatic Keyword Extraction) |
| **Model Fusion** | Normalized weighted combination (35% TF-IDF, 35% RAKE, 30% Lexicon) | Hybrid Score Fusion & Ranking |
| **Entity Tagging** | Linguistic POS patterns combined with court/act/statute gazetteers | Hybrid Named Entity Recognition (NER) |
| **Comparative IR** | Unit-norm vector dot product across document vocabulary projections | High-Dimensional Vector Cosine Similarity |
| **Empirical Evaluation**| Curated 12-doc gold-standard corpus, Micro/Macro P/R/F1, Top-K, ablation | Information Retrieval Benchmark Metrics |

---

### 2.3 IT Project Management (ITPM) Concepts
| Architectural Layer | Implementation in LexExtract | Academic Concept |
| :--- | :--- | :--- |
| **Scope Management** | 12-phase Work Breakdown Structure (`docs/WBS.md`) | PMBOK 100% Rule WBS Hierarchical Decomposition |
| **Schedule Control** | Milestone tracking and critical path analysis (`docs/PROJECT_TIMELINE.md`) | Phased Iterative Lifecycle & Gantt Scheduling |
| **Risk Management** | 10-point Risk Register (R-01 to R-10) with severity scoring (`docs/RISK_REGISTER.md`) | PMBOK Qualitative Risk Analysis & Contingency Planning |
| **Requirements** | Requirements Traceability Matrix (`docs/REQUIREMENTS_TRACEABILITY_MATRIX.md`) | Bidirectional Traceability Engineering |
| **Quality Assurance** | 6-tier QA Checklist (`docs/QA_CHECKLIST.md`) & 119 automated Pytest cases | IEEE 829 Software Test Plan & Execution |
| **Verification** | Empirical Requirement Coverage Report (`docs/REQUIREMENT_COVERAGE_REPORT.md`)| Quantitative Software Verification & Validation |

---

## 3. How to Explain the Architecture in 60 Seconds (Viva Pitch)

> *"LexExtract is built on a clean Three-Tier Enterprise Architecture. The Presentation Tier is a React 18 single-page app that visualizes legal documents and highlights extracted concepts. The Application Tier is powered by FastAPI, which exposes asynchronous REST microservices. When a request arrives, our security layer verifies the user's JWT token and enforces Role-Based Access Control and tenant isolation. 
> 
> The document is ingested via PyMuPDF or python-docx, and our preprocessor cleans the text while preserving statutory citations like Section 11(6). The text enters our ASTMA NLP pipeline, which extracts keywords using a hybrid combination of TF-IDF, RAKE graph scoring, and legal lexicons, while extracting 13 legal entity classes using spaCy and domain gazetteers. We also detect 13 standard contractual clauses, extract modal obligations, and compute cosine similarity for contract comparison. 
> 
> Finally, all structured data is persisted in a relational database using SQLAlchemy ORM, and full reports can be exported as printable PDFs. The entire project is traceable to our 12-phase WBS, 10-point Risk Register, and 119 automated passing tests."*
