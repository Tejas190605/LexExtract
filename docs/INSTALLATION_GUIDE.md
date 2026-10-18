# LexExtract — Installation & Deployment Guide

**Application Version:** 1.0.0  
**Project:** LexExtract — Legal Document Keyword & Entity Extractor  
**Date:** October 2026  

---

## 1. System Requirements

- **Operating System:** Windows 10/11, Ubuntu 22.04 LTS+, or macOS 13+
- **Python:** Python 3.10 – 3.14 (Tested on Python 3.14)
- **Node.js:** Node.js 18.x or 20.x LTS with npm 9.x+
- **Memory (RAM):** 4 GB minimum (8 GB recommended)
- **Disk Space:** 1 GB free disk space

---

## 2. Repository Setup

Clone or download the repository to your local workspace:

```bash
git clone <repository_url> "PBL project (ES,ASTMA,ITPM)"
cd "PBL project (ES,ASTMA,ITPM)"
```

---

## 3. Backend Setup & Configuration

### 3.1 Create and Activate Virtual Environment
```bash
cd backend
python -m venv .venv

# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1

# On Linux/macOS:
source .venv/bin/activate
```

### 3.2 Install Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 3.3 Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Default `.env` configuration:
```env
PROJECT_NAME="LexExtract"
PROJECT_DESCRIPTION="Legal Document Keyword & Entity Extractor"
VERSION="0.1.0"
ENVIRONMENT="development"
DEBUG=True
SECRET_KEY="lexextract-academic-secret-key-change-in-production-2026"
ACCESS_TOKEN_EXPIRE_MINUTES=60
ALGORITHM="HS256"
DATABASE_URL="sqlite:///../storage/lexextract.db"
MAX_UPLOAD_SIZE_BYTES=10485760
```

### 3.4 Initialize and Seed Database
Run the seed utility to create all tables and set up the default demo accounts:
```bash
python scripts/init_db.py
```
This initializes the SQLite schema in `backend/storage/lexextract.db` and seeds the default administrator, analyst, and demonstration lawyer accounts.

### 3.5 Start Backend Server
```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```
- API Base URL: `http://127.0.0.1:8000`
- Interactive OpenAPI Docs: `http://127.0.0.1:8000/docs`
- Health Probe: `http://127.0.0.1:8000/health`

---

## 4. Frontend Setup & Configuration

Open a second terminal window:

### 4.1 Install Node Dependencies
```bash
cd frontend
npm install
```

### 4.2 Configure Frontend Environment
Ensure `.env` exists in `frontend/` (or copy `.env.example`):
```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

### 4.3 Start Development Server
```bash
npm run dev
```
Open `http://127.0.0.1:5173` in your browser.

### 4.4 Build for Production
To generate an optimized static production bundle:
```bash
npm run build
```
Compiled output is saved to `frontend/dist/`.

---

## 5. Running the Automated Test Suite

To run all backend unit, integration, RBAC, and edge-case tests:

```bash
cd backend
.\.venv\Scripts\pytest.exe -v
```

Expected result:
```
======================= 119 passed, 1 warning in ~40s =======================
```

---

## 6. Pre-Configured Demonstration Accounts

| Role | Username | Email | Password |
| :--- | :--- | :--- | :--- |
| **System Admin** | `admin` | `admin@lexextract.local` | `Admin@Lex2026!` |
| **Legal Analyst** | `analyst` | `analyst@lexextract.local` | `Analyst@Lex2026!` |
| **Standard Lawyer** | `lawyer_user` | `demo@lexextract.local` | `User@Lex2026!` |
