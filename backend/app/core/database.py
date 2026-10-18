import os
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from app.core.config import settings

# Ensure storage directory exists
os.makedirs(settings.STORAGE_DIR, exist_ok=True)

# Configure SQLite engine with thread check disabled for FastAPI concurrency
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency yielding a clean database session per request.
    Guarantees session closure on completion or exception.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db(target_engine=None) -> None:
    """
    Initializes all database tables registered on declarative Base.
    Safe and idempotent (does not overwrite existing data).
    Also performs lightweight column upgrades for existing SQLite tables.
    """
    from app import models  # noqa: F401 - ensures all models register with Base
    curr_engine = target_engine or engine
    Base.metadata.create_all(bind=curr_engine)

    # Lightweight backward-compatible migration for existing SQLite tables
    try:
        with curr_engine.connect() as conn:
            # Check users table columns
            res_user = conn.execute(text("PRAGMA table_info(users)"))
            user_cols = [row[1] for row in res_user.fetchall()]
            if user_cols:
                if "username" not in user_cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN username VARCHAR(50)"))
                    # Populate default username from email
                    conn.execute(text("UPDATE users SET username = SUBSTR(email, 1, INSTR(email, '@') - 1) WHERE username IS NULL"))
                if "full_name" not in user_cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN full_name VARCHAR(100)"))
                    if "name" in user_cols:
                        conn.execute(text("UPDATE users SET full_name = name WHERE full_name IS NULL"))
                if "updated_at" not in user_cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN updated_at DATETIME"))

            # Check documents table columns
            res_doc = conn.execute(text("PRAGMA table_info(documents)"))
            doc_cols = [row[1] for row in res_doc.fetchall()]
            if doc_cols:
                if "extracted_text" not in doc_cols:
                    conn.execute(text("ALTER TABLE documents ADD COLUMN extracted_text TEXT"))
                if "pages_json" not in doc_cols:
                    conn.execute(text("ALTER TABLE documents ADD COLUMN pages_json TEXT"))
                if "owner_id" not in doc_cols:
                    conn.execute(text("ALTER TABLE documents ADD COLUMN owner_id INTEGER"))
                    if "user_id" in doc_cols:
                        conn.execute(text("UPDATE documents SET owner_id = user_id WHERE owner_id IS NULL"))

            # Check extracted_entities table columns
            res_ent = conn.execute(text("PRAGMA table_info(extracted_entities)"))
            ent_cols = [row[1] for row in res_ent.fetchall()]
            if ent_cols:
                if "normalized_text" not in ent_cols:
                    conn.execute(text("ALTER TABLE extracted_entities ADD COLUMN normalized_text VARCHAR(255)"))
                if "confidence" not in ent_cols:
                    conn.execute(text("ALTER TABLE extracted_entities ADD COLUMN confidence FLOAT DEFAULT 1.0"))
                if "source" not in ent_cols:
                    conn.execute(text("ALTER TABLE extracted_entities ADD COLUMN source VARCHAR(50) DEFAULT 'rule'"))

            # Check extracted_keywords table columns
            res_kw = conn.execute(text("PRAGMA table_info(extracted_keywords)"))
            kw_cols = [row[1] for row in res_kw.fetchall()]
            if kw_cols:
                if "rank" not in kw_cols:
                    conn.execute(text("ALTER TABLE extracted_keywords ADD COLUMN rank INTEGER DEFAULT 1"))

            # Check audit_logs table columns
            res_audit = conn.execute(text("PRAGMA table_info(audit_logs)"))
            audit_cols = [row[1] for row in res_audit.fetchall()]
            if audit_cols:
                if "resource_type" not in audit_cols:
                    conn.execute(text("ALTER TABLE audit_logs ADD COLUMN resource_type VARCHAR(50)"))
                if "resource_id" not in audit_cols:
                    conn.execute(text("ALTER TABLE audit_logs ADD COLUMN resource_id INTEGER"))
                if "status" not in audit_cols:
                    conn.execute(text("ALTER TABLE audit_logs ADD COLUMN status VARCHAR(20) DEFAULT 'SUCCESS'"))
                if "ip_address" not in audit_cols:
                    conn.execute(text("ALTER TABLE audit_logs ADD COLUMN ip_address VARCHAR(45)"))

            conn.commit()
    except Exception:
        # Ignore on non-sqlite or in-memory engines where metadata already created columns
        pass


def check_db_connection() -> bool:
    """
    Verifies live operational connectivity to the database engine.
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
