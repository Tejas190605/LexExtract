"""
Safe Development & Test Environment Reset Utility for LexExtract.

Features:
1. Automatically creates a timestamped safety backup of `lexextract.db` before any reset.
2. Archives existing uploaded files in `storage/uploads` to `storage/uploads_archive_<timestamp>`.
3. Cleanses test records: documents, analyses, extracted keywords/entities, audit logs, and test users.
4. Preserves database schema, table structures, and migrations.
5. Seeds ONLY the single initial development ADMIN account (`admin` / `Admin@Lex2026!`).
6. Leaves the system ready for the FIRST-USER registration workflow via the UI.

Usage:
    python backend/scripts/reset_dev_environment.py
"""

import os
import sys
import shutil
import datetime
import sqlite3

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.core.config import settings
from app.core.database import engine, init_db, SessionLocal
from app.core.security import hash_password
from app.models.user import User


def reset_environment():
    db_path = os.path.join(settings.STORAGE_DIR, "lexextract.db")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print("=" * 60)
    print("LEXEXTRACT SAFE TEST ENVIRONMENT RESET")
    print("=" * 60)
    
    # Step 1: Backup existing database if present
    if os.path.exists(db_path):
        backup_path = os.path.join(settings.STORAGE_DIR, f"lexextract.db.bak_{timestamp}")
        print(f"--> [1/5] Creating safety backup of database:\n    Destination: {backup_path}")
        shutil.copy2(db_path, backup_path)
    else:
        print("--> [1/5] No existing database file found. Proceeding to create fresh database.")

    # Step 2: Archive uploaded documents
    uploads_dir = settings.UPLOAD_DIR
    if os.path.exists(uploads_dir):
        files_to_archive = [f for f in os.listdir(uploads_dir) if f != ".gitkeep"]
        if files_to_archive:
            archive_dir = os.path.join(settings.STORAGE_DIR, f"uploads_archive_{timestamp}")
            os.makedirs(archive_dir, exist_ok=True)
            print(f"--> [2/5] Archiving {len(files_to_archive)} uploaded files to:\n    {archive_dir}")
            for f in files_to_archive:
                src = os.path.join(uploads_dir, f)
                dst = os.path.join(archive_dir, f)
                shutil.move(src, dst)
        else:
            print("--> [2/5] Uploads folder is already clean (0 files).")
    else:
        os.makedirs(uploads_dir, exist_ok=True)

    # Step 3: Ensure Schema & Clean Tables
    print("--> [3/5] Resetting database tables while preserving schema...")
    init_db(engine)
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = OFF;")
        cursor.execute("DELETE FROM extracted_keywords;")
        cursor.execute("DELETE FROM extracted_entities;")
        cursor.execute("DELETE FROM analysis_runs;")
        cursor.execute("DELETE FROM documents;")
        cursor.execute("DELETE FROM audit_logs;")
        cursor.execute("DELETE FROM users;")
        try:
            cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('users', 'documents', 'analysis_runs', 'audit_logs', 'extracted_keywords', 'extracted_entities');")
        except sqlite3.OperationalError:
            pass
        cursor.execute("PRAGMA foreign_keys = ON;")
        conn.commit()
    print("    Cleared: extracted_keywords, extracted_entities, analysis_runs, documents, audit_logs, users.")

    # Step 4: Seed Single Admin Account for System Governance
    print("--> [4/5] Seeding clean development-only ADMIN account...")
    db = SessionLocal()
    try:
        admin_user = User(
            username="admin",
            email="admin@lexextract.local",
            full_name="System Administrator",
            name="System Administrator",
            password_hash=hash_password("Admin@Lex2026!"),
            role="ADMIN",
            is_active=True
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        print(f"    Admin seeded successfully (ID: {admin_user.id}, Username: admin, Role: ADMIN).")
    except Exception as exc:
        db.rollback()
        print(f"    Error seeding admin user: {exc}", file=sys.stderr)
        raise exc
    finally:
        db.close()

    # Step 5: Verify clean environment state
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        user_count = cursor.execute("SELECT count(*) FROM users").fetchone()[0]
        doc_count = cursor.execute("SELECT count(*) FROM documents").fetchone()[0]
        analysis_count = cursor.execute("SELECT count(*) FROM analysis_runs").fetchone()[0]
        audit_count = cursor.execute("SELECT count(*) FROM audit_logs").fetchone()[0]
        
    print("--> [5/5] Verification of clean environment state:")
    print(f"    Users: {user_count} (only admin)")
    print(f"    Documents: {doc_count} (0 ordinary documents)")
    print(f"    Analysis History: {analysis_count} (0 runs)")
    print(f"    Audit Records: {audit_count} (0 logs)")
    print("=" * 60)
    print("CLEAN TEST ENVIRONMENT IS READY!")
    print("Administrator Account:")
    print("  Username: admin")
    print("  Password: Admin@Lex2026!")
    print("  Role:     ADMIN")
    print("You can now test registering the FIRST regular user through the UI.")
    print("=" * 60)


if __name__ == "__main__":
    reset_environment()
