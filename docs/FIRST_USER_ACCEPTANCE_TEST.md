# LexExtract — First-User Acceptance Test Protocol

**Document Version:** 1.0.0 (Release Acceptance Testing)  
**Target Environment:** Clean Local Deployment (`http://localhost:5173`)  
**Audience:** Manual QA Tester / First-Time User  
**Date:** October 2026  

---

## 1. Introduction & Test Philosophy

This protocol guides a tester who has **never used LexExtract before**. Starting from a freshly initialized test environment containing zero user data, you will perform the complete journey of a new user: registration, authentication, document intake, multi-faceted NLP review, in-document search, interactive source navigation, document history management, and executive report export.

---

## 2. Test Prerequisites & Environment Verification

Before beginning:
1. Verify the database is freshly reset:
   ```bash
   python backend/scripts/reset_dev_environment.py
   ```
2. Start the FastAPI backend:
   ```bash
   cd backend
   .\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
   ```
3. Start the React frontend:
   ```bash
   cd frontend
   npm run dev
   ```
4. Open your browser in an **Incognito / Private Window** to `http://127.0.0.1:5173`.

---

## 3. Step-by-Step Test Procedure: Employment Agreement

### Phase A: Initial Application Load
- **Step A.1:**
  - **Action:** Open `http://127.0.0.1:5173` in your browser.
  - **Expected Result:** Application redirects to `/login`. The institutional legal-tech aesthetic (deep navy, parchment tones, crisp typography) loads cleanly. "Sign In" form with fields for Username and Password is displayed. Footer shows the institutional legal disclaimer.
  - **Pass/Fail:** `[ ]`
  - **Observation:**

---

### Phase B: First-Time User Registration
- **Step B.1:**
  - **Action:** Click the **"Create an Account"** link below the sign-in form.
  - **Expected Result:** URL navigates to `/register`. Registration form appears with fields: Full Name, Email, Username, Password, Confirm Password.
  - **Pass/Fail:** `[ ]`
  - **Observation:**

- **Step B.2 (Invalid Input Validation):**
  - **Action:** Leave fields empty and click **"Create Account"**.
  - **Expected Result:** Form prevents submission; fields highlight or error banner informs that required fields are missing.
  - **Pass/Fail:** `[ ]`
  - **Observation:**

- **Step B.3 (Successful Registration):**
  - **Action:** Fill in the registration form:
    - Full Name: `Adv. Rohan Verma`
    - Email: `rohan.verma@lawfirm.local`
    - Username: `rohan_verma`
    - Password: `Lawyer@Lex2026!`
    - Confirm Password: `Lawyer@Lex2026!`
    Click **"Create Account"**.
  - **Expected Result:** Success notification or automatic redirection to `/login` with username pre-filled or ready for authentication.
  - **Pass/Fail:** `[ ]`
  - **Observation:**

---

### Phase C: Login Authentication
- **Step C.1 (Invalid Credentials Test):**
  - **Action:** Enter Username: `rohan_verma`, Password: `WrongPassword123!` and click **"Sign In"**.
  - **Expected Result:** Error message displayed: *"Invalid username or password"*. No stack trace or 500 error.
  - **Pass/Fail:** `[ ]`
  - **Observation:**

- **Step C.2 (Valid Login):**
  - **Action:** Enter Username: `rohan_verma`, Password: `Lawyer@Lex2026!`, and click **"Sign In"**.
  - **Expected Result:** Login succeeds. URL navigates to `/dashboard`. Navigation bar displays user's name (`Adv. Rohan Verma`), role badge (`USER`), and links: *Dashboard, New Analysis, Document Viewer, Document Comparison, Repository History*.
  - **Pass/Fail:** `[ ]`
  - **Observation:**

---

### Phase D: Clean First-Time Dashboard State
- **Step D.1:**
  - **Action:** Inspect the Dashboard screen.
  - **Expected Result:**
    - Metric cards display zero state: Total Documents: `0`, Processed Analyses: `0`, Entities Extracted: `0`, Keywords Mined: `0`.
    - Recent Documents table displays empty state: *"No documents in repository. Upload your first document to begin."*
    - Legal disclaimer is displayed.
  - **Pass/Fail:** `[ ]`
  - **Observation:**

---

### Phase E: Document Intake & Upload
- **Step E.1:**
  - **Action:** Click **"New Analysis"** in the top navigation.
  - **Expected Result:** Navigates to `/new-analysis`. File intake dropzone appears with file format badge (`PDF`, `DOCX`, `TXT`) and 25 MB size limit notice.
  - **Pass/Fail:** `[ ]`
  - **Observation:**

