# LexExtract — Relational Database Schema & Data Dictionary

## 1. Database Architecture Overview

LexExtract utilizes a relational data model managed via SQLAlchemy 2.0 ORM. The default storage engine is SQLite (`backend/storage/lexextract.db`), configured with foreign key enforcement and connection pooling. The schema is organized into six normalized tables designed to manage user identities, document files, extraction runs, and compliance audit records.

```
                    ┌──────────────┐
                    │    users     │
                    └──────┬───────┘
                           │ 1
                           │
             ┌─────────────┴─────────────┐
           * │                         * │
     ┌───────▼────────┐          ┌───────▼────────┐
     │   documents    │          │   audit_logs   │
     └───────┬────────┘          └────────────────┘
             │ 1
             │
           * │
     ┌───────▼────────┐
     │ analysis_runs  │
     └───────┬────────┘
             │ 1
             │
       ┌─────┴─────┐
     * │         * │
┌──────▼──────┐ ┌──▼──────────┐
│  extracted  │ │  extracted  │
│  keywords   │ │  entities   │
└─────────────┘ └─────────────┘
```

---

## 2. Table Specifications & Data Dictionary

### 2.1 Table: `users`
- **Purpose:** Stores user identities, encrypted credentials, access roles, and account status.
- **SQL Table Name:** `users`

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | Primary Key, Auto-increment | Unique identifier for the user account. |
| `email` | `VARCHAR(255)` | Unique, Not Null, Index | User's email address used for login. |
| `username` | `VARCHAR(50)` | Unique, Not Null, Index | Unique system username. |
| `full_name` | `VARCHAR(100)` | Nullable | User's display name. |
| `name` | `VARCHAR(100)` | Nullable | Legacy display name alias. |
| `password_hash` | `VARCHAR(255)` | Not Null | Argon2id cryptographically hashed password. |
| `role` | `VARCHAR(20)` | Not Null, Default: `'USER'` | Access role (`USER`, `ANALYST`, `ADMIN`). |
| `is_active` | `BOOLEAN` | Not Null, Default: `True` | Account active flag (disabled users cannot log in). |
| `created_at` | `DATETIME` | Default: UTC Now | Account creation timestamp. |
| `updated_at` | `DATETIME` | Nullable | Account modification timestamp. |

- **Relationships:**
  - `documents`: One-to-many relationship with `Document` (`User.documents`).
  - `audit_logs`: One-to-many relationship with `AuditLog` (`User.audit_logs`).

---

### 2.2 Table: `documents`
- **Purpose:** Tracks uploaded legal briefs, stored file paths, cryptographic checksums, and extracted text.
- **SQL Table Name:** `documents`

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | Primary Key, Auto-increment | Unique identifier for the uploaded brief. |
| `owner_id` | `INTEGER` | Foreign Key (`users.id`), Index | User account that owns and manages the document. |
| `user_id` | `INTEGER` | Foreign Key (`users.id`), Nullable | Legacy owner identifier alias. |
| `filename` | `VARCHAR(255)` | Not Null | Original filename of uploaded document. |
| `stored_filename`| `VARCHAR(255)`| Not Null | Unique internal stored filename in uploads folder. |
| `file_type` | `VARCHAR(10)` | Not Null | Format extension (`pdf` or `docx`). |
| `file_size` | `INTEGER` | Not Null | File size in bytes. |
| `file_hash` | `VARCHAR(64)` | Index | SHA-256 cryptographic hash of file content. |
| `page_count` | `INTEGER` | Nullable | Number of pages (for PDF briefs). |
| `word_count` | `INTEGER` | Not Null, Default: `0` | Total words extracted from document. |
| `extracted_text` | `TEXT` | Nullable | Full extracted and normalized plain text. |
| `pages_json` | `TEXT` | Nullable | JSON-serialized array of per-page text segments. |
| `status` | `VARCHAR(20)` | Default: `'uploaded'` | Processing status (`uploaded`, `analyzed`, `failed`). |
| `created_at` | `DATETIME` | Default: UTC Now | Document upload timestamp. |

- **Relationships:**
  - `owner`: Many-to-one relationship with `User`.
  - `analyses`: One-to-many relationship with `AnalysisRun` (`cascade="all, delete-orphan"`).

---

### 2.3 Table: `analysis_runs`
- **Purpose:** Records NLP extraction execution runs, processing latencies, and summary statistics.
- **SQL Table Name:** `analysis_runs`

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | Primary Key, Auto-increment | Unique identifier for the analysis execution. |
| `document_id` | `INTEGER` | Foreign Key (`documents.id`), Index | Target document that was analyzed. |
| `status` | `VARCHAR(20)` | Default: `'processing'` | Execution status (`processing`, `completed`, `failed`). |
| `processing_time`| `FLOAT` | Nullable | Total execution latency in seconds. |
| `total_keywords` | `INTEGER` | Default: `0` | Number of ranked keywords extracted. |
| `total_entities` | `INTEGER` | Default: `0` | Number of typed legal entities extracted. |
| `created_at` | `DATETIME` | Default: UTC Now | Analysis trigger timestamp. |
| `completed_at` | `DATETIME` | Nullable | Analysis completion timestamp. |

