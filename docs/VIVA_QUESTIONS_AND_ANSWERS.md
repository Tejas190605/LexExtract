# LexExtract — Comprehensive Viva Voce Questions & Answers (45+ Questions)

**Project Title:** LexExtract — Legal Document Keyword & Entity Extractor  
**Subject Integration:** Enterprise Systems (ES) • Advanced Statistical & Text Mining Analysis (ASTMA) • IT Project Management (ITPM)  
**Standard Structure:** Organized into 12 Core Academic Categories (A through L)  

---

## Category A: Project Basics

### Q1: Why did you choose this project?
- **Short Answer:** To address the severe inefficiency, cost, and opacity of manual legal document review using explainable text mining.
- **Detailed Explanation:** Legal professionals review voluminous agreements, judgments, and notices under strict time constraints. Generic search tools lack domain understanding, while commercial legal-tech systems are expensive, proprietary, and operate as unexplainable black boxes. LexExtract provides an open, local, three-tier architecture demonstrating verifiable information extraction without external AI API dependencies.
- **Project Context:** Implemented across 12 iterative engineering phases covering full-stack development, statistical NLP, and project governance.

### Q2: What problem does LexExtract solve?
- **Short Answer:** It extracts critical terms, clauses, obligations, facts, and entities from unstructured legal files and enables side-by-side contract comparison.
- **Detailed Explanation:** Unstructured legal texts (PDF, DOCX, TXT) bury essential business facts in dense legal prose. LexExtract normalizes text while preserving statutory citations, extracts ranked keywords and typed entities, identifies 13 standard contractual clauses, extracts modal duties and prohibitions, and computes cosine similarity diffs between contract versions.
- **Project Context:** Transforms a 20-page agreement into an immediate "Document At-a-Glance" summary with traceable source passages.

### Q3: What are the three core academic subjects integrated in this project?
- **Short Answer:** Enterprise Systems (ES), Advanced Statistical & Text Mining Analysis (ASTMA), and IT Project Management (ITPM).
- **Detailed Explanation:**
  - **ES:** Three-tier architecture, asynchronous FastAPI REST services, SQLAlchemy ORM, stateless JWT authentication, Argon2id hashing, multi-role RBAC, tenant document isolation, and immutable audit trails.
  - **ASTMA:** Statutory citation-preserving tokenization, TF-IDF, RAKE graph scoring, domain lexicon matching, spaCy linguistic NER, legal gazetteers, cosine vector similarity, and empirical IR benchmarking ($P, R, F_1$).
  - **ITPM:** 12-phase WBS, milestone scheduling, 10-point PMBOK Risk Register (R-01 to R-10), Requirements Traceability Matrix (RTM), IEEE 829 test plan/cases, and requirement coverage reporting.

---

## Category B: Enterprise Systems (ES)

### Q4: What is a Three-Tier Enterprise Architecture and how is it implemented?
- **Short Answer:** Separation of an application into Presentation, Application (Business Logic), and Data tiers.
- **Detailed Explanation:**
  - **Presentation Tier:** React 18 single-page application built with Vite and a tailored legal-tech dark slate design system.
  - **Application Tier:** FastAPI (Python 3.12+) running asynchronously on Uvicorn ASGI, managing authentication, document ingestion, and NLP pipelines.
  - **Data Tier:** SQLAlchemy 2.0 ORM with SQLite (development/academic default) and PostgreSQL production capability, backed by secure local filesystem storage.
- **Project Benefit:** Allows independent scaling, testing, and maintenance of each tier without architectural coupling.

### Q5: What is a REST API and why did you choose FastAPI?
- **Short Answer:** REST (Representational State Transfer) is a stateless client-server architectural style using standard HTTP verbs. FastAPI was chosen for native async support, automated OpenAPI documentation, and high throughput.
- **Detailed Explanation:** FastAPI utilizes Starlette and Pydantic v2 to enforce strict request/response data typing, automatic JSON serialization, and interactive Swagger UI (`/docs`). It provides asynchronous non-blocking request handling, essential for document processing pipelines.
- **Project Metric:** Average API response time for complex analysis is under 250 milliseconds.

