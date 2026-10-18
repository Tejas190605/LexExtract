"""
Database Initialization & Development Seed Utility for LexExtract.
Usage:
    python scripts/init_db.py
"""

import os
import sys

# Ensure backend root is on sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.core.database import engine, init_db, SessionLocal
from app.core.security import hash_password
from app.models.user import User
from app.models.document import Document


DEMO_ACCOUNTS = [
    {
        "email": "admin@lexextract.local",
        "username": "admin",
        "full_name": "System Administrator",
        "password": "Admin@Lex2026!",
        "role": "ADMIN",
        "is_active": True,
    },
    {
        "email": "analyst@lexextract.local",
        "username": "analyst",
        "full_name": "Senior Legal Analyst",
        "password": "Analyst@Lex2026!",
        "role": "ANALYST",
        "is_active": True,
    },
    {
        "email": "demo@lexextract.local",
        "username": "lawyer_user",
        "full_name": "Demonstration Lawyer",
        "password": "User@Lex2026!",
        "role": "USER",
        "is_active": True,
    }
]


def seed_database():
    """
    Creates tables if they don't exist and safely seeds initial development records.
    Idempotent: Does not insert duplicates if already executed.
    """
    print("--> Initializing SQLite database schema and applying migrations...")
    init_db(engine)
    print("--> Schema created / verified successfully.")

    db = SessionLocal()
    try:
        # 1. Seed Demo Accounts
        for account in DEMO_ACCOUNTS:
            existing_user = db.query(User).filter(
                (User.email == account["email"]) | (User.username == account["username"])
            ).first()

            if not existing_user:
                print(f"--> Seeding development user: {account['username']} ({account['email']}, Role: {account['role']})...")
                user = User(
                    username=account["username"],
                    email=account["email"],
                    full_name=account["full_name"],
                    name=account["full_name"],
                    password_hash=hash_password(account["password"]),
                    role=account["role"],
                    is_active=account["is_active"]
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                print(f"    Created user ID: {user.id}")
            else:
                # Update password hash if legacy placeholder hash exists
                if existing_user.password_hash.startswith("placeholder"):
                    print(f"    Updating password hash for existing user ID: {existing_user.id}")
                    existing_user.password_hash = hash_password(account["password"])
                    existing_user.role = account["role"]
                    db.commit()
                print(f"--> User already exists: {account['username']} (ID: {existing_user.id}). Skipping.")

        # 2. Check sample document for demo user
        demo_user = db.query(User).filter(User.email == "demo@lexextract.local").first()
        if demo_user:
            sample_filename = "sample_commercial_lease.pdf"
            doc = db.query(Document).filter(
                Document.user_id == demo_user.id,
                Document.filename == sample_filename
            ).first()

            if not doc:
                print(f"--> Seeding sample document metadata ({sample_filename})...")
                doc = Document(
                    user_id=demo_user.id,
                    owner_id=demo_user.id,
                    filename=sample_filename,
                    stored_filename="doc_seed_sample_lease.pdf",
                    file_type="pdf",
                    file_size=1048576,
                    file_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                    page_count=5,
                    word_count=2450,
                    status="uploaded",
                )
                db.add(doc)
                db.commit()
                db.refresh(doc)
                print(f"--> Sample document created with ID: {doc.id}")
            else:
                print(f"--> Sample document already exists (ID: {doc.id}). Skipping document seed.")

        print("--> Database initialization and seeding complete.")

    except Exception as exc:
        db.rollback()
        print(f"ERROR during seeding: {exc}", file=sys.stderr)
        raise exc
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
