# LexExtract — Final Project Demonstration Script (Viva & Evaluation)

**Project Title:** LexExtract — Legal Document Keyword & Entity Extractor  
**Subject Focus:** Enterprise Systems (ES) • Advanced Statistical & Text Mining Analysis (ASTMA) • IT Project Management (ITPM)  
**Total Demonstration Time:** 5 to 10 Minutes  
**Target Audience:** PBL Evaluation Committee, External Examiners & Faculty Evaluators  

---

## Complete Demonstration Sequence (Steps 1 to 22)

### 1. Problem Statement
- **WHAT TO SHOW:** Introduction slide or browser landing screen (`http://localhost:5173`).
- **WHAT TO CLICK:** Point cursor to the LexExtract header and subtitle.
- **WHAT TO SAY:**
  > *"Respected evaluators, reviewing legal documents like commercial leases, contracts, and arbitrations is time-consuming and prone to human oversight. Generic search tools often fail because legal drafting uses specialized syntax, and standard NLP can corrupt statutory citations like Section 11(6). Furthermore, proprietary cloud LLMs pose data privacy concerns and act as unexplainable black boxes. LexExtract solves this by providing an explainable, local Three-Tier platform using statistical and rule-based text mining to extract key information, detect clauses, extract obligations, compare contracts, and generate executive reports without external AI APIs."*

---

### 2. Login & Authentication
- **WHAT TO SHOW:** Login Page (`http://localhost:5173/login`).
- **WHAT TO CLICK:** Click preset **"Admin (Full Governance Access)"** (or enter `admin@lexextract.local` / `AdminPassword123!`), then click **"Sign In to Portal"**.
- **WHAT TO SAY:**
  > *"Under Enterprise Systems, we enforce secure stateless authentication using RFC 7519 JSON Web Tokens (JWT) signed with HS256. Passwords are cryptographically hashed using the memory-hard Argon2id algorithm. Upon submitting valid credentials, the client securely stores the bearer token and redirects to the dashboard."*

---

### 3. Dashboard
- **WHAT TO SHOW:** Executive Dashboard (`http://localhost:5173/`).
- **WHAT TO CLICK:** Hover over the summary metric cards at the top.
- **WHAT TO SAY:**
  > *"The Dashboard provides immediate visibility into system throughput: total cataloged documents, words processed, completed analyses, and extracted legal entities. Below, users see recent uploads with quick links to results, viewer, or downloads, along with our active institutional legal disclaimer."*

---

### 4. Upload Document
- **WHAT TO SHOW:** Document Intake / New Analysis Page (`/new_analysis`).
- **WHAT TO CLICK:** Click **"New Document Intake"** in the sidebar. Select or drag-and-drop `sample_documents/sample_contract.pdf` (or `sample_arbitration_agreement.txt`). Click **"Ingest & Process Document"**.
- **WHAT TO SAY:**
  > *"Our document ingestion engine supports PDF, Word DOCX, and TXT files. We enforce a 25 MB file size ceiling, check MIME types, and verify magic bytes. PyMuPDF extracts the text stream while preserving paragraph structures, section symbols, and statutory citations."*

---

### 5. Document Processing & Automated Analysis
- **WHAT TO SHOW:** Analysis execution progress indicator.
- **WHAT TO CLICK:** Click **"Execute Analysis"** (or observe automatic redirection to `/results`).
- **WHAT TO SAY:**
  > *"Once text is extracted, our asynchronous FastAPI backend executes the analytical pipeline in approximately 230 milliseconds. It generates n-gram candidates, computes TF-IDF and RAKE scores, matches legal lexicons, identifies named entities with spaCy, and scans for 13 standard contractual clauses."*

---

### 6. Document Overview (At-a-Glance)
- **WHAT TO SHOW:** Analysis Results $\rightarrow$ **Overview** tab.
- **WHAT TO CLICK:** Click the **"Overview"** tab.
- **WHAT TO SAY:**
  > *"The Overview tab provides an executive summary of the document. Here we see the detected document type ('Commercial Lease Agreement'), identified parties ('Apex Realty Holdings', 'Zenith Logistics'), execution dates, financial totals, and detected clauses. Notice the 'Attention Areas' card—it highlights critical risks like indemnification requirements and unilateral termination clauses."*

