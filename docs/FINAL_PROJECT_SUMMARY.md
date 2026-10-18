# LexExtract — Final Project Summary & Academic Synthesis

**Academic Year:** 2026  
**Course Context:** Project-Based Learning (PBL) Capstone  
**Integrated Subjects:** Enterprise Systems (ES), Advanced Statistical & Text Mining Analysis (ASTMA), Information Technology Project Management (ITPM)  
**Status:** **FEATURE COMPLETE & RELEASE FROZEN (v1.0.0)**  

---

## 1. Title
**LexExtract: A High-Throughput, Local-First Legal Document Intelligence Platform for Keyword, Entity, and Clause Mining.**

---

## 2. Problem Statement
Modern legal document review is notoriously labor-intensive, slow, and expensive. Law firms and corporate in-house departments routinely process hundreds of multi-page agreements, contracts, and dispute notices. Existing automated solutions often rely on closed cloud-hosted LLM APIs, creating severe risks of client confidentiality breaches, unpredictable subscription costs, and non-deterministic hallucinated outputs. There is a pressing need for a local-first, explainable, and privacy-preserving legal extraction and comparison platform.

---

## 3. Motivation
- **Confidentiality:** Legal documents contain strictly privileged client communications and trade secrets. Cloud transmission is restricted under attorney-client privilege and data sovereignty mandates.
- **Explainability:** In litigation and legal due diligence, algorithmic outputs must be traceable to exact statutory provisions, page offsets, and deterministic mathematical scores.
- **Economic Feasibility:** Eliminates recurring per-token cloud API charges, making legal-tech accessible to small practices and academic environments.

---

## 4. Objectives
1. Build an enterprise-grade multi-tier web platform with role-based access control and tenant isolation.
2. Develop a hybrid text mining pipeline combining statistical n-gram TF-IDF, graph-based RAKE, and curated domain lexicons.
3. Formulate a dual-engine Named Entity Recognizer (NER) resolving 13 legal entity classes across Indian and international jurisdictions.
4. Implement automated extraction of critical clauses, obligations, dates, monetary totals, and contractual deadlines.
5. Provide side-by-side document comparison with cosine similarity and report export capabilities (PDF & JSON).
6. Subject the entire platform to rigorous IEEE 830 traceability, Pytest automation, and ASTMA empirical benchmarking.

---

## 5. Proposed System
LexExtract is a local-first legal intelligence suite. Users authenticate via Argon2id credentials, upload legal instruments (.pdf, .docx, .txt), and receive structured, interactive breakdowns of clauses, duties, entities, and keywords in under 350 ms. All processing occurs locally on the server without external network dependencies.

---

## 6. Key Features
1. **Multi-Format Ingestion:** Stream parsing for PDF, Word (.docx), and plain text with page segmentation.
2. **Hybrid Keyword Extraction:** Unigram/bigram/trigram candidate generation with weighted fusion scoring (TF-IDF + RAKE + Domain Lexicon).
3. **Legal Entity Extraction:** Detection across 13 classes (Acts, Sections, Courts, Case Citations, Persons, Organizations, etc.).
4. **Important Clause Detection:** Automated detection of 13 clause classes (Confidentiality, Termination, Indemnity, Arbitration, etc.).
5. **Contractual Obligation Extractor:** Modal verb analysis separating affirmative duties (*shall*) from prohibitions (*shall not*).
6. **Structured Facts & Chronology:** Multi-currency detection (₹, $, €, £), dates, and deadline timeframes.
7. **In-Document Search:** TF-IDF passage-level relevance scoring with instant text offset navigation.
8. **Document Comparison:** TF-IDF cosine vector similarity score (0–100%) and aligned clause diffing.
9. **Executive Reporting:** PyMuPDF multi-page vector PDF generation and structured JSON exports.
10. **Administrative Governance:** Immutable audit trail logging actor actions, IP addresses, and timestamps.

---

## 7. System Architecture
A decoupled 3-tier architecture:
- **Presentation Tier:** React 18 Single Page Application (SPA), Vite 5, Tailwind CSS.
- **Application Tier:** FastAPI (Python 3.14 async ASGI framework), Pydantic v2 validation models, modular service layer.
- **Data Tier:** SQLAlchemy 2.0 ORM over SQLite 3 with cascading foreign keys and disk storage for uploaded documents.

---

## 8. Technology Stack
- **Backend:** Python 3.14, FastAPI, Uvicorn, SQLAlchemy 2.0, Pydantic v2, PyMuPDF (fitz), python-docx.
- **NLP / Text Mining:** spaCy (`en_core_web_sm`), scikit-learn (TfidfVectorizer), custom RAKE graph scorer, regex rule engines.
- **Security:** Argon2id (`passlib`), PyJWT (RFC 7519), Python-multipart.
- **Frontend:** React 18, Vite 5, React Router DOM 6, Axios, Tailwind CSS, Lucide React icons.
- **Testing:** Pytest 9.1.1, pytest-asyncio, HTTPX.

