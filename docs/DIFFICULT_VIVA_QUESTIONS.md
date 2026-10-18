# LexExtract — Difficult Viva Defense & Academic Justifications

This document prepares candidates for challenging technical questions frequently posed by external examiners and faculty panels regarding design trade-offs, algorithmic choices, and academic rigor.

---

### Q1: "Why did you not simply use a Large Language Model (e.g., GPT-4 or Claude)?"
**Examiner's Premise:** Modern LLMs can extract entities and keywords through zero-shot prompting; why engineer custom pipelines?

**Defense:**
1. **Determinism and Reproducibility:** LLM generation is inherently probabilistic. In legal compliance, auditing, and academic evaluation, identical inputs must yield identical extraction scores and offsets. LexExtract produces deterministic scores based on mathematical formulas.
2. **Explainability and Auditing:** LLMs function as black boxes. In LexExtract, every keyword score is broken down into clear components: $0.35 \cdot S_{\text{TF-IDF}} + 0.35 \cdot S_{\text{RAKE}} + 0.30 \cdot S_{\text{Lexicon}}$. Examiners and practitioners can see why a term was selected.
3. **Data Privacy and On-Premise Operation:** Commercial legal documents are bound by attorney-client privilege and non-disclosure agreements. Sending sensitive briefs to third-party commercial cloud LLM APIs violates confidentiality. LexExtract runs completely offline on local hardware.
4. **Computational Efficiency:** An LLM inference call can take several seconds and require high-end GPU hardware. LexExtract processes a 350-word agreement in ~824 milliseconds on a consumer CPU.

---

### Q2: "Why not use BERT or a transformer-based embedding model?"
**Examiner's Premise:** Pre-trained transformer models (such as BERT or RoBERTa) offer contextual awareness; why use TF-IDF and RAKE?

**Defense:**
1. **Hardware Constraints:** Training or hosting a transformer model requires dedicated GPU memory (VRAM), making deployment on standard consumer laptops or lightweight student environments impractical.
2. **Academic Focus:** For the ASTMA curriculum, demonstrating foundational Information Retrieval techniques—such as vector space TF-IDF, graph co-occurrence (RAKE), and contingency matrix computation—provides direct evidence of understanding core text mining principles.
3. **Domain Vocabulary Misalignment:** Standard BERT models are trained on Wikipedia and BooksCorpus. Without extensive domain fine-tuning on legal corpora (e.g., Legal-BERT), standard BERT struggles with specialized statutory phrasing. Our rule gazetteer directly addresses this domain gap.
4. **Appropriate Pipeline Architecture:** LexExtract already incorporates statistical neural models via `spaCy`'s transition-based tagger for general entities, combining it with symbolic rules where statistical models fail on legal structures.

---

### Q3: "Why is your keyword F1-score around 0.16? Isn't that low?"
**Examiner's Premise:** In machine learning benchmarks, accuracy scores above 80% are common; why is the keyword F1-score ~0.16?

**Defense:**
1. **Exact Normalized Matching:** Our evaluation compares extracted terms against human-curated ground truth using strict normalized string matching. In natural language, there are many valid ways to phrase a concept. If the ground truth has `"indemnity"` and the system extracts `"indemnification"`, exact matching scores it as a False Negative and a False Positive, penalizing both Precision and Recall.
2. **Subjectivity of Keyword Annotation:** Different legal experts frequently choose different keyword subsets from the same document. A human annotator might select 10 core concepts, while the extraction pipeline identifies 20 valid domain terms. The additional 10 terms are technically scored as False Positives, lowering Precision.
3. **Integrity in Academic Reporting:** Many student projects artificially inflate scores by setting broad similarity thresholds or hard-coding expected predictions. We report actual unmanipulated empirical results.
4. **Top-K Ranking Validates the Model:** Looking at Top-5 cutoffs, Precision rises to **0.217**, proving that the highest-ranked candidates have higher overlap with the expert annotations.

