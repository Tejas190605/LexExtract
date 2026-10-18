# ITPM Project Risk Register

**Project Title:** LexExtract — Legal Document Keyword & Entity Extractor  
**Subject:** Information Technology Project Management (ITPM)  
**Standard:** PMBOK Risk Management Framework  
**Risk Scoring Matrix:** Probability (Low=1, Medium=2, High=3) $\times$ Impact (Low=1, Medium=2, High=3) = Risk Score (1-9)  
- **1–3 (Low Severity):** Monitor and manage via standard operational controls.  
- **4–5 (Medium Severity):** Proactive mitigation and automated validation required.  
- **6–9 (High Severity / Critical):** Architectural safeguards, active unit testing, and contingency plans mandatory.  

---

## Comprehensive Risk Log (R-01 to R-10)

| ID | Risk Description | Prob. | Impact | Risk Score | Mitigation Strategy | Contingency Plan | Status |
| :---: | :--- | :---: | :---: | :---: | :--- | :--- | :---: |
| **R-01** | **Poor NLP Extraction Accuracy**<br/>Statistical extractors output low-quality keywords or miss essential contractual obligations. | Medium (2) | High (3) | **6 (High)** | Benchmark against 12-document curated gold standard; combine TF-IDF, RAKE, and domain lexicon; perform ablation evaluation. | Fall back to domain lexicon keywords and rule-based candidate filters; provide manual inspection in UI. | **Mitigated** |
| **R-02** | **Unsupported / Corrupted Documents**<br/>Users upload scanned image PDFs (without OCR), encrypted PDFs, or non-text binaries. | High (3) | Medium (2) | **6 (High)** | Multi-tier file validation checking file headers, MIME types, and text length; graceful HTTP 400 error handling. | Display clear UI alert explaining file lack of selectable text; guide user to convert or OCR the file. | **Mitigated** |
| **R-03** | **Unauthorized Document Access**<br/>Malicious users attempt to view, download, or compare legal files belonging to other users. | Medium (2) | High (3) | **6 (High)** | Strict tenant isolation in database queries (`user_id == current_user.id`), stateless JWT tokens, and RBAC middleware returning 403 Forbidden. | Comprehensive audit logging in `audit_logs` table tracking every authorization failure with IP address. | **Mitigated** |
| **R-04** | **Large Document Processing Failure**<br/>Uploading massive 100+ page contracts causes memory exhaustion or timeout. | Medium (2) | High (3) | **6 (High)** | Upload size ceiling enforced (max 25 MB); chunked sentence processing and efficient regex/tokenization pipelines. | Graceful degradation: limit extraction to first 50 pages or return timeout error with guidance to chunk document. | **Mitigated** |
| **R-05** | **False-Positive Clause Detection**<br/>Non-legal documents or irrelevant text mistakenly trigger high-confidence legal clause warnings. | Medium (2) | Medium (2) | **4 (Medium)** | Multi-term syntactic clustering requires multiple corroborating legal terms before declaring a clause `Found`. | Display confidence scores and source text snippets in the UI so legal professionals can verify context. | **Mitigated** |
| **R-06** | **False-Negative Information Extraction**<br/>Unusual contract drafting syntax omits critical indemnities or payment terms. | Medium (2) | High (3) | **6 (High)** | Expanded synonym dictionaries, multi-modal verb regex patterns (`shall`, `must`, `agrees to`), and section-aware scanning. | Prominent legal disclaimer on all screens stating LexExtract is an assistive tool and not a substitute for legal review. | **Mitigated** |
| **R-07** | **Database Failure or Data Corruption**<br/>SQLite file corruption, connection pooling locks, or concurrent write deadlocks. | Low (1) | High (3) | **3 (Low)** | SQLAlchemy ORM abstractions, static connection pooling (`check_same_thread=False`), transactional session rollbacks on error. | Automated database backup routines; seamless configuration switch to enterprise PostgreSQL via `DATABASE_URL`. | **Mitigated** |
| **R-08** | **Frontend / Backend Integration Failure**<br/>API schema drift, CORS configuration blocks, or serialization mismatches breaking UI components. | Low (1) | High (3) | **3 (Low)** | Strict Pydantic schemas validating all request/response models; centralized `api.js` client with error interceptors; CORS headers. | Automated Vite build validation (`npm run build`) and integration test suites validating end-to-end payload formats. | **Mitigated** |
| **R-09** | **Incomplete Test Coverage**<br/>Undetected bugs slip into production due to lack of edge-case and negative tests. | Low (1) | High (3) | **3 (Low)** | Comprehensive Pytest suite covering unit, integration, edge cases, RBAC, and NLP pipelines (119 automated tests passing). | Continuous regression testing during build pipeline; strict quality gate requiring 100% test pass before release. | **Mitigated** |
| **R-10** | **Incorrect Comparison Results**<br/>Document comparison module yields inaccurate cosine similarity or missed clause differences. | Low (1) | Medium (2) | **2 (Low)** | Deterministic TF-IDF vectorization with unit-norm cosine calculation; exact syntactic clause diffing with UNCHANGED/MODIFIED/ADDED flags. | Provide full side-by-side snippet comparisons and shared keyword breakdowns allowing direct human validation. | **Mitigated** |

---

## Risk Review & Monitoring Cadence

1. **Risk Ownership:** Assigned to Technical Lead & QA Engineer.
2. **Review Trigger:** Re-assessed at each project phase milestone.
3. **Escalation Path:** Any risk transitioning to a score $\ge 6$ mandates architectural review and immediate regression testing before deployment.