### Q6: How does Role-Based Access Control (RBAC) work in LexExtract?
- **Short Answer:** Restricts API endpoints and UI features based on user roles encoded in signed JWT payloads.
- **Detailed Explanation:** We define three hierarchical roles:
  1. `USER`: Can upload, analyze, search, compare, and export their own documents.
  2. `ANALYST`: Includes USER privileges plus access to ASTMA empirical evaluation benchmarking.
  3. `ADMIN`: Full administrative control, including user account management and governance audit log inspection.
- **Implementation:** Enforced via FastAPI dependency injection (`require_admin`, `get_current_user`).

### Q7: How do you prevent cross-user document access (Horizontal Privilege Escalation)?
- **Short Answer:** Through the `check_document_access` backend dependency verifying tenant ownership on every query.
- **Detailed Explanation:** Every document and analysis request validates that `document.user_id == current_user.id` or that `current_user.role == 'ADMIN'`. If User B attempts to access User A's document ID or analysis ID, the backend immediately intercepts the request and returns **HTTP 403 Forbidden**.
- **Test Verification:** Verified in automated security test suites (`test_authorization.py` and `test_phase12_quality_edge_cases.py`).

### Q8: What is the purpose of the Governance Audit Ledger?
- **Short Answer:** Non-repudiation tracking of all sensitive institutional operations for compliance.
- **Detailed Explanation:** Critical actions (`LOGIN_SUCCESS`, `DOCUMENT_UPLOAD`, `DOCUMENT_DELETE`, `ANALYSIS_EXECUTE`, `DOCUMENT_COMPARE`, `REPORT_EXPORT`) are written permanently to the `audit_logs` table, storing user ID, action type, client IP address, status, and UTC timestamp.

---

## Category C: Advanced Statistical & Text Mining Analysis (ASTMA)

### Q9: Why is keyword extraction useful in legal documents?
- **Short Answer:** It identifies core legal concepts, governing subject matter, and operational rights without reading the entire document.
- **Detailed Explanation:** In contract review, keywords reveal whether a document governs software licensing, commercial leasing, employment non-competition, or dispute arbitration, facilitating fast indexing, search, and routing.

### Q10: What is TF-IDF and how does it work mathematically?
- **Short Answer:** Term Frequency-Inverse Document Frequency balances local word prominence against global corpus rarity.
- **Detailed Explanation:**
  $$\text{TF}(t, d) = \frac{f_{t,d}}{\sum_{t' \in d} f_{t',d}}$$
  $$\text{IDF}(t, D) = \ln\left(\frac{1 + |D|}{1 + |\{d \in D : t \in d\}|}\right) + 1$$
  $$\text{TF-IDF}(t, d, D) = \text{TF}(t, d) \times \text{IDF}(t, D)$$
  Words appearing frequently in one contract but rarely across the legal corpus receive elevated weights, penalizing boilerplate terms.

### Q11: What is RAKE and how does it score candidate keywords?
- **Short Answer:** Rapid Automatic Keyword Extraction scores candidate keywords based on a word co-occurrence graph.
- **Detailed Explanation:** RAKE partitions text by stopwords and phrase delimiters, builds a word co-occurrence matrix, and calculates each word's degree ($\text{deg}(w)$) and frequency ($\text{freq}(w)$). The word score is:
  $$\text{Score}(w) = \frac{\text{deg}(w)}{\text{freq}(w)}$$
  Multi-word candidate phrase scores are the sum of their individual member word scores.

### Q12: Why use a hybrid keyword extraction approach instead of a single model?
- **Short Answer:** Individual models have complementary blind spots: TF-IDF overlooks phrase co-occurrence, RAKE over-segments punctuated legal text, and lexicons miss novel terminology.
- **Detailed Explanation:** Our tri-model fusion combines:
  $$\text{Score}_{\text{final}} = 0.35 \times \text{Score}_{\text{TF-IDF}} + 0.35 \times \text{Score}_{\text{RAKE}} + 0.30 \times \text{Score}_{\text{Lexicon}}$$
  This produces candidates that are statistically discriminative, grammatically cohesive, and legally meaningful.

