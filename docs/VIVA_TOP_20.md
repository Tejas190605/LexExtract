# LexExtract — Top 20 Most Likely Viva Questions & Answers

**Subject Focus:** Tri-Disciplinary Defense (ES, ASTMA, ITPM)  
**Preparation Target:** Final Academic Viva Voce / Capstone Review  
**Date:** October 2026  

---

### Q1: What is the core problem LexExtract solves, and why not just use ChatGPT or an LLM?
**Answer:**  
"LexExtract solves the challenge of rapidly extracting, analyzing, and comparing legal contracts. We deliberately avoid cloud LLMs because uploading contracts to third-party APIs violates attorney-client privilege and data confidentiality laws. Furthermore, cloud LLMs are expensive on per-token pricing and suffer from non-deterministic hallucinations. LexExtract runs 100% locally on the server, provides sub-350ms processing latency, and uses mathematically explainable algorithms that guarantee 100% repeatable auditability."

---

### Q2: How does the system architecture demonstrate Enterprise Systems (ES) principles?
**Answer:**  
"LexExtract implements a decoupled three-tier enterprise architecture. The presentation tier is a React 18 single-page application built with Vite; the application tier is a FastAPI async ASGI server with Pydantic validation; and the data tier is a relational SQLite database managed via SQLAlchemy ORM. The system enforces strict Role-Based Access Control, stateless JWT authentication, multi-tenant document isolation, and an immutable audit logging table for compliance."

---

### Q3: How does the hybrid keyword extraction algorithm work in ASTMA?
**Answer:**  
"Our keyword engine uses a tri-factor fusion formula combining statistical TF-IDF, graph-based RAKE, and domain lexicon weighting. TF-IDF measures corpus-wide frequency discrimination; RAKE builds a word co-occurrence graph to capture multi-word collocations; and our legal lexicon assigns domain bonuses to recognized statutory phrases. The final composite score is calculated as:  
$$S = 0.45 \cdot S_{\text{tfidf}} + 0.35 \cdot S_{\text{rake}} + 0.20 \cdot S_{\text{legal}}$$  
This formula balances corpus distinctiveness, multi-word phrasing, and legal significance."

---

### Q4: Why did RAKE alone perform poorly in your ablation study?
**Answer:**  
"In our ablation study, RAKE alone achieved an F1-score of only 2.17%. This is because legal contracts use heavy punctuation—semicolons, enumerated sub-clauses, parentheticals like *(a)* or *(i)*, and nested clauses. In standard RAKE, punctuation acts as phrase delimiters, which artificially fractures co-occurrence graphs into single words, ruining graph degree calculations. Combining RAKE with TF-IDF and domain filters solves this breakdown."

---

### Q5: How is Named Entity Recognition (NER) implemented and evaluated?
**Answer:**  
"We use a hybrid dual-engine pipeline. A statistical spaCy model (`en_core_web_sm`) extracts general entities like persons, organizations, locations, and monetary amounts. A custom deterministic rule engine using compiled regular expressions extracts domain-specific legal entities such as statutory Acts, Sections, Courts, and Case Citations. When spans overlap, rule-based gazetteers take precedence over spaCy. In benchmark evaluation across 12 legal documents, our NER achieved 38.79% precision, 68.55% recall, and 49.55% F1-score."

---

### Q6: How does the system calculate Precision, Recall, and F1-score in ASTMA?
**Answer:**  
"We evaluate against a gold-standard benchmark annotated by legal experts:  
- **Precision:** $\frac{\text{True Positives}}{\text{True Positives} + \text{False Positives}}$ (fraction of extracted items that are correct).  
- **Recall:** $\frac{\text{True Positives}}{\text{True Positives} + \text{False Negatives}}$ (fraction of gold-standard items captured).  
- **F1-Score:** The harmonic mean: $2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$.  
We calculate both Micro-averages (aggregating totals across all documents) and Macro-averages (averaging individual document scores)."

---

### Q7: Why is the keyword extraction precision 12.50% at K=20, and does that indicate failure?
**Answer:**  
"No, in Information Retrieval, precision naturally drops as the retrieval cutoff $K$ increases because the model retrieves domain-adjacent phrases beyond the strict manual annotations. At $K=5$, our precision is 21.67%. More importantly, our recall is 23.26%, meaning the top-20 candidates capture almost a quarter of all manual annotations. This behavior is standard in Information Retrieval when evaluating un-pruned candidate sets."

---

### Q8: How does the document comparison engine compute similarity?
**Answer:**  
"Document comparison uses the Vector Space Model with Cosine Similarity. Both documents are tokenized and transformed into TF-IDF vector representations across the joint legal vocabulary. The cosine similarity is the cosine of the angle between the two vectors:  
$$\text{Cosine Similarity} = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\| \|\mathbf{v}\|}$$  
This yields a percentage score between 0% and 100%. In addition, the engine aligns corresponding clauses side-by-side and computes the vocabulary delta."

