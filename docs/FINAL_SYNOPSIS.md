# PROJECT SYNOPSIS

## Project Title
**LexExtract: Intelligent Legal Document Keyword & Entity Extraction System**

---

## 1. Background
In contemporary legal practice, legal firms, corporate compliance departments, and judicial institutions process substantial volumes of unstructured text spanning commercial contracts, court judgments, statutory provisions, arbitration pleadings, and legal notices. Manual document triage requires significant practitioner time to identify essential governing clauses, statutory citations, participating entities, and financial liabilities. Automated information retrieval and natural language processing provide a structured, deterministic approach to indexing and extracting domain concepts from legal documents.

---

## 2. Problem Statement
Commercial legal briefs and court judgments exhibit dense syntax, multi-word legal nominal compounds, archaic preambles, and cross-statutory citations. Generic natural language processing tools frequently fail on such texts because standard normalizers destructively strip essential punctuation (e.g., transforming `Section 11(6)` into `section 11 6`), general statistical models misclassify specialized judicial forums as generic commercial corporations, and generic stopword lists eliminate legally meaningful particles. Furthermore, existing commercial legal-tech systems are proprietary, closed-source, and fail to provide explainable scoring or reproducible academic benchmarking.

---

## 3. Aim & Objectives
The aim of LexExtract is to design, implement, and empirically evaluate a domain-adapted Information Extraction and Retrieval system for legal documents.

### Specific Objectives:
1. Engineer a decoupled Three-Tier Enterprise Architecture separating presentation, application, and persistence layers.
2. Develop a multi-format document parser supporting `.pdf` and `.docx` that preserves statutory subsection citations.
3. Build a tri-model keyword extraction engine combining TF-IDF statistical weighting (35%), RAKE word co-occurrence graph scoring (35%), and a 1,200-term legal domain lexicon (30%).
4. Construct a hybrid legal Named Entity Recognition (NER) pipeline fusing statistical linguistic parsing (`spaCy`) with symbolic regular expressions and legal gazetteers across 13 legal categories.
5. Implement stateless authentication (RFC 7519 JWT), Argon2id password hashing, Role-Based Access Control (`USER`, `ANALYST`, `ADMIN`), cross-user document isolation, and an immutable audit ledger.
6. Provide an interactive visual document viewer with multi-layer token-span highlighting.
7. Implement an empirical Information Retrieval evaluation engine benchmarking precision, recall, and F1-score against a curated ground-truth legal dataset.

---

## 4. Proposed Solution & Architecture
LexExtract is designed on a **Three-Tier Architecture**:
- **Presentation Tier:** A responsive Single-Page Application (SPA) built with React 18, Vite, and Tailwind CSS.
- **Application Tier:** An asynchronous RESTful API service built with FastAPI, Python 3.12+, and Pydantic validation schemas.
- **Data Tier:** Relational persistence using SQLite via SQLAlchemy 2.0 ORM (with direct migration capability to PostgreSQL) and local structured file storage with SHA-256 integrity validation.

```
[ React 18 / Tailwind SPA ] <──REST/JWT──> [ FastAPI Application Tier ] <──ORM──> [ SQLite Relational DB ]
                                                    │
                                     ┌──────────────┴──────────────┐
                                     ▼                             ▼
                           [ Tri-Model Keyword Engine ]   [ Hybrid Legal NER ]
                           (TF-IDF + RAKE + Lexicon)      (spaCy + Gazetteers)
```

---

## 5. Methodology & Technical Workflow
1. **Document Ingestion:** PDF files are extracted via PyMuPDF (`pymupdf`) preserving text block coordinates; DOCX files are extracted via `python-docx` traversing XML paragraphs and tables.
2. **Citation-Preserving Normalization:** Text is cleaned and whitespace is collapsed while explicitly preserving statutory parentheses.
3. **Keyword Extraction:** N-grams ($1 \le n \le 3$) are generated, filtered against legal stopword exceptions, and scored via weighted rank fusion:
   $$\text{Final Score} = 0.35 \cdot S_{\text{TF-IDF}} + 0.35 \cdot S_{\text{RAKE}} + 0.30 \cdot S_{\text{Lexicon}}$$
