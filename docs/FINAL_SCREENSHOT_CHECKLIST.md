# LexExtract — Final Report Screenshot Checklist

**Project Title:** LexExtract — Legal Document Keyword & Entity Extractor  
**Purpose:** Comprehensive guide for capturing and cataloging all screenshots required for the Final Project Report, Synopsis, and Presentation Slides.  

---

## 1. Required System Screenshots (Items 1 to 20)

| Item # | Screenshot Title | Recommended Route / Screen | Key Visual Elements to Capture | Report Section |
| :---: | :--- | :--- | :--- | :--- |
| **01** | **User Authentication & Login** | `/login` | Dual authentication fields, preset credential buttons, legal-tech branding, HTTPS indicator. | Section 4: Security Tier |
| **02** | **Executive Dashboard** | `/` (`/dashboard`) | Metric cards (Cataloged Briefs, Words, Analyses, Entities), recent documents table, legal disclaimer. | Section 3: System Overview |
| **03** | **Document Upload & Ingestion** | `/new_analysis` | Drag-and-drop zone, supported file formats (PDF, DOCX, TXT), 25 MB ceiling indicator, upload button. | Section 5: Document Ingestion |
| **04** | **Analysis Execution State** | `/new_analysis` / `/results` | Processing spinner / status indicator showing active NLP pipeline execution. | Section 5: Execution Pipeline |
| **05** | **Document Overview (At-a-Glance)** | `/results` (Overview tab) | Document type badge, identified parties, key dates, attention areas / governance checks card. | Section 6: Legal Intelligence |
| **06** | **Keyword Extraction Explorer** | `/results` (Keywords tab) | Ranked keyword table with TF-IDF, RAKE, and Final Score columns, category filter dropdown. | Section 7: Keyword Extraction |
| **07** | **Entity Extraction Explorer** | `/results` (Entities tab) | Grid of typed entity cards with confidence badges, type filter dropdown (Courts, Statutes, Parties). | Section 8: Legal NER |
| **08** | **Important Clauses Finder** | `/results` (Clauses tab) | 13 controlled clause categories, Found/Not Found status badges, confidence ratings, source snippets. | Section 6: Clause Classification |
| **09** | **Obligations & Duties Breakdown** | `/results` (Obligations tab) | Party attribution, obligation description, prohibition badges, deadlines, source sentences. | Section 6: Obligation Extraction |
| **10** | **Structured Facts (Dates & Money)**| `/results` (Facts tab) | Subtabs for Dates, Monetary Sums (multi-currency INR, USD, EUR, GBP), and Durations with Locate buttons. | Section 6: Structured Facts |
| **11** | **In-Document Semantic Search** | `/results` (Search tab) | Search query bar, match counts, relevance scores, and contextual snippet cards with "Open in Viewer". | Section 9: Information Retrieval |
| **12** | **Interactive Document Viewer** | `/viewer` | Multi-layer visual text stream, color-coded keyword/entity token highlights, layer toggles, entity drawer. | Section 10: Presentation Tier |
| **13** | **Two-Document Comparison** | `/compare` | Side-by-side contract selector, cosine similarity score (%), word delta, clause alignment table (`UNCHANGED`, `MODIFIED`). | Section 9: Document Comparison |
| **14** | **Executive Report Export (PDF/JSON)**| Export dropdown / PDF viewer | Generated multi-page PyMuPDF vector PDF showing professional layout, tables, and mandatory disclaimer. | Section 11: Export Module |
| **15** | **Repository History Archive** | `/history` | Tabular archive of all uploaded briefs, file formats, page counts, word counts, and cascading delete buttons. | Section 4: Repository Management |
| **16** | **Governance Audit Ledger (Admin)** | `/admin_audit` | Paginated immutable audit trail showing action types, user IDs, IP addresses, statuses, and UTC timestamps. | Section 4: Institutional Governance |
| **17** | **Three-Tier Architecture Diagram** | `docs/ARCHITECTURE_FOR_VIVA.md` | Flowchart showing Presentation Tier, FastAPI Application Tier, and SQLAlchemy Data Tier interactions. | Section 2: Architecture Design |
| **18** | **ASTMA Evaluation Benchmark** | `/benchmark` (`/evaluation`) | Empirical evaluation console showing Micro/Macro P/R/F1 scorecards, ablation comparison, and latency meters. | Section 12: ASTMA Evaluation |
| **19** | **Automated Test Suite Execution** | Terminal (`python -m pytest`)| Console output showing 119/119 passing tests with 100% pass rate in green. | Section 13: Software Testing |
| **20** | **Project Management Artifacts** | `docs/WBS.md` / `RISK_REGISTER.md` | Work Breakdown Structure hierarchical chart and 10-point PMBOK Risk Register table. | Section 14: ITPM Methodology |

---

## 2. Best Practices for Screenshot Capture

1. **Resolution & Scaling:** Capture at standard 1080p desktop resolution ($1920 \times 1080$) with 100% browser zoom for crisp typography.
2. **Realistic Data:** Use active project demonstration documents (`sample_contract.pdf` or `sample_arbitration_agreement.txt`) rather than empty placeholder screens.
3. **No PII or Secrets:** Ensure no sensitive operating system notifications or personal credentials are included in the capture frame.
4. **Naming Convention:** Save image files systematically as `fig_01_login.png`, `fig_02_dashboard.png`, ..., `fig_20_risk_register.png` in the project documentation directory.
