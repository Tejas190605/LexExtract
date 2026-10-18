# LexExtract — Document Comparison Acceptance Test Protocol

**Document Version:** 1.0.0 (Release Acceptance Testing)  
**Test Focus:** Side-by-Side Comparative Diffing & Cosine Similarity  
**Documents Tested:** `03_Service_Agreement_V1.docx` vs. `04_Service_Agreement_V2.docx`  
**Date:** October 2026  

---

## 1. Overview & Objective

This protocol evaluates the LexExtract Document Comparison engine (`/compare`). It tests the ability of the system to take two versions of a commercial agreement, compute their Vector Space Model cosine similarity, analyze the vocabulary/token delta, and align corresponding clauses side-by-side to highlight negotiated revisions.

---

## 2. Test Setup & Ingestion

1. Log into LexExtract as an authenticated user.
2. In **New Analysis**, upload and analyze:
   - File A: `sample_documents/03_Service_Agreement_V1.docx`
   - File B: `sample_documents/04_Service_Agreement_V2.docx`
3. Verify both documents appear in **Repository History** with status `PROCESSED`.
4. Click **"Document Comparison"** in the top navigation bar.

---

## 3. Comparison Test Execution Steps

### Step 1: Select Comparison Targets
- **Action:**
  - Select **Document A (Base Version):** `03_Service_Agreement_V1.docx`
  - Select **Document B (Revised Version):** `04_Service_Agreement_V2.docx`
  - Click **"Compare Documents"**.
- **Expected Result:**
  - Comparison executes in under 100 ms.
  - The comparison view displays:
    1. Overall Cosine Similarity gauge/percentage.
    2. Document Metrics & Vocabulary Delta card.
    3. Side-by-Side Aligned Clauses table.
- **Pass/Fail:** `[ ]`
- **Observation:**

---

### Step 2: Verify Cosine Similarity Score
- **Action:** Observe the Cosine Similarity percentage.
- **Expected Result:**
  - Similarity score is high (~80%–95%), reflecting that both documents share substantial foundational legal vocabulary (parties, boilerplate, jurisdiction) while differing in specific commercial terms.
- **Pass/Fail:** `[ ]`
- **Observation:**

---

### Step 3: Verify Vocabulary & Token Delta
- **Action:** Inspect the Vocabulary & Metadata comparison card.
- **Expected Result:**
  - Displays word count comparison between V1 and V2.
  - Lists Shared Legal Keywords common to both documents.
  - Lists Unique Keywords appearing exclusively in V1 or V2 (e.g., terms related to *automatic renewal*, *cure*, *remedy*).
- **Pass/Fail:** `[ ]`
- **Observation:**

---

### Step 4: Verification of Specific Negotiated Revisions

Inspect the Side-by-Side Clause Alignment and diff highlights for the 6 known contractual variations:

| Contractual Dimension | Base Version (V1) Expectation | Revised Version (V2) Expectation | Verified in Comparison? | Pass / Fail |
| :--- | :--- | :--- | :---: | :---: |
| **1. Service Fee** | `INR 120,000 per month` | `INR 145,000 per month` (Increased fee) | Aligned under Service Fees / Billing clause | `[ ]` |
| **2. Payment Period** | `thirty (30) days` | `fifteen (15) days` (Accelerated payment) | Aligned under Payment Period clause | `[ ]` |
| **3. Contract Term & Renewal** | Initial term 1 year; `no automatic renewal` | Initial term 1 year; `automatic six (6) month renewal` | Aligned under Term / Renewal clause | `[ ]` |
| **4. Termination Notice** | `thirty (30) days` advance notice | `sixty (60) days` advance notice | Aligned under Termination Notice clause | `[ ]` |
| **5. Default & Termination Condition** | Immediate termination on any breach | Added `material breach cure mechanism` with `thirty (30) days` notice to cure | Aligned under Default / Breach clause | `[ ]` |
| **6. Limitation of Liability Cap** | Capped at `INR 500,000` | Capped at `INR 750,000` (Increased liability ceiling) | Aligned under Limitation of Liability clause | `[ ]` |

---

### Step 5: Edge Case — Identical Document Comparison
- **Action:** Select `03_Service_Agreement_V1.docx` for both Document A and Document B, then click **"Compare Documents"**.
- **Expected Result:**
  - System handles identical comparison gracefully.
  - Cosine Similarity displays `100.0%`.
  - Word count delta displays `0 words`.
  - Zero differences flagged.
- **Pass/Fail:** `[ ]`
- **Observation:**

---

### Step 6: Edge Case — Unrelated Document Comparison
- **Action:** Compare `01_Employment_Agreement.docx` against `03_Service_Agreement_V1.docx`.
- **Expected Result:**
  - Comparison displays substantially lower similarity score (< 60%).
  - Vocabulary delta reflects distinct contract types.
  - Aligned clauses correctly match only shared standard provisions (e.g., Governing Law, Dispute Resolution) while marking specialized clauses as unaligned.
- **Pass/Fail:** `[ ]`
- **Observation:**

---

## 4. Comparison Sign-Off

- **Tester Name:** ___________________________  
- **Test Date:** _____________________________  
- **Overall Result:** `[ ] PASS` / `[ ] FAIL`  
- **Comments:**  
  _________________________________________________________________________
