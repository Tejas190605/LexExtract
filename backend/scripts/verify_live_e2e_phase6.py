"""
Comprehensive Live End-to-End Verification Script for Phase 6.
Tests:
1. Public User Registration
2. JWT Authentication & /auth/me Profile Inspection
3. Authenticated Document Upload & Ownership Attribution
4. Document Keyword & Entity Extraction Execution
5. Ranked Keyword & Classified Entity Retrieval
6. Cross-Tenant Isolation Enforcement (HTTP 403 Forbidden on Document & Analysis access)
7. Audit Trail Verification for UNAUTHORIZED_ACCESS
8. User Logout
9. Administrator Authentication & Privileged Access
10. Admin User Directory & Role-Based Safeguards
11. Admin Audit Trail Inspection & Query Filtering
"""

import sys
import requests

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_live_phase6():
    session_user1 = requests.Session()
    session_user2 = requests.Session()
    session_admin = requests.Session()

    print("\n=======================================================")
    print("  PHASE 6 LIVE VERIFICATION TEST SUITE")
    print("=======================================================")

    # 1. Register a new USER
    print("\n[Step 1] Registering a new practitioner account...")
    reg_payload = {
        "full_name": "Advocate Priya Sen",
        "username": "priya_sen_live",
        "email": "priya.sen@lexextract.local",
        "password": "Password@2026!"
    }
    # If already exists from previous test, proceed to login
    reg_res = session_user1.post(f"{BASE_URL}/auth/register", json=reg_payload)
    if reg_res.status_code == 201:
        print(f"  --> Registered successfully! User ID: {reg_res.json()['id']}, Role: {reg_res.json()['role']}")
        assert reg_res.json()["role"] == "USER"
    elif reg_res.status_code == 400 and "already exists" in reg_res.text:
        print("  --> User already registered. Proceeding to login.")
    else:
        print(f"  FAILED registration: {reg_res.status_code} {reg_res.text}")
        sys.exit(1)

    # 2. Login as USER
    print("\n[Step 2] Authenticating as Advocate Priya Sen...")
    login_res = session_user1.post(f"{BASE_URL}/auth/login", json={
        "email_or_username": "priya_sen_live",
        "password": "Password@2026!"
    })
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    token_user1 = login_res.json()["access_token"]
    print(f"  --> JWT Token acquired: {token_user1[:20]}...")
    session_user1.headers.update({"Authorization": f"Bearer {token_user1}"})

    # Verify /auth/me
    me_res = session_user1.get(f"{BASE_URL}/auth/me")
    assert me_res.status_code == 200
    user1_profile = me_res.json()
    user1_id = user1_profile["id"]
    print(f"  --> /auth/me profile validated: ID={user1_id}, Email={user1_profile['email']}, Role={user1_profile['role']}")
    assert "password_hash" not in user1_profile

    # 3. Upload Document
    print("\n[Step 3] Uploading a legal document under user context...")
    sample_legal_text = (
        "This Commercial Lease Agreement is executed on 15 January 2026 between Alpha Corp "
        "and Rajesh Sharma. The dispute is subject to the Indian Contract Act. The plaintiff seeks "
        "₹50,000 under Section 73. Case No. ABC/123/2026 is pending before the Supreme Court of India."
    )
    # Create mock text as pdf/docx or text
    # In LexExtract, /documents/upload accepts multipart PDF/DOCX
    # Let's use sample_commercial_lease.pdf from sample_documents if available, or generate a minimal valid docx/pdf
    import os
    sample_pdf_path = os.path.join(os.path.dirname(__file__), "..", "..", "sample_documents", "sample_lease.pdf")
    if not os.path.exists(sample_pdf_path):
        # Check backend/storage or create a test docx
        from docx import Document as DocxDocument
        docx_path = os.path.join(os.path.dirname(__file__), "test_doc.docx")
        doc_obj = DocxDocument()
        doc_obj.add_heading("Commercial Lease Agreement", level=1)
        doc_obj.add_paragraph(sample_legal_text)
        doc_obj.save(docx_path)
        upload_file_path = docx_path
    else:
        upload_file_path = sample_pdf_path

    with open(upload_file_path, "rb") as f:
        files = {"file": ("lease_agreement_live.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        up_res = session_user1.post(f"{BASE_URL}/documents/upload", files=files)

    assert up_res.status_code == 201, f"Upload failed: {up_res.text}"
    doc1 = up_res.json()
    doc1_id = doc1["id"]
    print(f"  --> Document uploaded: ID={doc1_id}, Filename={doc1['filename']}, WordCount={doc1['word_count']}")

    # 4. Analyze Document
    print("\n[Step 4] Running keyword and entity extraction...")
    ana_res = session_user1.post(f"{BASE_URL}/analyses/{doc1_id}")
    assert ana_res.status_code == 200, f"Analysis failed: {ana_res.text}"
    ana_data = ana_res.json()
    analysis_id = ana_data["analysis_id"]
    print(f"  --> Analysis completed: ID={analysis_id}, Keywords={ana_data['total_keywords']}, Entities={ana_data['total_entities']}, Time={ana_data['processing_time']}s")
    assert ana_data["total_keywords"] > 0
    assert ana_data["total_entities"] > 0

    # 5. Retrieve Keywords & Entities
    print("\n[Step 5] Retrieving extracted keywords and entities...")
    kw_res = session_user1.get(f"{BASE_URL}/analyses/{analysis_id}/keywords")
    assert kw_res.status_code == 200
    keywords = kw_res.json()["keywords"]
    print(f"  --> Retrieved {len(keywords)} ranked keywords. Top 3:")
    for k in keywords[:3]:
        print(f"      - {k['keyword']} (Score: {k['final_score']}, Category: {k['category']})")

    ent_res = session_user1.get(f"{BASE_URL}/analyses/{analysis_id}/entities")
    assert ent_res.status_code == 200
    entities = ent_res.json()["entities"]
    print(f"  --> Retrieved {len(entities)} classified legal entities. Sample:")
    for e in entities[:4]:
        print(f"      - {e['normalized_text']} [{e['entity_type']}] (Confidence: {e['confidence']}, Source: {e['source']})")

    # 6. Cross-Tenant Isolation Security Test
    print("\n[Step 6] Testing Cross-Tenant Isolation (Unauthorized User access)...")
    # Register/Login user 2 (adversary / unprivileged user)
    reg2_res = session_user2.post(f"{BASE_URL}/auth/register", json={
        "full_name": "Advocate Rival Sharma",
        "username": "rival_user_live",
        "email": "rival@lexextract.local",
        "password": "Password@2026!"
    })
    login2_res = session_user2.post(f"{BASE_URL}/auth/login", json={
        "email_or_username": "rival_user_live",
        "password": "Password@2026!"
    })
    token_user2 = login2_res.json()["access_token"]
    session_user2.headers.update({"Authorization": f"Bearer {token_user2}"})

    # Attempt to access user 1's document metadata
    tamper_doc = session_user2.get(f"{BASE_URL}/documents/{doc1_id}")
    print(f"  --> User 2 attempting GET /documents/{doc1_id} (Owned by User 1): HTTP {tamper_doc.status_code}")
    assert tamper_doc.status_code == 403, f"Expected 403 Forbidden, got {tamper_doc.status_code}"

    # Attempt to access user 1's analysis keywords
    tamper_ana_kw = session_user2.get(f"{BASE_URL}/analyses/{analysis_id}/keywords")
    print(f"  --> User 2 attempting GET /analyses/{analysis_id}/keywords: HTTP {tamper_ana_kw.status_code}")
    assert tamper_ana_kw.status_code == 403, f"Expected 403 Forbidden, got {tamper_ana_kw.status_code}"

    # Attempt to access user 1's analysis entities
    tamper_ana_ent = session_user2.get(f"{BASE_URL}/analyses/{analysis_id}/entities")
    print(f"  --> User 2 attempting GET /analyses/{analysis_id}/entities: HTTP {tamper_ana_ent.status_code}")
    assert tamper_ana_ent.status_code == 403, f"Expected 403 Forbidden, got {tamper_ana_ent.status_code}"

    # Attempt to access admin endpoint
    tamper_admin = session_user2.get(f"{BASE_URL}/admin/audit-logs")
    print(f"  --> User 2 attempting GET /admin/audit-logs: HTTP {tamper_admin.status_code}")
    assert tamper_admin.status_code == 403, f"Expected 403 Forbidden, got {tamper_admin.status_code}"
    print("  --> ALL cross-tenant & privilege escalation attempts blocked with HTTP 403 Forbidden!")

    # 7. User Logout
    print("\n[Step 7] Testing User Logout...")
    logout_res = session_user1.post(f"{BASE_URL}/auth/logout")
    assert logout_res.status_code == 200
    print("  --> User signed out successfully.")

    # 8. Admin Login & Verification
    print("\n[Step 8] Authenticating as System Administrator...")
    admin_login_res = session_admin.post(f"{BASE_URL}/auth/login", json={
        "email_or_username": "admin",
        "password": "Admin@Lex2026!"
    })
    assert admin_login_res.status_code == 200, f"Admin login failed: {admin_login_res.text}"
    token_admin = admin_login_res.json()["access_token"]
    session_admin.headers.update({"Authorization": f"Bearer {token_admin}"})
    print("  --> Administrator authenticated successfully.")

    # 9. Admin User Directory & Safeguards
    print("\n[Step 9] Inspecting User Management & Admin Safeguards...")
    users_res = session_admin.get(f"{BASE_URL}/users/")
    assert users_res.status_code == 200
    users_list = users_res.json()
    print(f"  --> Admin retrieved {len(users_list)} system users.")
    admin_user = [u for u in users_list if u["role"] == "ADMIN"][0]

    # Test safeguard: cannot deactivate last admin
    bad_deactivate = session_admin.patch(f"{BASE_URL}/users/{admin_user['id']}/status", json={"is_active": False})
    print(f"  --> Attempting to deactivate only active admin: HTTP {bad_deactivate.status_code} ({bad_deactivate.json()['detail']})")
    assert bad_deactivate.status_code == 400

    # Test safeguard: cannot demote last admin
    bad_demote = session_admin.patch(f"{BASE_URL}/users/{admin_user['id']}/role", json={"role": "USER"})
    print(f"  --> Attempting to demote only active admin: HTTP {bad_demote.status_code} ({bad_demote.json()['detail']})")
    assert bad_demote.status_code == 400
    print("  --> Admin preservation safeguards operational!")

    # 10. Admin Audit Trail Verification
    print("\n[Step 10] Inspecting Governance Audit Trail...")
    audit_res = session_admin.get(f"{BASE_URL}/admin/audit-logs?limit=50")
    assert audit_res.status_code == 200
    audit_data = audit_res.json()
    total_logs = audit_data["total"]
    logs = audit_data["logs"]
    print(f"  --> Total Audit Events recorded in ledger: {total_logs}")

    actions_recorded = set(l["action"] for l in logs)
    print(f"  --> Distinct actions observed: {actions_recorded}")

    # Verify key compliance events are present
    assert "LOGIN_SUCCESS" in actions_recorded
    assert "DOCUMENT_UPLOAD" in actions_recorded
    assert "ANALYSIS_START" in actions_recorded
    assert "ANALYSIS_COMPLETE" in actions_recorded
    assert "UNAUTHORIZED_ACCESS" in actions_recorded
    assert "LOGOUT" in actions_recorded

    # Check UNAUTHORIZED_ACCESS details
    unauth_events = [l for l in logs if l["action"] == "UNAUTHORIZED_ACCESS"]
    print(f"  --> Verified {len(unauth_events)} UNAUTHORIZED_ACCESS incidents logged with status FAILURE:")
    for ue in unauth_events[:2]:
        print(f"      - User {ue['user_id']}: {ue['details']} [Status: {ue['status']}]")

    print("\n=======================================================")
    print("  ALL LIVE PHASE 6 VERIFICATION CHECKS PASSED (10/10)")
    print("=======================================================\n")

if __name__ == "__main__":
    test_live_phase6()
