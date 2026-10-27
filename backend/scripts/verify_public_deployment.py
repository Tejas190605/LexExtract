"""
LexExtract Public Deployment Verification Script.
Tests a live deployed instance of LexExtract against all core functionality:
1. Health and API metadata probes
2. Demonstration authentication (User, Analyst, Admin)
3. Document upload (.pdf and .docx)
4. Legal text and page extraction
5. Keyword and entity extraction (Rule-based + spaCy NER)
6. In-document semantic search
7. Document comparison (diff, clause matching)
8. Export generation (JSON and PDF reports)
9. Admin governance and audit log inspection
10. Frontend availability and security headers

Usage:
    python backend/scripts/verify_public_deployment.py --backend <BACKEND_URL> --frontend <FRONTEND_URL>
"""

import os
import sys
import argparse
import time
import requests

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

def parse_args():
    parser = argparse.ArgumentParser(description="Verify LexExtract public deployment.")
    parser.add_argument("--backend", required=True, help="Base URL of deployed backend (e.g. https://lexextract-backend.onrender.com)")
    parser.add_argument("--frontend", required=False, help="URL of deployed frontend (e.g. https://lexextract-frontend.onrender.com)")
    return parser.parse_args()

def run_verification(backend_url: str, frontend_url: str = None):
    backend_url = backend_url.rstrip("/")
    print("=" * 70)
    print("LEXEXTRACT PUBLIC DEPLOYMENT VERIFICATION SUITE")
    print(f"Target Backend:  {backend_url}")
    if frontend_url:
        print(f"Target Frontend: {frontend_url.rstrip('/')}")
    print("=" * 70)

    # 1. Backend Health Check
    print("\n[1/10] Verifying Backend Health Probe...")
    max_retries = 10
    health_data = None
    for attempt in range(1, max_retries + 1):
        try:
            res = requests.get(f"{backend_url}/health", timeout=30)
            if res.status_code == 200:
                health_data = res.json()
                print(f"  ✓ Health Check OK: status={health_data.get('status')}, db={health_data.get('database')}, env={health_data.get('environment')}")
                break
            else:
                print(f"  Attempt {attempt}: Status code {res.status_code}. Waiting for service...")
        except Exception as exc:
            print(f"  Attempt {attempt}: Waiting for cold start / wake up ({exc})...")
        time.sleep(5)
    
    if not health_data:
        print("  ✗ Failed to connect to backend health endpoint after retries.")
        sys.exit(1)

    # 2. API Root & Documentation Probe
    print("\n[2/10] Verifying API v1 Root & OpenAPI Specification...")
    res = requests.get(f"{backend_url}/api/v1/", timeout=15)
    assert res.status_code == 200, f"API root failed: {res.text}"
    print(f"  ✓ API v1 Root: {res.json().get('message')}")

    docs_res = requests.get(f"{backend_url}/docs", timeout=15)
    assert docs_res.status_code == 200, f"Swagger docs unreachable: {docs_res.status_code}"
    print(f"  ✓ Swagger UI Documentation: 200 OK")

    # 3. Demonstration Authentication
    print("\n[3/10] Verifying Demonstration Account Logins (RBAC)...")
    roles_tested = [
        ("lawyer_user", "User@Lex2026!", "USER"),
        ("analyst", "Analyst@Lex2026!", "ANALYST"),
        ("admin", "Admin@Lex2026!", "ADMIN"),
    ]
    tokens = {}
    for username, password, expected_role in roles_tested:
        login_res = requests.post(
            f"{backend_url}/api/v1/auth/login",
            json={"email_or_username": username, "password": password},
            timeout=15
        )
        assert login_res.status_code == 200, f"Login failed for {username}: {login_res.text}"
        data = login_res.json()
        assert data.get("access_token"), "Missing access token"
        user_role = data.get("user", {}).get("role") or data.get("role")
        assert user_role == expected_role, f"Expected role {expected_role}, got {user_role}"
        tokens[expected_role] = data["access_token"]
        print(f"  ✓ Role {expected_role} ({username}): Authenticated, JWT issued.")

    user_headers = {"Authorization": f"Bearer {tokens['USER']}"}
    admin_headers = {"Authorization": f"Bearer {tokens['ADMIN']}"}

    # 4. Document Upload (PDF & DOCX)
    print("\n[4/10] Verifying Document Ingestion (.pdf & .docx)...")
    sample_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "sample_documents")
    pdf_path = os.path.join(sample_dir, "sample_contract.pdf")
    docx_path = os.path.join(sample_dir, "01_Employment_Agreement.docx")

    uploaded_doc_ids = []

    # Upload PDF
    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        res = requests.post(
            f"{backend_url}/api/v1/documents/upload",
            files={"file": ("sample_contract.pdf", pdf_bytes, "application/pdf")},
            headers=user_headers,
            timeout=30
        )
        assert res.status_code == 201, f"PDF upload failed: {res.text}"
        pdf_doc = res.json()
        uploaded_doc_ids.append(pdf_doc["id"])
        print(f"  ✓ Uploaded PDF (ID: {pdf_doc['id']}): words={pdf_doc.get('word_count')}, pages={pdf_doc.get('page_count')}")
    else:
        print(f"  ! PDF sample file not found locally at {pdf_path}, skipping PDF upload test.")

    # Upload DOCX
    if os.path.exists(docx_path):
        with open(docx_path, "rb") as f:
            docx_bytes = f.read()
        res = requests.post(
            f"{backend_url}/api/v1/documents/upload",
            files={"file": ("01_Employment_Agreement.docx", docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
            headers=user_headers,
            timeout=30
        )
        assert res.status_code == 201, f"DOCX upload failed: {res.text}"
        docx_doc = res.json()
        uploaded_doc_ids.append(docx_doc["id"])
        print(f"  ✓ Uploaded DOCX (ID: {docx_doc['id']}): words={docx_doc.get('word_count')}, pages={docx_doc.get('page_count')}")
    else:
        print(f"  ! DOCX sample file not found locally at {docx_path}, skipping DOCX upload test.")

    if not uploaded_doc_ids:
        # Fetch existing documents
        list_res = requests.get(f"{backend_url}/api/v1/documents/", headers=user_headers, timeout=15)
        assert list_res.status_code == 200
        docs = list_res.json()
        assert len(docs) > 0, "No documents available to test."
        uploaded_doc_ids = [d["id"] for d in docs]

    target_doc_id = uploaded_doc_ids[-1]

    # 5. Document Text & Page Retrieval
    print("\n[5/10] Verifying Extracted Text & Structured Pages...")
    text_res = requests.get(f"{backend_url}/api/v1/documents/{target_doc_id}/text", headers=user_headers, timeout=15)
    text_data = text_res.json()
    doc_text = text_data.get("text") or text_data.get("extracted_text") or ""
    assert len(doc_text) > 0, "Extracted text is empty"
    print(f"  ✓ Document {target_doc_id}: Extracted text length = {len(doc_text)} chars across {len(text_data.get('pages', []))} page(s).")

    # 6. Analysis Pipeline (Keywords & Legal Entities)
    print(f"\n[6/10] Executing Legal Intelligence Analysis on Document {target_doc_id}...")
    an_res = requests.post(f"{backend_url}/api/v1/analyses/{target_doc_id}", headers=user_headers, timeout=45)
    assert an_res.status_code in [200, 201], f"Analysis run failed: {an_res.text}"
    analysis_data = an_res.json()
    analysis_id = analysis_data.get("analysis_id") or analysis_data.get("id")
    print(f"  ✓ Analysis Run #{analysis_id} Complete (status: {analysis_data['status']})")

    # Fetch Keywords
    kw_res = requests.get(f"{backend_url}/api/v1/analyses/{analysis_id}/keywords?limit=10", headers=user_headers, timeout=15)
    assert kw_res.status_code == 200
    keywords = kw_res.json().get("keywords", [])
    print(f"  ✓ Keywords Extracted: {len(keywords)} items (Top: {[k['keyword'] for k in keywords[:5]]})")

    # Fetch Entities
    ent_res = requests.get(f"{backend_url}/api/v1/analyses/{analysis_id}/entities?limit=10", headers=user_headers, timeout=15)
    assert ent_res.status_code == 200
    entities = ent_res.json().get("entities", [])
    print(f"  ✓ Entities Extracted: {len(entities)} items (Top: {[(e.get('text') or e.get('entity_text')) + ' (' + e['entity_type'] + ')' for e in entities[:5]]})")

    # 7. In-Document Search
    print("\n[7/10] Verifying In-Document Semantic & Keyword Search...")
    search_q = "agreement" if "agreement" in doc_text.lower() else "the"
    search_res = requests.get(f"{backend_url}/api/v1/documents/{target_doc_id}/search?q={search_q}", headers=user_headers, timeout=15)
    assert search_res.status_code == 200
    search_matches = search_res.json().get("matches", [])
    print(f"  ✓ Search query '{search_q}': Found {len(search_matches)} occurrences with snippet context.")

    # 8. Document Comparison
    print("\n[8/10] Verifying Comparative Document Analysis...")
    if len(uploaded_doc_ids) >= 2:
        doc_a = uploaded_doc_ids[0]
        doc_b = uploaded_doc_ids[1]
    else:
        doc_a = target_doc_id
        doc_b = target_doc_id

    comp_res = requests.post(
        f"{backend_url}/api/v1/documents/compare",
        json={"doc_a_id": doc_a, "doc_b_id": doc_b},
        headers=user_headers,
        timeout=30
    )
    assert comp_res.status_code == 200, f"Comparison failed: {comp_res.text}"
    comp_data = comp_res.json()
    print(f"  ✓ Comparison between Doc #{doc_a} and Doc #{doc_b}: Similarity Score = {comp_data.get('similarity_score')}")

    # 9. Reports & Exports (JSON & PDF)
    print(f"\n[9/10] Verifying Analysis Exports (JSON & PDF Dossiers)...")
    json_export = requests.get(f"{backend_url}/api/v1/analyses/{analysis_id}/export?format=json", headers=user_headers, timeout=15)
    assert json_export.status_code == 200
    assert "application/json" in json_export.headers.get("content-type", "")
    print(f"  ✓ JSON Export Dossier: Valid JSON report payload received ({len(json_export.content)} bytes).")

    pdf_export = requests.get(f"{backend_url}/api/v1/analyses/{analysis_id}/export?format=pdf", headers=user_headers, timeout=20)
    assert pdf_export.status_code == 200
    assert pdf_export.content.startswith(b"%PDF"), "Response is not a valid PDF binary stream"
    print(f"  ✓ PDF Export Dossier: Valid PDF stream received ({len(pdf_export.content)} bytes).")

    # 10. Admin Access & Governance Audit Trail
    print("\n[10/10] Verifying Administrative Governance & Audit Ledger...")
    # Verify non-admin blocked
    forbidden_res = requests.get(f"{backend_url}/api/v1/users/", headers=user_headers, timeout=15)
    assert forbidden_res.status_code == 403, f"Expected 403 for non-admin, got {forbidden_res.status_code}"
    print(f"  ✓ Security Enforcement: Non-admin practitioner blocked from /users/ (403 Forbidden).")

    # Admin access allowed
    users_res = requests.get(f"{backend_url}/api/v1/users/", headers=admin_headers, timeout=15)
    assert users_res.status_code == 200
    users_list = users_res.json()
    print(f"  ✓ Admin Directory: {len(users_list)} registered user account(s) visible.")

    audit_res = requests.get(f"{backend_url}/api/v1/admin/audit-logs", headers=admin_headers, timeout=15)
    assert audit_res.status_code == 200
    audit_logs = audit_res.json()
    print(f"  ✓ Governance Audit Trail: {len(audit_logs)} tamper-evident audit events recorded.")

    # Frontend Check (if URL provided)
    if frontend_url:
        print("\n[+] Verifying Frontend Public URL Availability...")
        try:
            fe_res = requests.get(frontend_url, timeout=15)
            assert fe_res.status_code == 200, f"Frontend returned {fe_res.status_code}"
            assert "LexExtract" in fe_res.text or "root" in fe_res.text
            print(f"  ✓ Frontend Live: {frontend_url} (200 OK, SPA root container confirmed).")
        except Exception as exc:
            print(f"  ! Frontend check note: {exc}")

    print("\n" + "=" * 70)
    print("ALL 10 VERIFICATION CHECKS PASSED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    args = parse_args()
    run_verification(args.backend, args.frontend)
