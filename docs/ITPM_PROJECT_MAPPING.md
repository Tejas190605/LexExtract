# LexExtract — IT Project Management (ITPM) Academic Syllabus Mapping

**Subject:** IT Project Management (ITPM)  
**Curriculum Domain:** Software Project Management, Quality Assurance, Risk Management & Verification  
**Implementation System:** LexExtract Legal Document Analysis Engine

---

## 1. Executive Curriculum Alignment

This document details the mapping between the academic syllabus of **IT Project Management (ITPM)** and the project governance, planning, testing, and risk management practices implemented across the LexExtract lifecycle.

---

## 2. Topic-by-Topic Syllabus Mapping

### 2.1 Work Breakdown Structure (WBS) & Phased Development
- **Syllabus Concept:** Hierarchical decomposition of total project scope into manageable, sequential deliverables.
- **Where It Appears:** Complete project history; [`LEXEXTRACT_BLUEPRINT.md`](file:///c:/Users/tejas/PBL%20project%20(ES,ASTMA,ITPM)/LEXEXTRACT_BLUEPRINT.md).
- **Academic Implementation Details:**
  LexExtract was delivered across nine iterative, structured phases:
  - **Phase 1:** Core Blueprint & Three-Tier Scaffolding
  - **Phase 2:** Database Design & Repository Implementation
  - **Phase 3:** Document Ingestion & Citation-Preserving Text Processing
  - **Phase 4:** Tri-Model Keyword Extraction Pipeline
  - **Phase 5:** Legal Named Entity Recognition Engine
  - **Phase 6:** Authentication, RBAC, Data Isolation & Audit Ledger
  - **Phase 7:** Legal-Tech UI, Interactive Viewer & Results Explorer
  - **Phase 8:** ASTMA Empirical Evaluation Benchmark & Ablation Study
  - **Phase 9:** Final Integration, Deployment Preparation & Full QA
  Each phase concluded with formal acceptance criteria before subsequent phases began.

---

### 2.2 Requirements Traceability Management (RTM)
- **Syllabus Concept:** Bidirectional traceability linking business requirements to architectural components, code modules, and test verification.
- **Where It Appears:** [`docs/REQUIREMENTS_TRACEABILITY.md`](file:///c:/Users/tejas/PBL%20project%20(ES,ASTMA,ITPM)/docs/REQUIREMENTS_TRACEABILITY.md).
- **Academic Implementation Details:**
  Maintains a formal matrix mapping 12 functional requirements (`FR-01` through `FR-12`) and 5 non-functional requirements (`NFR-01` through `NFR-05`) directly to source code files, database models, and automated tests. This ensures no orphaned requirements and 100% verification coverage.

---

### 2.3 Project Risk Management & Mitigation Strategies
- **Syllabus Concept:** Risk identification, qualitative impact assessment, probability scoring, and risk mitigation registers.
- **Where It Appears:** [`docs/RISK_REGISTER.md`](file:///c:/Users/tejas/PBL%20project%20(ES,ASTMA,ITPM)/docs/RISK_REGISTER.md).
- **Academic Implementation Details:**
  Tracks 10 project and technical risks with documented likelihoods, impacts, and mitigations:
  - `RSK-01` (Empty text on scanned PDFs): Mitigated by pre-extraction length validation returning HTTP 400 errors.
  - `RSK-03` (Zero-division in evaluation): Mitigated by explicit denominator guards returning `0.0`.
  - `RSK-04` (Horizontal privilege escalation): Mitigated by `check_document_access` dependency checks returning HTTP 403 Forbidden.
  - `RSK-05` (Accidental admin lockout): Mitigated by minimum active administrator count safeguards.

---

### 2.4 Software Quality Assurance (SQA) & Multi-Tier Testing
- **Syllabus Concept:** Verification and validation (V&V), regression testing, test automation, and code coverage.
- **Where It Appears:** `backend/tests/`, [`docs/FINAL_TEST_RESULTS.md`](file:///c:/Users/tejas/PBL%20project%20(ES,ASTMA,ITPM)/docs/FINAL_TEST_RESULTS.md).
- **Academic Implementation Details:**
  Implements a tiered testing hierarchy:
  - **Unit Testing:** Validates mathematical formulas, normalization rules, and candidate generation.
  - **Integration Testing:** Tests database cascades, session closures, and multi-service workflows.
  - **API Contract Testing:** Verifies HTTP response codes, headers, and Pydantic schemas.
  - **Security Regression Testing:** Confirms RBAC and cross-user isolation boundaries.
  - **Regression Baseline:** Maintained 100% pass rate across 98 automated backend tests.

---

### 2.5 Verification & Acceptance Testing (V&V)
- **Syllabus Concept:** Acceptance testing against predefined functional criteria, user workflow validation, and automated browser simulation.
- **Where It Appears:** `backend/verify_phase9_qa.py`, browser automation recordings.
- **Academic Implementation Details:**
  End-to-end user journeys were verified using automated browser agents that simulated practitioner and administrator actions across 15 discrete workflow steps (from login and document upload to viewer inspection, benchmark execution, and audit log review).

---

### 2.6 Configuration & Change Management
- **Syllabus Concept:** Baseline configuration, environment isolation, version control policies, and secret protection.
- **Where It Appears:** `.gitignore`, `backend/.env.example`, `frontend/.env.example`.
- **Academic Implementation Details:**
  Enforces clean separation between environment configuration and source code. Secret keys and credentials are abstracted into `.env` files and excluded from version control via `.gitignore`. Template `.env.example` files document all required configuration keys without exposing sensitive values.
