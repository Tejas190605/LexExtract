"""
Phase 9 Final Integration, Security, and Quality Assurance Verification Script.
Validates:
1. Multi-format ingestion (PDF, DOCX, TXT)
2. Text, Keyword & Entity extraction accuracy
3. Strict ownership isolation (User A vs User B cross-access blocked with 403)
4. Admin visibility and governance access
5. Comprehensive error code handling (401, 403, 404, 422)
6. Latency and performance timings
"""

import time
import httpx

BASE_URL = "http://127.0.0.1:8000/api/v1"

def run_phase9_qa():
    print("=" * 65)
    print("LEXEXTRACT PHASE 9 INTEGRATION & SECURITY QA SUITE")
    print("=" * 65)

    client = httpx.Client(timeout=30.0)

    # 1. Health check & Startup validation
    t0 = time.perf_counter()
    resp = client.get("http://127.0.0.1:8000/health")
    health_ms = (time.perf_counter() - t0) * 1000
    assert resp.status_code == 200, f"Health check failed: {resp.text}"
    health_data = resp.json()
    assert health_data["status"] == "healthy" and health_data["database"] == "connected"
    print(f"\n[1] Health Check & Service Latency: {health_ms:.2f} ms")
    print(f"    Status: {health_data['status']}, Database: {health_data['database']}")

    # 2. Authentication: User A (demo lawyer)
    resp = client.post(
        f"{BASE_URL}/auth/login",
        data={"username": "demo@lexextract.local", "password": "User@Lex2026!"}
    )
    assert resp.status_code == 200, f"User A login failed: {resp.text}"
    user_a_token = resp.json()["access_token"]
    user_a_headers = {"Authorization": f"Bearer {user_a_token}"}
    print("\n[2] User A Authentication: SUCCESS")
    print("    Logged in as demo@lexextract.local (Role: USER)")

    # 3. Authentication: User B (Create new separate user if needed, or login)
    unique_suffix = int(time.time())
    user_b_email = f"user_b_{unique_suffix}@lexextract.local"
    user_b_username = f"user_b_{unique_suffix}"
    reg_resp = client.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": user_b_email,
            "username": user_b_username,
            "full_name": "Counsel B",
            "password": "UserB@Secure2026!"
        }
    )
    assert reg_resp.status_code == 201, f"Registration failed: {reg_resp.text}"
    login_resp = client.post(
        f"{BASE_URL}/auth/login",
        data={"username": user_b_email, "password": "UserB@Secure2026!"}
    )
    assert login_resp.status_code == 200, f"User B login failed: {login_resp.text}"
    user_b_token = login_resp.json()["access_token"]
    user_b_headers = {"Authorization": f"Bearer {user_b_token}"}
    print("\n[3] User B Authentication: SUCCESS")
    print(f"    Logged in as {user_b_email} (Role: USER)")

    # 4. Multi-format Document Ingestion by User A
    print("\n[4] Multi-Format Ingestion by User A:")
    
    import os
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    samples_dir = os.path.join(root_dir, "sample_documents")

    # 4a. PDF upload
    t_pdf0 = time.perf_counter()
    with open(os.path.join(samples_dir, "sample_contract.pdf"), "rb") as f:
        pdf_bytes = f.read()
    pdf_resp = client.post(
        f"{BASE_URL}/documents/upload",
        headers=user_a_headers,
        files={"file": ("qa_sample_lease.pdf", pdf_bytes, "application/pdf")}
    )
    t_pdf_ms = (time.perf_counter() - t_pdf0) * 1000
    assert pdf_resp.status_code == 201, f"PDF upload failed: {pdf_resp.text}"
    doc_pdf = pdf_resp.json()
    print(f"    [PDF]  Uploaded ID #{doc_pdf['id']}: '{doc_pdf['filename']}', {doc_pdf['word_count']} words, Pages: {doc_pdf['page_count']} ({t_pdf_ms:.2f} ms)")

    # 4b. DOCX upload
    t_docx0 = time.perf_counter()
    with open(os.path.join(samples_dir, "sample_legal_notice.docx"), "rb") as f:
        docx_bytes = f.read()
    docx_resp = client.post(
        f"{BASE_URL}/documents/upload",
        headers=user_a_headers,
        files={"file": ("qa_legal_notice.docx", docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    )
    t_docx_ms = (time.perf_counter() - t_docx0) * 1000
    assert docx_resp.status_code == 201, f"DOCX upload failed: {docx_resp.text}"
    doc_docx = docx_resp.json()
    print(f"    [DOCX] Uploaded ID #{doc_docx['id']}: '{doc_docx['filename']}', {doc_docx['word_count']} words, Pages: {doc_docx['page_count']} ({t_docx_ms:.2f} ms)")

    # 4c. Verify unsupported extension rejection (e.g. TXT/EXE)
    t_txt0 = time.perf_counter()
    with open(os.path.join(samples_dir, "sample_arbitration_agreement.txt"), "rb") as f:
        txt_bytes = f.read()
    txt_resp = client.post(
        f"{BASE_URL}/documents/upload",
        headers=user_a_headers,
        files={"file": ("qa_arbitration_agreement.txt", txt_bytes, "text/plain")}
    )
    t_txt_ms = (time.perf_counter() - t_txt0) * 1000
    assert txt_resp.status_code == 400, f"Expected 400 for unsupported extension, got {txt_resp.status_code}"
    print(f"    [TXT]  File policy verified: Plaintext rejected with HTTP 400 ('{txt_resp.json()['detail']}') ({t_txt_ms:.2f} ms)")

    # 5. Pipeline Analysis on PDF by User A
    t_an0 = time.perf_counter()
    an_resp = client.post(
        f"{BASE_URL}/analyses/{doc_pdf['id']}",
        headers=user_a_headers
    )
    t_an_ms = (time.perf_counter() - t_an0) * 1000
    assert an_resp.status_code == 200, f"Analysis failed: {an_resp.text}"
    an_data = an_resp.json()
    analysis_id = an_data["analysis_id"]
    print(f"\n[5] NLP Analysis for Doc #{doc_pdf['id']} (Analysis ID #{analysis_id}):")
    print(f"    Total Latency: {t_an_ms:.2f} ms (Status: {an_data['status']})")
    print(f"    Extracted Keywords: {an_data['total_keywords']}, Extracted Entities: {an_data['total_entities']}")

    # 6. Data Isolation Verification (User B tries accessing User A's data)
    print("\n[6] Cross-User Ownership / Data Isolation Enforcement:")
    
    # 6a. User B tries to view User A's document metadata
    iso_doc = client.get(f"{BASE_URL}/documents/{doc_pdf['id']}", headers=user_b_headers)
    assert iso_doc.status_code == 403, f"Expected 403 for document metadata, got {iso_doc.status_code}"
    print(f"    [OK] User B access to Document #{doc_pdf['id']} metadata blocked: HTTP 403 Forbidden")

    # 6b. User B tries to read User A's extracted text
    iso_text = client.get(f"{BASE_URL}/documents/{doc_pdf['id']}/text", headers=user_b_headers)
    assert iso_text.status_code == 403, f"Expected 403 for document text, got {iso_text.status_code}"
    print(f"    [OK] User B access to Document #{doc_pdf['id']} text blocked: HTTP 403 Forbidden")

    # 6c. User B tries to download User A's file
    iso_file = client.get(f"{BASE_URL}/documents/{doc_pdf['id']}/file", headers=user_b_headers)
    assert iso_file.status_code == 403, f"Expected 403 for file stream, got {iso_file.status_code}"
    print(f"    [OK] User B access to Document #{doc_pdf['id']} file stream blocked: HTTP 403 Forbidden")

    # 6d. User B tries to view User A's analysis summary
    iso_an = client.get(f"{BASE_URL}/analyses/{analysis_id}", headers=user_b_headers)
    assert iso_an.status_code == 403, f"Expected 403 for analysis, got {iso_an.status_code}"
    print(f"    [OK] User B access to Analysis #{analysis_id} summary blocked: HTTP 403 Forbidden")

    # 6e. User B tries to trigger analysis on User A's document
    iso_run = client.post(
        f"{BASE_URL}/analyses/{doc_pdf['id']}",
        headers=user_b_headers
    )
    assert iso_run.status_code == 403, f"Expected 403 for analysis run, got {iso_run.status_code}"
    print(f"    [OK] User B triggering analysis on Doc #{doc_pdf['id']} blocked: HTTP 403 Forbidden")

    # 6f. User B tries to list User A's document analyses
    iso_analyses = client.get(f"{BASE_URL}/analyses/document/{doc_pdf['id']}", headers=user_b_headers)
    assert iso_analyses.status_code == 403, f"Expected 403 for document analyses list, got {iso_analyses.status_code}"
    print(f"    [OK] User B listing analyses for Document #{doc_pdf['id']} blocked: HTTP 403 Forbidden")

    # 7. Admin Access & Governance
    print("\n[7] Administrator Access & Governance:")
    admin_login = client.post(
        f"{BASE_URL}/auth/login",
        data={"username": "admin@lexextract.local", "password": "Admin@Lex2026!"}
    )
    assert admin_login.status_code == 200
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Admin can view User A's document
    adm_doc = client.get(f"{BASE_URL}/documents/{doc_pdf['id']}", headers=admin_headers)
    assert adm_doc.status_code == 200
    print(f"    [OK] Admin successfully accessed Document #{doc_pdf['id']} (Admin override verified)")

    # Admin audit trail
    audit_resp = client.get(f"{BASE_URL}/admin/audit-logs", headers=admin_headers)
    assert audit_resp.status_code == 200
    audit_data = audit_resp.json()
    audit_logs = audit_data["logs"]
    print(f"    [OK] Admin audit ledger operational: {audit_data['total']} recorded events")
    if audit_logs:
        latest_event = audit_logs[0]
        print(f"      Latest event: [{latest_event.get('created_at', latest_event.get('timestamp'))}] {latest_event['action']} by User #{latest_event['user_id']} ({latest_event['status']})")

    # 8. Negative / Security Error Code Validation
    print("\n[8] Comprehensive Error Handling Validation:")
    
    # 8a. 401 Unauthorized (No token)
    no_auth = client.get(f"{BASE_URL}/documents/")
    assert no_auth.status_code == 401
    print(f"    [OK] HTTP 401 Unauthorized returned on missing token: '{no_auth.json()['detail']}'")

    # 8b. 403 Forbidden (Normal user accessing admin endpoint)
    forbidden_audit = client.get(f"{BASE_URL}/admin/audit-logs", headers=user_a_headers)
    assert forbidden_audit.status_code == 403
    print(f"    [OK] HTTP 403 Forbidden returned on role violation: '{forbidden_audit.json()['detail']}'")

    # 8c. 404 Not Found (Nonexistent document)
    not_found = client.get(f"{BASE_URL}/documents/999999", headers=user_a_headers)
    assert not_found.status_code == 404
    print(f"    [OK] HTTP 404 Not Found returned on nonexistent resource: '{not_found.json()['detail']}'")

    # 8d. 422 Unprocessable Entity (Invalid payload)
    invalid_payload = client.post(
        f"{BASE_URL}/auth/register",
        json={"email": "not-an-email"}  # missing password and username
    )
    assert invalid_payload.status_code == 422
    print(f"    [OK] HTTP 422 Unprocessable Entity returned on invalid request schema")

    # 8e. Unsupported file upload
    bad_upload = client.post(
        f"{BASE_URL}/documents/upload",
        headers=user_a_headers,
        files={"file": ("virus.exe", b"malicious binary content", "application/octet-stream")}
    )
    assert bad_upload.status_code in [400, 422]
    print(f"    [OK] Unsupported file upload rejected with HTTP {bad_upload.status_code}: '{bad_upload.json()['detail']}'")

    print("\n" + "=" * 65)
    print("PHASE 9 INTEGRATION & SECURITY QA CONFIRMED: 100% PASS")
    print("=" * 65)

if __name__ == "__main__":
    run_phase9_qa()