---

### 7. Keyword Extraction
- **WHAT TO SHOW:** Analysis Results $\rightarrow$ **Keywords** tab.
- **WHAT TO CLICK:** Click the **"Keywords"** tab. Filter by category (e.g. `Contract` or `Corporate`).
- **WHAT TO SAY:**
  > *"Under ASTMA, we avoid simple word counts. Our keyword engine is a hybrid tri-model: 35% TF-IDF for corpus-wide discriminative weighting, 35% RAKE for graph word co-occurrence scoring, and 30% domain legal taxonomy matching. In the table, you see each phrase's TF-IDF score, RAKE score, and combined final score. Clicking 'Highlight' will navigate directly to that term in the document viewer."*

---

### 8. Entity Extraction (NER)
- **WHAT TO SHOW:** Analysis Results $\rightarrow$ **Entities** tab.
- **WHAT TO CLICK:** Click the **"Entities"** tab. Filter by entity type (e.g. `ORGANIZATION`, `ACT`, `MONEY`).
- **WHAT TO SAY:**
  > *"For Named Entity Recognition, we combine statistical NLP using spaCy with deterministic symbolic legal gazetteers. This allows us to accurately detect and tag 13 legal categories—such as Courts, Statutes, Sections, Parties, and Jurisdictions—with transparent confidence scores."*

---

### 9. Important Clauses
- **WHAT TO SHOW:** Analysis Results $\rightarrow$ **Important Clauses** tab.
- **WHAT TO CLICK:** Click the **"Important Clauses"** tab. Filter by `Found`.
- **WHAT TO SAY:**
  > *"The Important Clause Finder scans for 13 controlled contractual categories—such as Termination, Confidentiality, Dispute Resolution, Governing Law, Indemnification, and Force Majeure. For every detected clause, it provides the category, confidence rating, source section, and the exact extracted text passage."*

---

### 10. Obligations & Responsibilities
- **WHAT TO SHOW:** Analysis Results $\rightarrow$ **Obligations & Duties** tab.
- **WHAT TO CLICK:** Click the **"Obligations & Duties"** tab. Filter by `Prohibition` or `Payment`.
- **WHAT TO SAY:**
  > *"Contract review requires knowing who is obligated to do what. Our obligation engine analyzes modal verbs like 'shall', 'must', and 'agrees to'. It separates affirmative duties from prohibitions—such as 'shall not assign' or 'shall not disclose'—and identifies the responsible party, deadline, and source sentence."*

---

### 11. Dates and Monetary Values
- **WHAT TO SHOW:** Analysis Results $\rightarrow$ **Dates & Money** tab.
- **WHAT TO CLICK:** Click between **"Dates"**, **"Monetary Sums"**, and **"Deadlines"**.
- **WHAT TO SAY:**
  > *"The Structured Facts engine extracts execution dates, payment amounts across currencies (Rupees, Dollars, Euros, Pounds), and timeline durations. Each fact preserves its original textual context and provides a 'Locate' button for document traceability."*

---

### 12. In-Document Search
- **WHAT TO SHOW:** Analysis Results $\rightarrow$ **In-Document Search** tab.
- **WHAT TO CLICK:** Type `'notice'` or `'indemnity'` into the search input and press Enter.
- **WHAT TO SAY:**
  > *"The search feature performs Information Retrieval across document passages using TF-IDF relevance scoring. It displays match counts, section names, relevance scores, and contextual snippets. Clicking 'Open in Viewer' takes us directly to that passage in the full text."*

---

### 13. Document Viewer & Source Traceability
- **WHAT TO SHOW:** Document Viewer Page (`/viewer`).
- **WHAT TO CLICK:** Click **"Open in Viewer"** from a search result or clause snippet. Toggle layers: **"All Overlays"**, **"Keywords Only"**, **"Entities Only"**, **"Clean Plain Text"**.
- **WHAT TO SAY:**
  > *"This is our interactive Document Viewer. Every extracted result in LexExtract is traceable to source text. Notice how the searched term and key phrases are highlighted dynamically. Users can toggle visualization layers or inspect entity drawers, ensuring full transparency rather than an opaque black box."*

---

