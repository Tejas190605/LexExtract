# LexExtract — Academic Subject Mapping (ASTMA, ES, ITPM)

This document formally maps the implemented LexExtract software architecture and algorithmic capabilities to the academic syllabi of:
1. **ASTMA** — Advanced Software Tools, Methodologies & Applications
2. **ES** — Expert Systems & Software Engineering
3. **ITPM** — IT Project Management

---

## 1. ASTMA (Advanced Software Tools, Methodologies & Applications)

### 1.1 Information Retrieval (IR) & Natural Language Processing (NLP)
- **Tokenization & Citation-Aware Normalization:** Implementing specialized tokenizers that prevent destructive punctuation stripping across statutory citations (e.g., preserving `Section 11(6)` and `Article 226(1)`).
- **Candidate N-Gram Generation:** Extracting unigrams, bigrams, and trigrams with boundary-aware sliding windows.
- **Stopword Filtering with Domain Exceptions:** Standard stopword removal tailored with white-lists for legally discriminative particles (`whereas`, `hereinafter`, `pursuant to`).
- **TF-IDF Term Weighting:** Weighting local term frequencies against an inverse document frequency vector representing legal distribution.
- **Graph-Based Co-occurrence Analysis (RAKE):** Generating word co-occurrence matrices across clause boundaries and computing degree-to-frequency ratios.
- **Named Entity Recognition (NER):** Transition-based statistical sequence modeling via `spaCy` coupled with deterministic regex and gazetteer matchers.

### 1.2 Evaluation Methodologies & Quantitative Metrics
- **Contingency Matrix Computation:** Populating True Positives ($TP$), False Positives ($FP$), and False Negatives ($FN$) through strict normalized matching against curated ground truth.
- **Standard IR Metrics:**
  $$\text{Precision} = \frac{TP}{TP + FP}, \quad \text{Recall} = \frac{TP}{TP + FN}, \quad F_1 = \frac{2PR}{P + R}$$
- **Zero-Division Safeguards:** Mathematical boundary protection returning $0.0$ when denominators evaluate to zero, preventing IEEE 754 `NaN` corruption.
- **Ranked Retrieval Cutoffs (Top-K Evaluation):** Measuring Precision@K, Recall@K, and $F_1@K$ across $K \in \{5, 10, 20\}$ to validate ranking effectiveness.
- **Ablation Studies:** Isolating algorithmic sub-components (TF-IDF vs. RAKE vs. Lexicon Fusion) to quantify empirical value of domain gazetteers.
- **Taxonomic Error Analysis:** Systematic classification of failure modes into False Positives (over-generation), False Negatives (omissions), and Category Mismatches (correct boundary, inaccurate entity type).

---

## 2. ES (Expert Systems & Software Engineering)

### 2.1 Knowledge Representation & Rule-Based Inference
- **Domain Legal Gazetteers:** Encoding expert legal taxonomies across 7 statutory and transactional categories (Contract, Litigation, Corporate, Property, Statutory, Intellectual Property, Constitutional).
- **Pattern Matchers & Regular Expressions:** Symbolic production rules encoding legal syntax (e.g., judicial citations `W.P.(C) No. \d+/\d+`, Indian monetary expressions `Rs. [\d,]+`, and statutory provisions `Section \d+([A-Za-z])?`).
- **Conflict Arbitration:** Longest-match rule-based arbitration and confidence scoring to resolve entity span collisions between statistical and symbolic rules.

### 2.2 Software Engineering & Reliability
- **Three-Tier Architecture:** Complete decoupling of the Presentation Tier (React SPA), Application Tier (FastAPI), and Data Tier (SQLAlchemy ORM + SQLite).
- **Idempotent Data Migrations:** Self-healing, backward-compatible SQLite table schema migrations on application startup.
- **Automated Regression Testing:** 98 automated unit and integration tests executing across authentication, authorization, ingestion, NLP, and evaluation.

---

## 3. ITPM (IT Project Management)

### 3.1 Phased Work Breakdown Structure (WBS)
LexExtract was delivered across 9 phased iterations with strict acceptance verification at each milestone:
- **Phase 1:** Core Foundation, Architecture & Blueprint
- **Phase 2:** Database Design, Models & Repositories
- **Phase 3:** Document Ingestion & Text Preprocessing
- **Phase 4:** Keyword Extraction Pipeline (TF-IDF + RAKE + Lexicon)
- **Phase 5:** Named Entity Recognition (spaCy + Legal Rules)
- **Phase 6:** Authentication, Authorization, RBAC & Audit Ledger
- **Phase 7:** Legal UI, Interactive Document Viewer & Results Explorer
- **Phase 8:** ASTMA IR Evaluation Benchmark & Ablation Study
- **Phase 9:** Final Integration, Deployment Preparation & QA

### 3.2 Quality Assurance & Verification & Validation (V&V)
- **Independent Verification:** Continuous automated test execution establishing a 98/98 passing baseline.
- **End-to-End Browser Automation:** Full verification of user journeys and role restrictions using headless browser subagents.
- **Risk Management:** Authoring and maintaining an active project risk register addressing OCR limitations, vocabulary drift, and regulatory boundaries.

### 3.3 Security Governance & Compliance
- **Access Control & Least Privilege:** Role-Based Access Control enforcing discrete authorization for `USER`, `ANALYST`, and `ADMIN`.
- **Data Isolation:** Strict document ownership guards preventing horizontal privilege escalation.
- **Immutable Audit Trail:** Logging critical lifecycle actions (`LOGIN`, `DOCUMENT_UPLOAD`, `ANALYSIS_START`, `ANALYSIS_COMPLETE`, `UNAUTHORIZED_ACCESS`) with client IP and timestamps for institutional non-repudiation.
