# LexExtract — 3-Minute Comprehensive Technical Pitch

## Structure
- **Minute 0:00 – 0:45:** Problem, Motivation & Domain Sensitivity
- **Minute 0:45 – 1:30:** Three-Tier Architecture & NLP Pipeline
- **Minute 1:30 – 2:15:** Interactive UI, Security & RBAC
- **Minute 2:15 – 3:00:** Empirical Evaluation Results, Limitations & Future Scope

---

## The 3-Minute Script

### Part 1: Problem & Motivation (0:00 – 0:45)
> "Good morning, respected evaluators. In legal practice and corporate compliance, advocates and analysts spend countless hours reading voluminous briefs, commercial contracts, and appellate judgments to extract governing laws, participating parties, and liability terms. 
>
> Standard NLP tools fail on legal text for three primary reasons:
> 1. Standard text normalizers aggressively strip punctuation, corrupting statutory citations such as *Section 11(6)* or *Article 226(1)*.
> 2. General-purpose NER taggers lack legal hierarchy awareness, frequently misclassifying high courts and statutory tribunals as generic business corporations.
> 3. Existing commercial legal-tech systems are closed-source, proprietary black boxes that offer no transparency or reproducible benchmarks for academic evaluation.
>
> We built **LexExtract** to solve these challenges through domain-adapted, explainable information extraction."

### Part 2: Architecture & NLP Extraction Pipeline (0:45 – 1:30)
> "LexExtract is engineered on a decoupled Three-Tier Enterprise Architecture: a React 18 single-page application on the frontend, an asynchronous FastAPI application tier in Python, and an SQLAlchemy relational database tier utilizing SQLite.
>
> When a user uploads a PDF or Word document, our ingestion engine extracts the text while preserving statutory subsection parentheses. For keyword extraction, we implement a tri-model rank fusion combining cross-corpus TF-IDF (35%), RAKE word co-occurrence graph scoring (35%), and a curated 1,200-term legal domain lexicon (30%). 
>
> For Named Entity Recognition, we combine statistical sequence parsing from spaCy with custom regular expressions and legal gazetteers across 13 specialized legal classes—including Courts, Statutes, Sections, Case Citations, and Monetary Sums."

### Part 3: Interactive Features, Security & Governance (1:30 – 2:15)
> "The extracted information is delivered through an editorial legal-tech interface. The **Document Viewer** maps token offsets directly to the text, allowing practitioners to toggle highlight layers for keywords and entity categories.
>
> From an enterprise systems perspective, the platform enforces stateless RFC 7519 JWT authentication with Argon2id password hashing and Role-Based Access Control across three roles: *User*, *Analyst*, and *Admin*. 
>
> Strict document ownership guards prevent horizontal privilege escalation—if User B attempts to access User A's brief, the system returns an HTTP 403 Forbidden error. All critical operations are permanently recorded in an immutable audit ledger with client IP addresses and timestamps."

### Part 4: Empirical Evaluation, Limitations & Conclusion (2:15 – 3:00)
> "Under our ASTMA curriculum, we did not stop at simply building the software; we built an empirical Information Retrieval evaluation engine. The system benchmarks extractions against a curated corpus of 12 legal documents containing 129 gold keywords and 157 gold entities.
>
> We report honest, unmanipulated metrics: a keyword F1-score of **0.160** and an entity F1-score of **0.489**. Looking at Top-5 retrieval cutoffs, precision rises to **0.217**, proving that our ranking algorithm effectively prioritizes high-confidence legal concepts. Our ablation study confirms that the hybrid model outperforms standalone TF-IDF and RAKE.
>
> The system processes documents in an average of 824 milliseconds and is verified by **98 passing backend tests** and a clean production build. While the current system does not perform OCR on scanned PDFs, future work includes integrating Tesseract OCR and fine-tuning Legal-BERT.
>
> In conclusion, LexExtract delivers a robust, tested, and empirically evaluated legal document extraction system. Thank you."