### Q13: Why did TF-IDF perform better than RAKE in your empirical benchmark?
- **Short Answer:** Legal drafting syntax contains dense intra-clause punctuation (semicolons, commas, section numbers) that artificially fractures RAKE co-occurrence graphs.
- **Detailed Explanation:** RAKE relies on contiguous word runs between stopwords and punctuation. Legal sentences often exceed 80 words with numerous parenthetical statutory citations (`Section 10(2)(a)`). These delimiters prematurely terminate RAKE phrase extraction, reducing recall to 3.10% and F1 to 0.0217, whereas TF-IDF achieved an F1 of 0.1789.

### Q14: How does document comparison using vector cosine similarity work?
- **Short Answer:** It measures the cosine of the angle between two documents' TF-IDF feature vectors in multi-dimensional term space.
- **Detailed Explanation:**
  $$\text{Similarity}(A, B) = \frac{\mathbf{v}_A \cdot \mathbf{v}_B}{\|\mathbf{v}_A\| \|\mathbf{v}_B\|} = \frac{\sum_{i=1}^n A_i B_i}{\sqrt{\sum_{i=1}^n A_i^2} \sqrt{\sum_{i=1}^n B_i^2}}$$
  A score of 1.0 indicates identical vocabulary and frequency distributions, while 0.0 indicates completely disjoint term usage.

---

## Category D: IT Project Management (ITPM)

### Q15: What is a Work Breakdown Structure (WBS) and how was it used?
- **Short Answer:** A hierarchical decomposition of total project scope into manageable work packages adhering to the 100% rule.
- **Detailed Explanation:** LexExtract was decomposed across 12 distinct phases (`docs/WBS.md`), from requirements engineering (Phase 1) through backend foundation, NLP engines, RBAC, UI viewer, benchmarking, value-enhancements, and final quality assurance (Phase 12).

### Q16: What is a Requirements Traceability Matrix (RTM)?
- **Short Answer:** A grid linking user/functional requirements to system design components, code modules, and automated test cases.
- **Detailed Explanation:** LexExtract's RTM (`docs/REQUIREMENTS_TRACEABILITY_MATRIX.md`) tracks all 19 requirements (`FR-01` to `FR-14` and `NFR-01` to `NFR-05`) forward to implementation files and backward to automated test IDs (`TC-001` to `TC-025`), ensuring 100% verifiable requirement coverage.

### Q17: What are the major risks in your Risk Register and how were they mitigated?
- **Short Answer:** R-01 (Poor Extraction Accuracy), R-02 (Unsupported Documents), R-03 (Unauthorized Access), R-04 (Large Document Scaling), and R-05 (False-Positive Clauses).
- **Detailed Explanation:** In `docs/RISK_REGISTER.md`, each risk is assigned probability, impact, risk score (1-9), mitigation, contingency, and status. For instance, R-03 (Risk Score 6) was mitigated via tenant database filtering and JWT RBAC dependencies, confirmed via automated security regression tests.

### Q18: What is Precision, Recall, and F1-score in Information Retrieval?
- **Short Answer:**
  - **Precision:** Fraction of extracted items that are correct: $\frac{TP}{TP + FP}$.
  - **Recall:** Fraction of true items that were successfully extracted: $\frac{TP}{TP + FN}$.
  - **F1-Score:** Harmonic mean of precision and recall: $2 \times \frac{P \times R}{P + R}$.
- **Project Metric:** On our 12-document benchmark, Keyword Micro F1 is 0.1626, Top-5 Precision is 0.2167, and Entity Micro F1 is 0.4955.

---

## Category E: Backend Architecture

### Q19: How is the backend organized?
- **Short Answer:** In a modular directory structure under `backend/app/` following clean architecture principles.
- **Detailed Explanation:**
  - `core/`: Configuration, database engines, security, dependencies.
  - `models/`: SQLAlchemy ORM entity definitions.
  - `schemas/`: Pydantic request and response models.
  - `services/`: Business logic (ingestion, preprocessor, scorers, NER, clause/obligation service, evaluation, audit).
  - `api/v1/`: Versioned API endpoints partitioned by resource (`auth`, `documents`, `analysis`, `admin`, `evaluation`).

