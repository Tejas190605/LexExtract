# LexExtract — Sample Document Expected Results & Ground Truth Benchmark

**Document Version:** 1.0.0 (Release Testing)  
**Purpose:** Ground Truth Reference for Manual Acceptance Testing  
**Date:** October 2026  

---

## 1. Testing Philosophy & Evaluation Guidelines

When performing manual acceptance testing, legal document extractions should be evaluated against expected semantic categories rather than demanding rigid rank positions.

If an extraction varies from this reference:
1. **DO NOT change the algorithm immediately.**
2. Record the variance using the structured audit format:
   - **EXPECTED:** The expected entity, clause, or obligation.
   - **ACTUAL:** What LexExtract extracted.
   - **SOURCE TEXT:** The relevant sentence or clause from the document.
   - **REASON FOR DIFFERENCE:** Linguistic nuance, boundary splitting, or token variation.

---

## 2. Document 1: `01_Employment_Agreement.docx`

### Overview & Parties
- **Document Type:** Employment Agreement / Service Contract
- **Employer / Company:** `Meridian Technologies Pvt. Ltd.` (ORG)
- **Employee:** `Priya Sharma` (PERSON)
- **Designation:** Senior Software Architect
- **Governing Law / Jurisdiction:** Substantive laws of India; Civil Courts at Bengaluru, Karnataka

### Financial Terms & Dates
- **Salary / Compensation:** `INR 65,000` per month (Gross monthly salary)
- **Effective Commencement Date:** `1 April 2026`
- **Contract Expiry Date:** `31 March 2027`
- **Termination Notice Period:** `thirty (30) days` prior written notice (or salary in lieu)

### Detectable Clauses
- **Clause 1 (Appointment & Term):** Engagement duration from 1 April 2026 to 31 March 2027.
- **Clause 2 (Compensation):** Monthly payment and statutory tax deductions.
- **Clause 4 (Confidentiality & Non-Disclosure):** Nondisclosure of trade secrets, source code, and customer records; survival post-termination.
- **Clause 5 (Intellectual Property Rights):** Full assignment of all inventions and code to Meridian Technologies Pvt. Ltd.
- **Clause 6 (Termination):** 30 days notice requirement; immediate termination for gross misconduct.
- **Clause 7 (Dispute Resolution):** Binding arbitration under the Arbitration and Conciliation Act, 1996 before a sole arbitrator.
- **Clause 8 (Governing Law):** Substantive laws of India; exclusive jurisdiction in Bengaluru.

### Contractual Obligations
- **Affirmative Duties (Employer):** The Company shall pay the Employee monthly gross salary of INR 65,000.
- **Affirmative Duties (Employee):** The Employee shall perform all duties faithfully and diligently; Employee shall keep all Confidential Information strictly confidential.
- **Prohibitions (Employee):** The Employee shall not engage in conflicting commercial activities; Employee shall not disclose, copy, or distribute proprietary data.

---

## 3. Document 2: `02_Confidentiality_NDA.docx`

### Overview & Parties
- **Document Type:** Mutual Non-Disclosure Agreement (NDA)
- **Disclosing Party:** `Nova Labs Pvt. Ltd.` (ORG)
- **Receiving Party:** `Orbit Systems LLP` (ORG)
- **Execution Date:** `15th day of May, 2026`
- **Governing Law / Jurisdiction:** Laws of India; exclusive jurisdiction in Bengaluru, Karnataka

### Core Legal Terms & Durations
- **Term of Confidentiality:** `three (3) years` from effective date
- **Return / Destruction Deadline:** `ten (10) days` upon written demand to return or certify destruction of confidential materials
- **Injunctive Relief:** Explicit recognition that monetary damages are inadequate, entitling the disclosing party to immediate equitable relief

### Search Verification Ground Truth
- Search query: `proprietary` $\rightarrow$ Returns matches in Clause 1 (Definition of Confidential Information) and Clause 2 (Non-Disclosure and Non-Use Obligations).

---

## 4. Document 3 & 4: Service Agreement Comparison (V1 vs. V2)

When comparing `03_Service_Agreement_V1.docx` and `04_Service_Agreement_V2.docx`, the comparison screen should highlight the following 6 negotiated changes:

| Contract Dimension | Version 1.0 (`03_Service_Agreement_V1.docx`) | Version 2.0 (`04_Service_Agreement_V2.docx`) | Nature of Revision |
| :--- | :--- | :--- | :--- |
| **1. Service Fee** | `INR 120,000 per month` | `INR 145,000 per month` | **Modified Value:** +INR 25,000/month fee increase |
| **2. Payment Period** | `thirty (30) days` | `fifteen (15) days` | **Modified Term:** Payment terms accelerated by 15 days |
| **3. Contract Renewal** | Initial term 1 year; `no automatic renewal` | Initial term 1 year; `automatic six (6) month renewal` | **Added Provision:** Introduction of auto-renewal mechanism |
| **4. Termination Notice** | `thirty (30) days` advance notice | `sixty (60) days` advance notice | **Modified Term:** Notice window doubled to 60 days |
| **5. Breach / Cure Condition** | Immediate termination on any breach | Added `material breach cure mechanism` with `thirty (30) days` to cure | **Added Provision:** Notice-and-cure procedure added |
| **6. Liability Cap** | Capped at `INR 500,000` | Capped at `INR 750,000` | **Modified Value:** Liability ceiling increased by INR 250,000 |

### Expected Similarity Score:
- **Cosine Vector Similarity:** Expected in the range **82% – 94%**.
- High similarity is expected because the parties, service scope, boilerplate, and governing law remain unchanged.

---

## 5. Variance Recording Template

If any variance is observed during testing, copy this format into your test notes:

```markdown
### Variance Report: [Document Name] - [Feature]
- **Tested Item:** (e.g., Salary Amount / Termination Clause)
- **EXPECTED:** INR 65,000 monthly salary
- **ACTUAL:** INR 65,000 extracted under Facts tab with confidence 1.0
- **SOURCE TEXT:** "The Company shall pay the Employee a monthly gross salary of INR 65,000..."
- **REASON FOR DIFFERENCE:** (None / Exact Match)
```
