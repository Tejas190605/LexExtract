# LexExtract — User Guide

**Application Version:** 1.0.0  
**Project:** LexExtract — Legal Document Keyword & Entity Extractor  
**Date:** October 2026  

---

## 1. Introduction

LexExtract is an offline-capable, explainable legal document intelligence system. It helps attorneys, paralegals, and legal analysts rapidly extract, categorize, and cross-reference crucial legal concepts from contracts, notices, and agreements without relying on cloud AI APIs.

---

## 2. Starting the Application

To run LexExtract locally:

1. **Start the FastAPI Backend:**
   ```bash
   cd backend
   .\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
   ```
   The backend API runs at `http://127.0.0.1:8000` (API documentation at `http://127.0.0.1:8000/docs`).

2. **Start the Frontend Application:**
   ```bash
   cd frontend
   npm run dev
   ```
   Open your browser to `http://127.0.0.1:5173`.

---

## 3. Account Login & Registration

### 3.1 Pre-Configured Demo Accounts
You can log in immediately using the seeded demonstration accounts:

- **Administrator:**
  - Username: `admin`
  - Password: `Admin@Lex2026!`
  - Role: Full platform and governance audit access.

- **Senior Legal Analyst:**
  - Username: `analyst`
  - Password: `Analyst@Lex2026!`
  - Role: Standard analysis, comparison, and export access.

- **Practicing Lawyer:**
  - Username: `lawyer_user`
  - Password: `User@Lex2026!`
  - Role: Standard user account.

### 3.2 Registering a New Account
Click **"Create an Account"** on the login screen, enter your Full Name, Email, Username, and Password, and sign in.

---

## 4. Ingesting & Analyzing a Document

1. In the sidebar navigation, click **"New Analysis"**.
2. **Upload a File:**
   - Drag and drop or browse to select a PDF (`.pdf`), Word (`.docx`), or plain text (`.txt`) file (up to 25 MB).
   - Alternatively, choose one of the pre-loaded legal templates (e.g., `sample_contract.pdf` or `sample_arbitration_agreement.txt`).
3. Click **"Run Legal Analysis"**.
4. The system processes the document in approximately 200–350 milliseconds and automatically opens the **Analysis Results** view.

---

## 5. Navigating Analysis Results

The Analysis Results view provides 7 dedicated tabs:

### 5.1 Document Overview
- **Executive Metrics:** Word count, detected entities, unique keywords, clause count, and extraction latency.
- **Identified Parties:** Extracted organizational and individual entities.
- **Effective Dates & Total Values:** Identified contract dates and monetary amounts.
- **Attention Areas:** Highlighted risk clauses (Indemnity, Termination, Governing Law, Arbitration).

### 5.2 Important Clauses
- Displays clauses detected across 13 legal categories (e.g., *Confidentiality, Termination, Indemnity, Arbitration, Limitation of Liability*).
- Displays statistical confidence scores and original document snippets.
- Click **"Jump to Viewer"** to immediately open the document at that exact clause.

### 5.3 Obligations & Duties
- Categorizes contractual mandates:
  - **Affirmative Duties:** Actions a party *must* or *shall* perform.
  - **Prohibitions:** Actions a party *shall not* or *must not* perform.
- Identifies responsible party attribution and associated deadlines.

### 5.4 Dates, Money & Deadlines
- **Dates:** Extracted calendar dates, effective dates, and execution dates.
- **Monetary Values:** Multi-currency amounts (INR ₹, USD $, EUR €, GBP £).
- **Deadlines:** Timeframes (e.g., *30 days, within 14 business days*).

### 5.5 Keywords
- Shows top legal terms ranked by our hybrid score (TF-IDF + RAKE graph degree + Legal dictionary weight).
- Filter by category: General, Procedural, Substantive, or Corporate.

### 5.6 Named Entities
- View entities classified across 13 legal categories: *Statutes, Sections, Courts, Legal Roles, Case Citations, Persons, Organizations, and Locations*.

### 5.7 In-Document Search
- Search within the document using passage relevance scoring.
- Displays match frequency, scored snippets, and exact character offsets.

---

## 6. Document Viewer & Interactive Highlighting

Click **"Document Viewer"** in the top navigation or use **"Jump to Viewer"** from any extraction card:
- View the full formatted document text.
- Use the **Layer Toggle** to view:
  - **Keywords Only:** Highlights extracted legal terms in warm amber.
  - **Clean Plain Text:** Displays distraction-free plain text.
  - **Original Stream:** Shows the extracted text with line breaks preserved.

---

## 7. Side-by-Side Document Comparison

1. Click **"Document Comparison"** in the navigation bar.
2. Select **Document A** and **Document B** from your repository.
3. Click **"Compare Documents"**.
4. Review:
   - **Cosine Vector Similarity Score (0–100%)**: Based on shared legal terminology.
   - **Vocabulary Delta**: Word count differences and shared vs. unique keywords.
   - **Clause Alignment Table**: Side-by-side comparison of corresponding clauses in both agreements.

---

## 8. Exporting Analysis Reports

From the Analysis Results page:
- Click **"Export PDF"** to generate a multi-page vector PDF report containing executive summary, key findings, detected clauses, obligations, and legal notices.
- Click **"Export JSON"** for a structured machine-readable export suitable for external archiving or data pipelines.

---

## 9. Repository History

Click **"Repository History"** in the navigation bar to view all previously analyzed documents:
- Review past upload dates, file sizes, and status.
- Re-open past analysis results without re-uploading.
- Delete documents securely (automatically cascades to remove associated extractions and runs).

---

## 10. Administrator Audit Trail

*(Available to users with the `ADMIN` role)*
1. Click **"Admin Audit"** in the navigation.
2. Inspect the immutable security audit log:
   - Actor identity and username.
   - Action type (`DOCUMENT_UPLOAD`, `ANALYSIS_EXECUTE`, `USER_LOGIN`).
   - Resource affected, client IP address, and UTC timestamp.
   - Search and filter by user or action.

---

## 11. Known System Limitations

1. **Scanned Documents Without OCR:** The system expects digital text streams. Scanned image-only PDFs without an embedded text layer will return a prompt to OCR the document first.
2. **Local Explainable NLP:** LexExtract uses deterministic rule-and-statistical algorithms. It does not generate creative text or rewrite agreements.
3. **English Language Contracts:** Current legal gazetteers and grammatical rules are optimized for English-language legal instruments.

---

## 12. Legal Disclaimer

> **IMPORTANT NOTICE:**  
> LexExtract is an assistive statistical and natural language processing tool developed for academic and informational purposes. It does not provide legal advice, legal representation, or formal legal opinions. Output extractions must be reviewed and verified by qualified legal professionals before taking any legal, commercial, or regulatory action.