---

### Q9: How does the system extract contractual obligations?
**Answer:**  
"Our obligation parser in `clause_obligation_service.py` uses dependency and modal verb pattern matching. Sentences containing modal verbs such as *shall*, *must*, *agrees to*, and *is required to* are categorized as **Affirmative Duties**. Sentences containing negative modals like *shall not*, *must not*, or *will not* are categorized as **Prohibitions**. The engine also resolves the responsible subject entity and identifies deadline indicators like *within 30 days*."

---

### Q10: How does the in-document search work?
**Answer:**  
"Rather than a naive substring search, in-document search segments the document into paragraphs or clause chunks. It computes TF-IDF term weights for each passage relative to the user's query terms. Matches are ranked by cumulative passage relevance score, returning the match count, confidence score, and exact character offsets for instant UI highlighting."

---

### Q11: How is authentication and password security handled?
**Answer:**  
"Authentication uses stateless JSON Web Tokens (JWT) signed with HMAC-SHA256 (`HS256`) and a 60-minute expiration. User passwords are encrypted using the Argon2id hashing algorithm, the current industry gold standard recommended by OWASP. Zero plaintext passwords are ever stored or returned in API responses."

---

### Q12: How is multi-tenant document isolation enforced?
**Answer:**  
"Document access is strictly scoped to the authenticated user. In `backend/app/core/deps.py`, the `check_document_access` dependency queries the document and compares `document.owner_id` with the authenticated `current_user.id`. If a non-admin user attempts to access another user's document, analysis, or comparison, the system raises an `HTTP 403 Forbidden` exception."

---

### Q13: What role does Role-Based Access Control (RBAC) play in LexExtract?
**Answer:**  
"The system defines three roles:  
1. `USER`: Can upload documents, run analyses, and export reports for their own files.  
2. `ANALYST`: Advanced legal analysis permissions.  
3. `ADMIN`: Full access to the system, including viewing all tenant documents, managing users, and accessing the immutable governance audit ledger (`/api/v1/admin/audit-logs`)."

---

### Q14: How does the database design ensure data integrity and clean cascade deletes?
**Answer:**  
"Our relational schema in SQLAlchemy defines explicit foreign key relationships with `ondelete='CASCADE'`. When a user deletes a document, all associated `analysis_runs`, `extracted_keywords`, and `extracted_entities` are automatically purged by the database engine in a single transaction, preventing orphaned records."

---

### Q15: How did you manage project risks in accordance with ITPM?
**Answer:**  
"We maintained a formal Risk Register (`docs/RISK_REGISTER.md`) tracking 10 prioritized risks across technical, architectural, and operational domains. For instance, Risk RSK-01 (failure on scanned image PDFs) was mitigated by detecting zero-token streams and returning clear guidance to the user. Risk RSK-02 (tenant data leakage) was mitigated with automated RBAC regression tests."

---

### Q16: What is the Requirements Traceability Matrix (RTM) and what did it prove?
**Answer:**  
"The RTM (`docs/REQUIREMENTS_TRACEABILITY_MATRIX.md`) maps every functional requirement (FR-01 through FR-14) and non-functional requirement (NFR-01 through NFR-05) forward to its architectural design, concrete API endpoint, source file, automated test case, and pass result. It proved **100% test coverage and zero orphaned code**."

---

### Q17: What are the automated test results and build metrics?
**Answer:**  
"We executed the automated Pytest suite of 119 test cases covering unit models, services, RBAC authorization, integration flows, and edge cases. All **119 tests passed (100% pass rate)** with zero regressions. The frontend Vite production build completed cleanly with **0 errors and 0 warnings**."

---

### Q18: What happens if a user uploads a corrupt, oversized, or unsupported file?
**Answer:**  
"Our `DocumentValidator` service performs multi-layered defensive validation. It checks file extension against allowed types (`.pdf`, `.docx`, `.txt`), verifies the file size against the 25 MB ceiling, and validates magic bytes (e.g., `%PDF-` header). Unsupported extensions return `HTTP 400`, oversized files return `HTTP 413`, and corrupted documents are caught gracefully with user-friendly error messages."

---

### Q19: What are the primary limitations of the current implementation?
**Answer:**  
"The primary limitations are:  
1. **Scanned physical documents:** It processes computer-readable digital text streams; flat scans without an embedded OCR layer must be digitized beforehand.  
2. **Deterministic scope:** It extracts and categorizes structured information; it does not author or rewrite contracts.  
3. **Language:** It is optimized for English-language commercial and legal documents."

---

### Q20: What are the immediate future enhancements for LexExtract?
**Answer:**  
"Key future enhancements include:  
1. Integrating local Tesseract OCR into the ingestion pipeline for seamless scan handling.  
2. Expanding rule gazetteers to additional jurisdictions (US, UK, and European Union commercial laws).  
3. Implementing batch asynchronous queue workers for high-volume corporate due diligence discovery."