---

### Q4: "How do you know your ground truth is accurate and unbiased?"
**Examiner's Premise:** The benchmark was assembled by the students; how is it validated?

**Defense:**
1. **Curated Project-Level Ground Truth:** We explicitly document in `ANNOTATION_GUIDELINES.md` that our benchmark is a curated capstone dataset, not an externally peer-reviewed standard like CUAD or LEDGAR.
2. **Clear Inclusion Guidelines:** Annotations follow strict written criteria:
   - Must be domain-specific legal terms, not general English words.
   - Must represent substantive legal obligations, remedies, or procedural terms.
   - Entities must be tagged with explicit categories according to statutory definitions.
3. **Public Availability:** All 12 documents and paired JSON annotations are openly stored in `backend/data/evaluation/` so anyone can inspect and verify the ground-truth annotations directly.

---

### Q5: "What happens when the system encounters completely unseen legal terminology?"
**Examiner's Premise:** If a new statutory term is not in your 1,200-word lexicon, will the system miss it?

**Defense:**
1. **Tri-Model Fallback Design:** The pipeline does not depend solely on the domain lexicon. If a term is not in the dictionary, $S_{\text{Lexicon}} = 0.0$, but the term is still scored by TF-IDF (35%) and RAKE graph co-occurrence (35%).
2. **Frequency and Co-occurrence Extraction:** An unlisted legal phrase that appears frequently in key clauses will still score highly via TF-IDF and RAKE, allowing it to be extracted and ranked.
3. **Category Assignment:** In such cases, the keyword is assigned to the `General` category rather than a specific legal domain, but it is not discarded.

---

### Q6: "How would you scale LexExtract to handle 100,000 documents per day?"
**Examiner's Premise:** SQLite and local disk storage cannot handle enterprise volume; how does the architecture scale?

**Defense:**
1. **Decoupled Architecture:** The system is already structured in Three Tiers. The application tier (FastAPI) is stateless and can be horizontally scaled behind a load balancer (e.g., Nginx or AWS ALB).
2. **Database Migration:** SQLAlchemy ORM allows switching from SQLite to a managed PostgreSQL cluster (e.g., Amazon RDS) simply by changing `DATABASE_URL` in `.env`.
3. **Object Storage:** Local file storage (`storage/uploads/`) would be replaced with Amazon S3 or Cloudflare R2 using pre-signed upload URLs.
4. **Asynchronous Task Queue:** Heavy NLP extraction jobs would be offloaded to Celery workers with a Redis message broker, decoupling document upload from pipeline execution.

---

### Q7: "Why did you choose SQLite over PostgreSQL for the current project?"
**Examiner's Premise:** PostgreSQL is standard for production systems; why use SQLite here?

**Defense:**
1. **Portability and Ease of Evaluation:** SQLite requires no external service daemons, background processes, or database credentials. Any evaluator can clone the repository, run `python scripts/init_db.py`, and immediately have a functional system.
2. **Full Relational Features:** LexExtract uses foreign keys, cascade deletes, indices, and transactions. SQLite supports all of these through SQLAlchemy.
3. **Zero Code Changes for PostgreSQL:** Because all queries use SQLAlchemy ORM rather than raw SQLite dialect queries, migrating to PostgreSQL requires only a driver installation (`psycopg2`) and a connection string change.

---

### Q8: "What would you change or improve in Version 2.0?"
**Examiner's Premise:** What are the most significant technical areas for improvement?

**Defense:**
1. **OCR Integration:** Add Tesseract OCR to support scanned, image-only legal documents.
2. **Semantic Similarity Matching:** Complement exact string matching with cosine similarity over Legal-BERT embeddings to reward near-synonyms during evaluation.
3. **Interactive Citation Graphs:** Build a dependency network mapping references between statutory sections and court judgments.
4. **Active Learning:** Allow practitioners to accept or reject extracted keywords, updating user-specific lexicons over time.