---

## 9. Enterprise Systems (ES) Concepts
- Multi-tier modularity and presentation-application separation.
- RESTful HTTP API conventions and OpenAPI standard documentation.
- Role-Based Access Control (`ADMIN`, `ANALYST`, `USER`) and strict multi-tenant document isolation.
- ACID relational data modeling and database connection lifecycle management.
- Comprehensive security audit ledger and defensive input sanitation.

---

## 10. ASTMA Concepts
- Text preprocessing (tokenization, sentence splitting, lowercasing, punctuation normalization).
- Statistical n-gram generation and stopword filtering with legal domain preservation.
- TF-IDF calculation against a curated reference legal background corpus.
- RAKE graph-based word co-occurrence matrix and degree-to-frequency scoring.
- Information extraction (gazetteers, regex heuristics, spaCy statistical NER).
- Information retrieval (TF-IDF passage scoring, Vector Space Model cosine similarity).
- Quantitative empirical evaluation (Micro/Macro Precision, Recall, F1-score) and ablation analysis.

---

## 11. ITPM Concepts
- 14-phase structured software development lifecycle.
- Work Breakdown Structure (WBS) with 4-level decomposition.
- Risk management tracking 10 prioritized risks with mitigation plans.
- IEEE 830 Requirements Traceability Matrix linking 19 requirements to code and test cases.
- Formal Quality Assurance (QA) checklists and project closeout governance.

---

## 12. NLP Methodology
1. **Normalization:** Standardizes whitespace and legal citations (e.g., *Sec. 11* $\rightarrow$ *Section 11*).
2. **Candidate Generation:** Generates unigram, bigram, and trigram candidates.
3. **Filtering:** Strips common English stopwords while preserving essential legal terms (*prima facie*, *suo moto*, *de facto*).
4. **Scoring:** Combines TF-IDF ($S_{\text{tfidf}}$), RAKE ($S_{\text{rake}}$), and domain weight ($S_{\text{legal}}$):
   $$S_{\text{composite}} = 0.45 \cdot S_{\text{tfidf}} + 0.35 \cdot S_{\text{rake}} + 0.20 \cdot S_{\text{legal}}$$
5. **NER Deduplication:** Rule-based legal entities take precedence over statistical spaCy spans to resolve overlapping boundaries.

---

## 13. Database Design
Relational SQLite schema containing `users`, `documents`, `analysis_runs`, `extracted_keywords`, `extracted_entities`, and `audit_logs` tables with cascading foreign keys and indexes.

---

## 14. Security & Isolation
- Passwords hashed using Argon2id.
- Stateless Bearer JWT tokens with 60-minute expiration.
- Document ownership verified on every protected API call (`HTTP 403` on cross-tenant access).
- Magic byte validation and 25 MB payload ceiling.

---

## 15. Testing & Verification
- 119 automated test cases covering authentication, ingestion, NLP pipelines, comparison, export, RBAC, and error edge cases.
- Pass rate: **100% (119/119 tests passed)**.
- Vite frontend production build: **0 errors, 0 warnings**.
- End-to-end browser user journey: **100% verified**.

---

## 16. Evaluation & ASTMA Benchmarking
Evaluated across 12 dual-annotated legal documents (4,801 words, 169 gold keywords, 147 gold entities):
- Keyword Extraction: Precision: **12.50%**, Recall: **23.26%**, F1: **16.26%** (Top-5 Precision: **21.67%**).
- Named Entity Recognition: Precision: **38.79%**, Recall: **68.55%**, F1: **49.55%**.
- Processing Latency: Average of **230.5 ms** per document.

---

## 17. Results & Key Findings
- Hybrid fusion scoring produces substantially more readable multi-word legal terms than raw TF-IDF or RAKE alone.
- Local execution achieves sub-second processing latency with zero cloud transmission overhead.
- Deterministic extraction guarantees 100% repeatable audit trails for litigation and due diligence.

---

## 18. Limitations
- Physical paper scans without OCR layers require pre-digitization.
- Currently optimized for English-language commercial and dispute resolution documents.
- Rule-based gazetteers require periodic updates for newly enacted statutes.

---

## 19. Future Scope
- Local Tesseract OCR integration for automated flat image intake.
- Multi-jurisdictional expansion (US/UK/EU specialized statutory corpuses).
- Parallel processing for high-volume batch document discovery.

---

## 20. Conclusion
LexExtract demonstrates that a local-first, explainable, and privacy-preserving legal document analysis platform can be successfully built, rigorously evaluated, and cleanly deployed. By harmonizing Enterprise Systems architecture, ASTMA text mining rigor, and ITPM project governance, LexExtract delivers a complete, production-ready capstone project.
