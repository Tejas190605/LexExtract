# LexExtract — Comprehensive Viva Voce Preparation Guide (25 Questions & Answers)

This guide provides concise, technically accurate answers aligned directly with the actual implementation of LexExtract for academic examinations.

---

### Q1: What is LexExtract?
**Answer:** LexExtract is an intelligent, domain-specific Information Extraction and Retrieval application designed to ingest unstructured legal briefs, contracts, and court judgments, and automatically extract, score, and highlight domain keywords and named legal entities.

### Q2: Why focus on legal documents?
**Answer:** Legal documents possess distinctive domain characteristics—dense syntactic preambles, archaic Latin maxims, complex cross-statutory citations, and multi-word nominal compounds—that cause generic off-the-shelf NLP tools to fail or produce excessive false positives.

### Q3: What core problem does LexExtract solve?
**Answer:** Legal professionals spend excessive manual billable hours reviewing voluminous briefs to identify governing statutes, participating parties, financial obligations, and dispute clauses. LexExtract accelerates document triage and indexing through automated, structured concept extraction.

### Q4: Why is keyword extraction important in legal tech?
**Answer:** Keywords serve as content anchors and search descriptors, enabling instant semantic indexing, categorization across legal disciplines (e.g., Contract, Intellectual Property, Arbitration), and rapid clause retrieval.

### Q5: What is Natural Language Processing (NLP)?
**Answer:** NLP is an interdisciplinary subfield of computer science and artificial intelligence focused on enabling software to parse, understand, and extract structured meaning from human natural language text.

### Q6: What text preprocessing steps does LexExtract perform?
**Answer:** The system performs layout-aware text extraction (via PyMuPDF for PDF and python-docx for DOCX), newline and whitespace normalization, stopword filtering with legal vocabulary protection, and punctuation normalization that strictly preserves statutory parenthesis (such as `Section 11(6)`).

### Q7: What is TF-IDF and how is it used in LexExtract?
**Answer:** Term Frequency-Inverse Document Frequency (TF-IDF) evaluates how important a word is to a specific document within a collection. LexExtract uses TF-IDF to score candidate terms against a legal reference corpus, accounting for 35% of the final hybrid keyword score.

### Q8: What is RAKE and how is it used in LexExtract?
**Answer:** Rapid Automatic Keyword Extraction (RAKE) is an unsupervised, domain-independent algorithm that identifies multi-word phrases using stopword delimiters and word co-occurrence graphs. The degree-to-frequency ratio ($\text{deg}(w)/\text{freq}(w)$) scores phrase cohesion, contributing 35% to the keyword score.

### Q9: What is Named Entity Recognition (NER)?
**Answer:** NER is an information extraction subtask that identifies and classifies key unstructured text spans into predefined categories, such as persons, organizations, locations, courts, and legal statutes.

### Q10: Why integrate legal-specific lexicons and gazetteers?
**Answer:** Statistical NLP models alone lack legal semantic awareness (e.g., they often misclassify `"Supreme Court of India"` as a generic `ORGANIZATION`). A curated lexicon of 1,200+ terms and regex gazetteers provides domain guidance and accurate classification.

### Q11: What is Precision in Information Retrieval?
**Answer:** Precision measures the exactness of the extraction pipeline:
$$\text{Precision} = \frac{TP}{TP + FP}$$
It represents the percentage of predicted keywords or entities that were genuinely correct according to the ground truth.

### Q12: What is Recall in Information Retrieval?
**Answer:** Recall measures the completeness of the extraction pipeline:
$$\text{Recall} = \frac{TP}{TP + FN}$$
It represents the percentage of actual ground-truth concepts that the model successfully retrieved.

### Q13: What is the F1-score?
**Answer:** $F_1$-score is the harmonic mean of Precision and Recall:
$$F_1 = \frac{2 \cdot \text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$$
It provides a single balanced metric, penalizing extreme imbalances between precision and recall.

### Q14: What is the difference between a keyword and an entity?
**Answer:** A keyword is a topical phrase or conceptual descriptor representing document subject matter (e.g., `"liquidated damages"`), whereas a named entity is a specific, typed real-world reference (e.g., `"High Court of Delhi"` classified as `COURT`).

### Q15: Why choose FastAPI for the backend?
**Answer:** FastAPI offers native asynchronous I/O, automatic request/response validation through Pydantic v2 schemas, high throughput comparable to NodeJS/Go, and automatic generation of interactive OpenAPI Swagger documentation (`/docs`).

### Q16: Why choose React and Vite for the frontend?
**Answer:** React enables a modular, state-driven component architecture essential for multi-layer document highlighting and dynamic explorer filters. Vite provides fast Hot Module Replacement during development and optimized tree-shaken static production bundles.

### Q17: Why use SQLite with SQLAlchemy ORM?
**Answer:** SQLite requires zero server daemon setup and is ideal for standalone demonstration and academic reproducibility. SQLAlchemy ORM completely decouples the application logic from database specifics, allowing migration to PostgreSQL simply by changing the `DATABASE_URL` in `.env`.

### Q18: How is authentication implemented?
**Answer:** Authentication uses stateless RFC 7519 JSON Web Tokens (JWT) signed with HMAC-SHA256 (`HS256`). Client passwords are never stored in plaintext and are hashed using the Argon2id password-hashing algorithm.

### Q19: What is Role-Based Access Control (RBAC)?
**Answer:** RBAC restricts system privileges based on user roles. LexExtract implements three distinct roles: `USER` (document upload, viewing, and personal analysis), `ANALYST` (system benchmarking and evaluation), and `ADMIN` (user management and institutional audit log inspection).

### Q20: How is document ownership and data isolation enforced?
**Answer:** Every document and analysis record is linked to an `owner_id`. Backend dependency guards (`check_document_access`) verify ownership on every request. If a non-admin user attempts to access another user's document or analysis by enumerating IDs, the request is immediately rejected with HTTP 403 Forbidden.

### Q21: How was the evaluation benchmark dataset created?
**Answer:** A controlled legal benchmark corpus was assembled consisting of 12 diverse public-domain/synthetic legal documents (3,875 words) spanning commercial contracts, court judgments, legal notices, statutes, and arbitration agreements. Each document has a paired human-readable ground-truth JSON annotation file containing gold keywords and typed entities.

### Q22: What are False Positives in your system?
**Answer:** False Positives are concepts predicted by the NLP pipeline that are not present in the curated ground truth. Examples include procedural contractual phrases (e.g., `"herein referred"`) or generic header terms.

### Q23: What are False Negatives in your system?
**Answer:** False Negatives are genuine ground-truth concepts that the pipeline failed to extract. Examples include complex statutory sections not present in the base frequency dictionary or multi-token organization acronyms.

### Q24: What are the main limitations of LexExtract?
**Answer:** 
1. The system does not perform OCR on scanned image-only PDFs.
2. The benchmark corpus comprises 12 curated documents (project scale rather than multi-gigabyte corpus).
3. Evaluation uses strict normalized matching rather than semantic embeddings.
4. LexExtract is an academic analysis tool and does not provide legal advice.

### Q25: What future enhancements could be added?
**Answer:** Future enhancements include integrating Tesseract OCR for scanned historical judgments, fine-tuning a transformer model (e.g., Legal-BERT) for contextual embedding extraction, adding legal citation cross-referencing graphs, and deploying to cloud Kubernetes environments.