- **Step E.2:**
  - **Action:** Select or drag-and-drop `sample_documents/01_Employment_Agreement.docx` from the workspace.
  - **Expected Result:** Dropzone detects file, showing filename `01_Employment_Agreement.docx`, file type `docx`, and approximate file size (~36 KB). "Run Legal Analysis" button becomes active.
  - **Pass/Fail:** `[ ]`
  - **Observation:**

---

### Phase F: Automated Pipeline Execution
- **Step F.1:**
  - **Action:** Click **"Run Legal Analysis"**.
  - **Expected Result:** Processing spinner appears with status updates (*Extracting text $\rightarrow$ Computing TF-IDF & RAKE $\rightarrow$ Extracting Entities & Clauses*). Execution finishes in sub-second time (< 500 ms) and automatically redirects to the **Analysis Results** view (`/analysis/:id`).
  - **Pass/Fail:** `[ ]`
  - **Observation:**

---

### Phase G: Document Overview Tab
- **Step G.1:**
  - **Action:** Review the **"Overview"** tab of the analysis results.
  - **Expected Result:**
    - Document title: `01_Employment_Agreement.docx`.
    - Performance badge: Pipeline execution time (~200–350 ms).
    - Identified Parties: `Meridian Technologies Pvt. Ltd.` and `Priya Sharma`.
    - Identified Dates: `1 April 2026`, `31 March 2027`.
    - Identified Monetary Totals: `INR 65,000`.
    - Attention Areas: Identified high-priority clauses (Confidentiality, Termination, Governing Law).
  - **Pass/Fail:** `[ ]`
  - **Observation:**

---

### Phase H: Keywords Tab
- **Step H.1:**
  - **Action:** Click the **"Keywords"** tab.
  - **Expected Result:**
    - Ranked list of multi-word and single-word legal keywords.
    - Expected terms present: `employment agreement`, `confidential information`, `intellectual property`, `arbitration`, `termination`, `salary`.
    - Each keyword card displays rank, composite score, frequency, and category tag.
    - Category filter pills (*All, General, Procedural, Substantive, Corporate*) allow instant filtering.
  - **Pass/Fail:** `[ ]`
  - **Observation:**

---

### Phase I: Entities Tab
- **Step I.1:**
  - **Action:** Click the **"Entities"** tab.
  - **Expected Result:**
    - Entities grouped or tagged by category:
      - `ORG` / Company: `Meridian Technologies Pvt. Ltd.`
      - `PERSON` / Employee: `Priya Sharma`
      - `ACT` / Statute: `Companies Act 2013`, `Arbitration and Conciliation Act 1996`, `Income Tax Act 1961`
      - `MONEY`: `INR 65,000`
      - `GPE` / Location: `Bengaluru`, `Karnataka`, `India`
    - Source badge indicates extraction source (`rule` or `spacy`).
  - **Pass/Fail:** `[ ]`
  - **Observation:**

---

### Phase J: Important Clauses Tab
- **Step J.1:**
  - **Action:** Click the **"Important Clauses"** tab.
  - **Expected Result:**
    - Cards for detected clauses across categories:
      - **Confidentiality:** Clause 4 excerpt with high confidence score.
      - **Intellectual Property:** Clause 5 excerpt regarding invention assignment.
      - **Termination:** Clause 6 excerpt regarding 30 days notice.
      - **Dispute Resolution / Arbitration:** Clause 7 excerpt referencing Arbitration Act 1996.
      - **Governing Law / Jurisdiction:** Clause 8 excerpt referencing laws of India and courts at Bengaluru.
    - Each card displays confidence score, category badge, and a **"Jump to Viewer"** button.
  - **Pass/Fail:** `[ ]`
  - **Observation:**

---

### Phase K: Obligations & Responsibilities Tab
- **Step K.1:**
  - **Action:** Click the **"Obligations"** tab.
  - **Expected Result:**
    - **Affirmative Duties (shall/must):**
      - Company shall pay monthly gross salary of INR 65,000.
      - Employee shall perform all duties faithfully and diligently.
      - Employee shall keep all Confidential Information strictly confidential.
    - **Prohibitions (shall not):**
      - Employee shall not engage in conflicting commercial activities.
      - Employee shall not disclose, copy, or distribute proprietary data.
    - Party attribution correctly links duties to Employer or Employee.
  - **Pass/Fail:** `[ ]`
  - **Observation:**

---

### Phase L & M: Dates, Money & Deadlines Tab
- **Step L.1:**
  - **Action:** Click the **"Dates & Money"** tab.
  - **Expected Result:**
    - **Dates:** `1 April 2026` (Commencement), `31 March 2027` (Expiry).
    - **Monetary Values:** `INR 65,000` (Monthly Gross Salary).
    - **Contractual Deadlines:** `thirty (30) days` (Termination Notice Period).
  - **Pass/Fail:** `[ ]`
  - **Observation:**

---