- **Relationships:**
  - `document`: Many-to-one relationship with `Document`.
  - `keywords`: One-to-many relationship with `ExtractedKeyword` (`cascade="all, delete-orphan"`).
  - `entities`: One-to-many relationship with `ExtractedEntity` (`cascade="all, delete-orphan"`).

---

### 2.4 Table: `extracted_keywords`
- **Purpose:** Stores ranked keywords extracted by the tri-model fusion pipeline.
- **SQL Table Name:** `extracted_keywords`

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | Primary Key, Auto-increment | Unique keyword record identifier. |
| `analysis_id` | `INTEGER` | Foreign Key (`analysis_runs.id`), Index | Associated analysis run. |
| `analysis_run_id`| `INTEGER`| Nullable | Legacy foreign key alias. |
| `keyword` | `VARCHAR(255)` | Not Null | Clean normalized keyword or multi-word phrase. |
| `final_score` | `FLOAT` | Not Null | Composite weighted score ($[0.0, 1.0]$). |
| `category` | `VARCHAR(50)` | Default: `'General'` | Legal domain category (`Contract`, `Litigation`, etc.). |
| `frequency` | `INTEGER` | Default: `1` | Token occurrence count in source text. |
| `rank` | `INTEGER` | Default: `1` | Rank position in descending order of score. |
| `tfidf_score` | `FLOAT` | Default: `0.0` | Component TF-IDF score contribution. |
| `rake_score` | `FLOAT` | Default: `0.0` | Component RAKE graph score contribution. |
| `lexicon_score` | `FLOAT` | Default: `0.0` | Component domain dictionary boost. |

---

### 2.5 Table: `extracted_entities`
- **Purpose:** Stores typed legal entities extracted by the hybrid spaCy and regex gazetteer pipeline.
- **SQL Table Name:** `extracted_entities`

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | Primary Key, Auto-increment | Unique entity record identifier. |
| `analysis_id` | `INTEGER` | Foreign Key (`analysis_runs.id`), Index | Associated analysis run. |
| `analysis_run_id`| `INTEGER`| Nullable | Legacy foreign key alias. |
| `entity_text` | `VARCHAR(255)` | Not Null | Raw surface text span as it appears in document. |
| `normalized_text`| `VARCHAR(255)`| Not Null | Canonical normalized entity text. |
| `entity_type` | `VARCHAR(50)` | Not Null | Legal category (`COURT`, `STATUTE`, `SECTION`, etc.). |
| `confidence` | `FLOAT` | Default: `1.0` | Extraction confidence score ($[0.0, 1.0]$). |
| `source` | `VARCHAR(50)` | Default: `'rule'` | Extraction engine (`spacy`, `regex`, `gazetteer`, `hybrid`). |
| `start_position` | `INTEGER` | Default: `0` | Zero-indexed character start offset in document text. |
| `end_position` | `INTEGER` | Default: `0` | Zero-indexed character end offset in document text. |

---

### 2.6 Table: `audit_logs`
- **Purpose:** Non-repudiation security audit trail recording critical system operations.
- **SQL Table Name:** `audit_logs`

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | Primary Key, Auto-increment | Unique audit record identifier. |
| `user_id` | `INTEGER` | Foreign Key (`users.id`), Nullable | Actor account that triggered the event. |
| `action` | `VARCHAR(50)` | Not Null, Index | Action type (`LOGIN`, `DOCUMENT_UPLOAD`, etc.). |
| `resource_type` | `VARCHAR(50)` | Nullable | Target resource category (`DOCUMENT`, `ANALYSIS`, `USER`). |
| `resource_id` | `INTEGER` | Nullable | Identifier of target resource. |
| `status` | `VARCHAR(20)` | Default: `'SUCCESS'` | Outcome status (`SUCCESS` or `FAILURE`). |
| `details` | `TEXT` | Nullable | Informative description (passwords/tokens redacted). |
| `ip_address` | `VARCHAR(45)` | Nullable | Client IPv4 or IPv6 network address. |
| `timestamp` | `DATETIME` | Default: UTC Now, Index | Exact timestamp of event occurrence. |

---

## 3. Database Initialization & Migration Utilities
- The database schema is created and upgraded via `backend/app/core/database.py:init_db()`.
- Idempotent development seeding is provided via `backend/scripts/init_db.py`, which populates default accounts and baseline records without duplicating existing data.