### Q20: Why use Pydantic v2 schemas alongside SQLAlchemy ORM models?
- **Short Answer:** Separation of internal persistence representations from external network data contracts.
- **Detailed Explanation:** SQLAlchemy models manage database columns, relationships, and foreign keys. Pydantic schemas validate client inputs, sanitize output payloads, prevent mass-assignment vulnerabilities, and generate OpenAPI specifications.

---

## Category F: Frontend Architecture

### Q21: Why React 18 and Vite instead of traditional server-rendered templates?
- **Short Answer:** To deliver an interactive, responsive legal-tech workspace with multi-layer text highlighting and instantaneous tab switching.
- **Detailed Explanation:** Legal document inspection requires dynamic client-side interactions: toggling highlighting layers (keywords, entities, plain text), filtering clause tables, and searching in-document passages. Vite enables near-instant hot-module replacement and optimized production bundling (105 kB gzipped).

### Q22: How does the Interactive Document Viewer highlight text?
- **Short Answer:** By mapping extracted token character offsets directly onto the normalized document text stream.
- **Detailed Explanation:** The highlighter segments the text into ordered non-overlapping spans corresponding to keyword occurrences and entity boundaries, wrapping them in interactive CSS styled badges with tooltips.

---

## Category G: Database Architecture

### Q23: What is the database structure of LexExtract?
- **Short Answer:** Relational schema with 6 primary tables: `users`, `documents`, `analysis_runs`, `extracted_keywords`, `extracted_entities`, and `audit_logs`.
- **Detailed Explanation:**
  - `users` (1 to Many) $\rightarrow$ `documents`
  - `documents` (1 to Many) $\rightarrow$ `analysis_runs`
  - `analysis_runs` (1 to Many) $\rightarrow$ `extracted_keywords` & `extracted_entities`
  - `users` (1 to Many) $\rightarrow$ `audit_logs`
- **Integrity:** Configured with foreign key constraints and cascading deletions (`cascade="all, delete-orphan"`).

### Q24: Why use SQLite for development and how easily can you switch to PostgreSQL?
- **Short Answer:** SQLite is zero-configuration and serverless, perfect for local demonstration. Because we use SQLAlchemy ORM, switching to PostgreSQL requires only updating the `DATABASE_URL` environment variable.
- **Detailed Explanation:** No raw SQL queries or database-specific dialect hacks are used. All database queries utilize SQLAlchemy 2.0 select statements, ensuring seamless portability to enterprise relational database management systems.

---

## Category H: Security & Access Control

### Q25: How are passwords stored securely?
- **Short Answer:** Using Argon2id with memory-hard hashing parameters via `pwdlib[argon2]`.
- **Detailed Explanation:** Argon2id is the winner of the Password Hashing Competition (PHC). It resists GPU/ASIC brute-force attacks and side-channel timing attacks, far surpassing outdated MD5, SHA-1, or plain SHA-256.

### Q26: What is inside the JWT access token and how is it verified?
- **Short Answer:** Base64URL-encoded header, payload (subject user ID, email, role, expiration timestamp), and an HMAC-SHA256 signature.
- **Detailed Explanation:** The backend signs the token using a secret key. Every incoming request to protected routes must include the token in the `Authorization: Bearer <token>` header. The server verifies the signature and expiration without making a database lookup, ensuring stateless horizontal scalability.

---

## Category I: Natural Language Processing & Legal Intelligence

### Q27: What is Named Entity Recognition (NER) and what entities are extracted?
- **Short Answer:** NER identifies and classifies real-world entities into predefined categories. LexExtract extracts 13 legal entity classes.
- **Detailed Explanation:** Extracts `COURT`, `STATUTE`, `SECTION`, `CASE_NUMBER`, `ORGANIZATION`, `PERSON`, `LEGAL_ROLE`, `DATE`, `MONEY`, `LOCATION`, `JURISDICTION`, `PENALTY`, and `CONTRACT_TYPE`. Combines statistical spaCy POS patterns with deterministic legal gazetteer dictionaries.

