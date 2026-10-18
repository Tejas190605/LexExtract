# LexExtract — Demonstration Failure Contingency & Backup Plan

This document details diagnostic procedures, recovery steps, and fallback presentation assets in the event of hardware, network, or runtime issues during a live examination demonstration.

---

## 1. Quick Diagnostic Checklist

| Symptom | Probable Cause | Immediate Remediation Command |
| :--- | :--- | :--- |
| **Backend Not Responding (Port 8000)** | Uvicorn process terminated or port in use. | `cd backend && python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload` |
| **Frontend Not Loading (Port 5173)** | Vite development server stopped. | `cd frontend && npm run dev` |
| **Database Connection Error** | SQLite file lock or missing storage directory. | Verify `backend/storage/lexextract.db` exists. Run `python scripts/init_db.py`. |
| **Document Upload Rejection (400)** | Attempting to upload unsupported format. | Ensure uploading `.pdf` or `.docx` from `sample_documents/` folder. |
| **Missing spaCy Language Model** | Virtual environment recreated without model. | `python -m spacy download en_core_web_sm` |
| **Browser Port Conflict** | Port 5173 occupied by another process. | Check terminal for alternative port (e.g. `http://localhost:5174`). |

---

## 2. Failure Scenarios & Step-by-Step Recovery

### Scenario A: Backend API Fails to Start
1. Open PowerShell / Command Prompt as Administrator.
2. Check if port 8000 is occupied:
   ```powershell
   Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess
   ```
3. Terminate any orphaned Python process:
   ```powershell
   Stop-Process -Id <ProcessId> -Force
   ```
4. Restart the backend service:
   ```powershell
   cd "backend"
   python -m uvicorn main:app --host 127.0.0.1 --port 8000
   ```
5. Confirm operational state: Open `http://127.0.0.1:8000/health` in browser. Expect `{"status": "healthy", "database": "connected"}`.

### Scenario B: Database Corrupted or Empty
1. If the database file is missing or corrupted, re-initialize schema and demo accounts:
   ```bash
   cd backend
   python scripts/init_db.py
   ```
2. This creates all 6 tables and seeds the standard demo accounts:
   - `demo@lexextract.local` / `User@Lex2026!`
   - `analyst@lexextract.local` / `Analyst@Lex2026!`
   - `admin@lexextract.local` / `Admin@Lex2026!`

### Scenario C: File Upload Fails During Live Demo
1. If the file chooser dialog hangs or permissions fail, navigate to **"Repository History"** (`/history`).
2. Open pre-cataloged sample brief ID #1 (seeded commercial lease agreement).
3. Click **"Run Analysis"** or **"Open in Viewer"** directly from the history table.

### Scenario D: Live Evaluation Run Takes Too Long
1. If the evaluation endpoint takes longer than expected, the system maintains a persisted benchmark artifact:
   `backend/data/evaluation/latest_evaluation_report.json`
2. The Evaluation Page automatically loads the latest cached run results on initial page load. Refresh `/evaluation` to display the stored benchmark metrics without triggering a re-run.

---

## 3. Static Demonstration Fallback (No-Code Fallback)

If live execution is completely impossible due to hardware or operating system failure, fall back to the pre-recorded video artifacts and documented figures:

1. **Full End-to-End Walkthrough Recording:**
   - Location: `phase9_final_e2e_verify_1791218227518.webp` (WebP video artifact)
   - Demonstrates: Login $\rightarrow$ Dashboard $\rightarrow$ Upload $\rightarrow$ Analysis $\rightarrow$ Keyword Explorer $\rightarrow$ Entity Explorer $\rightarrow$ Document Viewer $\rightarrow$ Evaluation Run $\rightarrow$ Admin Audit Ledger.
2. **Screenshot Catalog:**
   - Refer to [`docs/SCREENSHOT_CATALOG.md`](file:///c:/Users/tejas/PBL%20project%20(ES,ASTMA,ITPM)/docs/SCREENSHOT_CATALOG.md) containing numbered figures of all key application views.
3. **Automated Verification Script Output:**
   - Refer to [`backend/verify_phase9_qa.py`](file:///c:/Users/tejas/PBL%20project%20(ES,ASTMA,ITPM)/backend/verify_phase9_qa.py) terminal logs confirming 100% pass rate across all 8 security and ingestion categories.