4. **Legal Entity Extraction:** Entities are detected via `spaCy` and symbolic gazetteers covering Courts, Statutes, Sections, Case Citations, Parties, Legal Roles, and Monetary Values. Longest-match span arbitration resolves overlaps.
5. **ASTMA IR Evaluation:** System extractions are compared against a curated 12-document benchmark corpus containing 129 gold keywords and 157 gold entities. Unmanipulated Precision, Recall, and F1 metrics are calculated with zero-division safeguards.

---

## 6. Technology Stack
- **Frontend:** React 18, Vite, Tailwind CSS, Lucide React, Axios.
- **Backend:** FastAPI, Uvicorn (ASGI), Pydantic v2.
- **NLP & Mining:** scikit-learn (`TfidfVectorizer`), in-house RAKE, spaCy (`en_core_web_sm`), regex rules.
- **Document Processing:** PyMuPDF, `python-docx`.
- **Security:** PyJWT (HS256), `pwdlib[argon2]` (Argon2id password hashing).
- **Database:** SQLite with SQLAlchemy 2.0 ORM.
- **Testing:** Pytest, HTTPX TestClient, Playwright browser automation.

---

## 7. Actual Outcomes & Verification
- **Test Suite:** **98 / 98 tests passing** (100%) in 27.34 seconds.
- **Frontend Build:** 1,559 modules compiled cleanly with zero errors.
- **Cross-User Data Isolation:** Enforced on all routes; unauthorized access attempts are blocked with HTTP 403 Forbidden.
- **Benchmark Evaluation Results (12 Documents, 3,875 Words):**
  - **Keywords:** Macro Precision = 0.125, Macro Recall = 0.224, Macro $F_1 = 0.160$.
  - **Entities:** Macro Precision = 0.383, Macro Recall = 0.690, Macro $F_1 = 0.489$.
  - **Top-5 Keywords:** Precision@5 = 0.217 (confirming effective ranking of high-confidence legal terms).
  - **Ablation Study:** LexExtract Hybrid ($F_1 = 0.163$) demonstrates balanced performance over standalone TF-IDF ($F_1 = 0.179$) and RAKE ($F_1 = 0.022$).
- **Average Document Processing Latency:** 824.0 ms per document.

---

## 8. Academic Subject Relevance
- **ASTMA (Advanced Social, Text and Media Analytics):** Tokenization, n-gram generation, RAKE co-occurrence graph scoring, TF-IDF statistical weighting, Named Entity Recognition, contingency tables ($TP, FP, FN$), Precision, Recall, $F_1$-score, Top-K evaluation, and error analysis.
- **ES (Enterprise Systems):** Three-Tier architecture, asynchronous REST API services, relational persistence, schema migrations, stateless JWT security, Argon2id hashing, and horizontal isolation.
- **ITPM (IT Project Management):** 9-phase Work Breakdown Structure, risk register, requirements traceability matrix, automated regression testing, and non-repudiation audit logging.

---

## 9. Limitations & Future Scope
- **Limitations:** No OCR engine for scanned PDF images; benchmark consists of 12 curated documents; exact normalized matching without embeddings; not intended as legal advice.
- **Future Scope:** Integration of Tesseract OCR for physical scanned archives; transformer fine-tuning (Legal-BERT); interactive statutory dependency cross-referencing graphs; managed PostgreSQL cloud deployment.

---

## 10. Key References
1. Salton, G., & McGill, M. J. (1983). *Introduction to Modern Information Retrieval*. McGraw-Hill.
2. Rose, S., Engel, D., Cramer, N., & Cowley, W. (2010). Automatic Keyword Extraction from Individual Documents. In *Text Mining: Applications and Theory*. John Wiley & Sons.
3. Honnibal, M., & Montani, I. (2017). spaCy 2: Natural language understanding with Bloom embeddings, convolutional neural networks and incremental parsing.
4. Chalkidis, I., et al. (2020). LEGAL-BERT: The Muppets straight out of Law School. *Findings of EMNLP 2020*.