### Q28: How are Important Clauses detected across the 13 categories?
- **Short Answer:** Through semantic keyword clustering and sentence-level syntactic regex matching.
- **Detailed Explanation:** Categories include Termination, Confidentiality, Dispute Resolution, Governing Law, Indemnification, Liability, Payment, Force Majeure, IP, Non-Compete, Severability, Amendment, and Entire Agreement. The engine scans section headings and operative paragraphs for co-occurring trigger terms (e.g., `indemnify`, `hold harmless`, `claims`, `damages`) and outputs confidence ratings with source snippets.

### Q29: How are Contractual Obligations and Prohibitions extracted?
- **Short Answer:** By detecting modal auxiliary verbs paired with dependency subject identification.
- **Detailed Explanation:** The extractor identifies modal patterns (`shall`, `must`, `agrees to`, `is required to`). If negated (`shall not`, `agrees not to`, `prohibited from`), it classifies the clause as a `Prohibition`. It extracts the responsible party, operative action, deadline, and source sentence.

### Q30: How does In-Document Search work?
- **Short Answer:** It indexes document passages and ranks matches using passage-level TF-IDF relevance scoring.
- **Detailed Explanation:** The document is split into natural paragraphs and pages. Matching paragraphs are scored based on query term frequency and sentence position, returning match counts, offsets, and contextual snippets with a direct "Jump to Viewer" button.

---

## Category J: Testing & Quality Assurance

### Q31: What testing levels did you perform on LexExtract?
- **Short Answer:** Unit testing, integration testing, security testing, negative/edge-case testing, and end-to-end system testing.
- **Detailed Explanation:**
  - **Unit:** Individual functions (tokenizers, candidate filters, scoring formulas).
  - **Integration:** Multi-step workflows (file upload $\rightarrow$ DB persistence $\rightarrow$ background analysis).
  - **Security:** Password hashing, JWT tampering, RBAC role boundaries, cross-user isolation.
  - **Edge Cases:** Empty files, single words, unusual punctuation, massive documents (4,500+ words), invalid extensions.
  - **Results:** 119 passed automated tests with 0 failures (`python -m pytest`).

---

## Category K: Limitations & Engineering Trade-Offs

### Q32: Why didn't you use a Large Language Model (LLM) or RAG architecture?
- **Short Answer:** To guarantee explainability, zero hallucinations, data privacy, and deterministic execution without external cloud API costs.
- **Detailed Explanation:** Commercial legal teams are strictly bound by client confidentiality and cannot upload unredacted contracts to third-party cloud APIs (like OpenAI or Anthropic). Furthermore, LLMs suffer from probabilistic hallucinations. LexExtract uses deterministic, open mathematical algorithms where every extracted phrase and score can be mathematically audited and reproduced.

### Q33: What happens when a user uploads a scanned image PDF?
- **Short Answer:** The system gracefully rejects it with an explanatory HTTP 400 alert explaining that selectable text is absent.
- **Detailed Explanation:** LexExtract ingests native computer-readable text streams. Scanned raster images lack text layers and return zero characters. Rather than crashing, the pre-extraction validator detects empty text and informs the user to pre-OCR the document using external tools (like Tesseract).

---

## Category L: Future Scope

### Q34: What are reasonable future enhancements for LexExtract?
- **Short Answer:** Integrating an embedded local OCR engine (Tesseract), scaling the benchmark to 500+ multilingual contracts, and adding real-time collaborative legal annotation.
- **Detailed Explanation:**
  1. **Embedded OCR:** Automatically converting scanned image PDFs into searchable text before ingestion.
  2. **Multilingual & Regional Acts:** Expanding gazetteers to regional state enactments and multilingual contracts (e.g., Hindi, Marathi, French legal briefs).
  3. **Collaborative Annotation:** Real-time multi-user redlining and clause negotiation tracking with WebSocket synchronization.