### Phase N & O: In-Document Search & Source Viewer
- **Step N.1:**
  - **Action:** Click the **"Search"** tab. Type `confidential` into the search box and press Enter.
  - **Expected Result:** Match count is displayed (> 0 matches). Relevant passages are listed with passage relevance score and highlighted occurrences.
  - **Pass/Fail:** `[ ]`
  - **Observation:**

- **Step O.1:**
  - **Action:** Click **"Jump to Viewer"** on one of the search result passages or clause cards.
  - **Expected Result:** Navigates directly to the **Document Viewer** (`/viewer`). The document text renders with the target snippet automatically scrolled into view and highlighted.
  - **Pass/Fail:** `[ ]`
  - **Observation:**

- **Step O.2:**
  - **Action:** In Document Viewer, test the **Layer Toggle** options (*Keywords Only, Clean Plain Text, Original Stream*).
  - **Expected Result:**
    - *Keywords Only*: Amber highlighting on extracted legal terms.
    - *Clean Plain Text*: Highlights toggle off; clean readable text.
    - *Original Stream*: Line breaks and spacing match raw extracted stream.
  - **Pass/Fail:** `[ ]`
  - **Observation:**

---

### Phase P: Repository History
- **Step P.1:**
  - **Action:** Click **"Repository History"** in the navigation.
  - **Expected Result:** History table lists `01_Employment_Agreement.docx` with status `PROCESSED`, correct upload timestamp, word count, and file size.
  - **Pass/Fail:** `[ ]`
  - **Observation:**

- **Step P.2:**
  - **Action:** Click the document title or "View Analysis" action.
  - **Expected Result:** Instantly opens the cached analysis results without re-uploading or re-processing.
  - **Pass/Fail:** `[ ]`
  - **Observation:**

---

### Phase Q: Report Export
- **Step Q.1:**
  - **Action:** On the Analysis Results page, click **"Export PDF"**.
  - **Expected Result:** Browser downloads a multi-page vector PDF report named `LexExtract_Analysis_Report_*.pdf`.
  - **Pass/Fail:** `[ ]`
  - **Observation:**

- **Step Q.2:**
  - **Action:** Open the downloaded PDF in your viewer.
  - **Expected Result:** PDF contains:
    - Institutional header with document metadata.
    - Executive Overview and Attention Areas.
    - Important Clauses table with confidence scores.
    - Obligations & Duties breakdown.
    - Top Keywords and Entities tables.
    - Prominent legal non-advice disclaimer in footer.
  - **Pass/Fail:** `[ ]`
  - **Observation:**

- **Step Q.3:**
  - **Action:** Click **"Export JSON"**.
  - **Expected Result:** Browser downloads structured `.json` payload containing the complete extraction schema.
  - **Pass/Fail:** `[ ]`
  - **Observation:**

---

### Phase R: Logout & Session Invalidation
- **Step R.1:**
  - **Action:** Click the user profile / **"Logout"** button in the header.
  - **Expected Result:** Session is cleared. User is redirected to `/login`.
  - **Pass/Fail:** `[ ]`
  - **Observation:**

- **Step R.2 (Browser Back Button Invalidation):**
  - **Action:** Click the browser's **Back** button.
  - **Expected Result:** Protected pages (`/dashboard`, `/analysis/:id`, `/viewer`) do not open. The application immediately redirects back to `/login`.
  - **Pass/Fail:** `[ ]`
  - **Observation:**

---

## 4. Second Test: Non-Disclosure Agreement (NDA)

Repeat the upload and analysis workflow with `sample_documents/02_Confidentiality_NDA.docx`:

| Verification Item | Expected Content | Actual Result | Pass / Fail |
| :--- | :--- | :--- | :---: |
| **Parties Identified** | `Nova Labs Pvt. Ltd.` (Disclosing Party), `Orbit Systems LLP` (Receiving Party) | | `[ ]` |
| **Confidentiality Clause** | Clause 1 & Clause 2 definitions and restrictions detected | | `[ ]` |
| **Duration of Confidentiality** | `three (3) years` (Duration / Term) | | `[ ]` |
| **Return / Destruction Obligation** | `ten (10) days` obligation to return or certify destruction | | `[ ]` |
| **Execution Date** | `15th day of May, 2026` | | `[ ]` |
| **Governing Law / Jurisdiction** | Laws of India, exclusive jurisdiction of courts at Bengaluru | | `[ ]` |
| **Search Query Test** | Query `proprietary` returns matches in Clauses 1 and 2 | | `[ ]` |

---

## 5. Acceptance Test Sign-Off

- **Tester Name:** ___________________________  
- **Test Date:** _____________________________  
- **Overall Result:** `[ ] PASS` / `[ ] FAIL`  
- **Tester Signature / Comments:**  
  _________________________________________________________________________
