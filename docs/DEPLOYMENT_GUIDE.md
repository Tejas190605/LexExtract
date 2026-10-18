# LexExtract — Production Deployment & Hosting Guide

## 1. Overview & Architectural Deployment Model

LexExtract is designed for flexible deployment across local workstations, containerized Docker environments, and modern cloud platforms.

```
                      [ Client Web Browsers ]
                                 │
                                 ▼
                     [ Frontend Static Host ]
                 (Vercel / Netlify / Cloudflare)
                                 │
                   HTTPS / WSS   │ (REST API)
                                 ▼
                    [ Backend Cloud Container ]
                    (Render / Railway / Fly.io)
                                 │
               ┌─────────────────┴─────────────────┐
               ▼                                   ▼
    [ Managed PostgreSQL DB ]           [ Persistent File Volume / S3 ]
     (Supabase / Neon / AWS RDS)           (AWS S3 / Cloudflare R2)
```

---

## 2. Local Production / On-Premise Deployment

### 2.1 Prerequisites
- **Python:** 3.11, 3.12, or 3.14 (64-bit)
- **Node.js:** v18.x or v20.x LTS with npm
- **Git**

### 2.2 Backend Production Setup
```bash
# Navigate to backend directory
cd backend

# Create and activate Python virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
# source .venv/bin/activate

# Install production dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Download required spaCy statistical linguistic model
python -m spacy download en_core_web_sm

# Configure environment variables
copy .env.example .env
# Edit .env and set strong SECRET_KEY and ENVIRONMENT=production

# Initialize database schema and default admin accounts
python scripts/init_db.py

# Launch production server with Uvicorn (multi-worker for concurrency)
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 2.3 Frontend Production Setup
```bash
# Navigate to frontend directory
cd ../frontend

# Install node dependencies
npm install

# Configure production environment variables
copy .env.example .env
# Ensure VITE_API_BASE_URL points to the production backend (e.g., https://api.lexextract.com)

# Build optimized production bundle
npm run build

# Serve production bundle using a high-performance static server
# Example with 'serve' or Nginx:
npx serve -s dist -l 5173
```

---

## 3. Cloud Deployment Strategy

### 3.1 Frontend Hosting (Vercel / Netlify)
1. **Repository Link:** Connect the GitHub repository to Vercel or Netlify.
2. **Root Directory:** Set root directory to `frontend`.
3. **Build Command:** `npm run build`
4. **Output Directory:** `dist`
5. **Environment Variable:**
   ```env
   VITE_API_BASE_URL=https://your-backend-service.onrender.com
   ```
6. **SPA Routing Rule:** Include a rewrite rule (`_redirects` or `vercel.json`) redirecting `/*` to `/index.html` with status `200`.

### 3.2 Backend Hosting (Render / Railway / Fly.io)
1. **Repository Link:** Set root directory to `backend`.
2. **Build Command:**
   ```bash
   pip install -r requirements.txt && python -m spacy download en_core_web_sm
   ```
3. **Start Command:**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port $PORT --workers 2
   ```
4. **Environment Variables:**
   ```env
   PROJECT_NAME=LexExtract
   ENVIRONMENT=production
   DEBUG=False
   SECRET_KEY=generate-a-cryptographically-secure-random-string-here
   ACCESS_TOKEN_EXPIRE_MINUTES=120
   DATABASE_URL=postgresql://user:password@hostname:5432/lexextract_db
   BACKEND_CORS_ORIGINS=["https://your-frontend.vercel.app"]
   ```

---

## 4. Production Database Configuration (SQLite to PostgreSQL)

While LexExtract utilizes SQLite by default for zero-friction local development and academic evaluation, SQLAlchemy ORM supports seamless PostgreSQL migration without code alterations:

1. Provision a PostgreSQL instance (e.g. AWS RDS, Neon, Supabase).
2. Install the PostgreSQL driver in `backend/requirements.txt`:
   ```bash
   pip install psycopg2-binary
   ```
3. Update `DATABASE_URL` in `.env`:
   ```env
   DATABASE_URL=postgresql://db_user:strong_password@db_host:5432/lexextract
   ```
4. Run `python scripts/init_db.py` to create the schema and initial seed data automatically.

---

## 5. Storage & High Availability Considerations

- **Local Storage Limitations:** By default, files are saved in `backend/storage/uploads/`. In ephemeral containerized cloud environments (e.g., free tier Render/Heroku dynos), local files are lost across restarts.
- **Production Storage Solution:** For production deployment, attach a persistent storage volume or configure an S3-compatible object store (AWS S3, Google Cloud Storage, Cloudflare R2).

---

## 6. Security & Hardening Checklist

- [x] Enforce HTTPS / TLS for all incoming presentation and API traffic.
- [x] Configure explicit CORS origins in `.env` (`BACKEND_CORS_ORIGINS`); never use wildcard `*` with credentials in production.
- [x] Generate a 256-bit cryptographically secure `SECRET_KEY` using `openssl rand -hex 32`.
- [x] Verify Argon2id password hashing is enforced on all stored credentials.
- [x] Confirm no API secrets or production database credentials are committed to version control.