### 14. Document Comparison (Diff Engine)
- **WHAT TO SHOW:** Document Comparison Page (`/compare`).
- **WHAT TO CLICK:** Select **Document A** (`sample_commercial_lease.pdf`) and **Document B** (`sample_contract.pdf`), then click **"Execute Comparative Analysis"**.
- **WHAT TO SAY:**
  > *"Legal practitioners frequently need to compare agreement versions. Our comparison module computes the ASTMA TF-IDF vector cosine similarity between the documents and renders a side-by-side clause alignment table. It flags each clause as UNCHANGED, MODIFIED, ADDED, or REMOVED, allowing rapid contract deviation analysis."*

---

### 15. Export Analysis Report (PDF & JSON)
- **WHAT TO SHOW:** Export dropdown on the Analysis Results page.
- **WHAT TO CLICK:** Click **"Export Report"** $\rightarrow$ **"Export Printable PDF"** (or **"Export JSON Data"**).
- **WHAT TO SAY:**
  > *"Users can export complete audit-ready reports. Our backend generates a clean multi-page vector PDF via PyMuPDF containing the document metadata, executive summary, detected clauses, obligations, and top keywords. Both exports strictly include our prominent non-legal advice disclaimer."*

---

### 16. Document History & Management
- **WHAT TO SHOW:** Repository History Page (`/history`).
- **WHAT TO CLICK:** Click **"Repository History"** in the sidebar.
- **WHAT TO SAY:**
  > *"The Repository History provides a complete institutional archive of uploaded documents, showing file types, sizes, analysis statuses, and timestamps. Deleting a document triggers foreign key cascading deletion in the database, ensuring zero orphaned rows."*

---

### 17. Governance Audit Ledger
- **WHAT TO SHOW:** Governance Audit Ledger Page (`/admin_audit`).
- **WHAT TO CLICK:** Click **"Governance Audit Ledger"** in the sidebar (Admin only).
- **WHAT TO SAY:**
  > *"Under enterprise governance and security, every critical action—such as logins, document uploads, searches, comparisons, and exports—is permanently recorded in the immutable `audit_logs` table with user IDs, timestamps, and client IP addresses."*

---

### 18. System Architecture Overview
- **WHAT TO SHOW:** Architecture diagram slide or `docs/ARCHITECTURE_FOR_VIVA.md`.
- **WHAT TO SAY:**
  > *"LexExtract follows a classic Three-Tier Enterprise Architecture: a React 18 presentation tier with a responsive dark-slate design system, a FastAPI business logic tier providing RESTful microservices, and a relational persistence tier using SQLAlchemy ORM with SQLite for development and seamless PostgreSQL support."*

---

### 19. Enterprise Systems (ES) Concepts Mapping
- **WHAT TO SAY:**
  > *"In Enterprise Systems, we demonstrated: Three-Tier architecture, stateless JWT authentication, Argon2id cryptographic hashing, multi-role RBAC (USER, ANALYST, ADMIN), strict tenant document isolation where User A cannot access User B's files (verified with HTTP 403 Forbidden), and non-repudiation audit logging."*

---

### 20. ASTMA Concepts Mapping
- **WHAT TO SAY:**
  > *"In ASTMA, we demonstrated: citation-preserving text preprocessing, TF-IDF term weighting, RAKE graph co-occurrence analysis, hybrid score fusion, linguistic spaCy NER, vector cosine similarity for contract comparison, and empirical benchmarking on a curated 12-document gold-standard corpus reporting real, unmanipulated Precision, Recall, and F1 scores."*

---

### 21. ITPM Concepts Mapping
- **WHAT TO SAY:**
  > *"In IT Project Management, we demonstrated: a 12-phase Work Breakdown Structure (WBS), milestone scheduling, a 10-point PMBOK Risk Register (R-01 to R-10), an IEEE 829 Test Plan, a Requirements Traceability Matrix mapping all 19 requirements to code and tests, and 100% automated test coverage across 119 passing tests."*

---

### 22. Limitations & Conclusion
- **WHAT TO SAY:**
  > *"To maintain academic integrity: LexExtract requires computer-readable documents and does not run OCR on scanned images. It uses deterministic, explainable NLP rather than generative AI to prevent hallucinations and eliminate external API costs. In conclusion, LexExtract is fully working, rigorously tested, and complete across all three subject areas. We are now ready for your questions."*
