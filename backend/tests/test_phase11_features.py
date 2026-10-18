import json
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.core.database import Base, get_db
from app.core.security import hash_password, create_access_token
from app.models.user import User
from app.models.document import Document
from app.models.analysis import AnalysisRun
from app.models.keyword import ExtractedKeyword
from app.models.entity import ExtractedEntity
from app.services.clause_obligation_service import (
    extract_important_clauses,
    extract_obligations,
    extract_structured_facts,
    generate_document_insights,
    search_document_text,
    compare_two_documents,
    generate_analysis_report_json,
    generate_analysis_report_pdf,
    CLAUSE_DEFINITIONS
)
from main import app

test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()


def make_auth_header(user: User) -> dict:
    token = create_access_token({
        "sub": str(user.id),
        "email": user.email,
        "role": user.role
    })
    return {"Authorization": f"Bearer {token}"}


SAMPLE_LEGAL_CONTRACT = """COMMERCIAL SERVICES AND NON-DISCLOSURE AGREEMENT

This Agreement is entered into on this 1st day of June, 2024, between Acme Corporation ("Client") and Zenith Tech LLP ("Provider").

1. TERMINATION
Either party may terminate this Agreement by giving thirty (30) days prior written notice. Client may terminate immediately for cause upon written notice of termination.

2. CONFIDENTIALITY AND NON-DISCLOSURE
The Provider agrees to maintain strict confidentiality of all proprietary information and shall not disclose any trade secrets to third parties.

3. PAYMENT AND COMPENSATION
Client shall pay Provider a monthly fee of Rs. 1,50,000 within thirty (30) days of invoice date. In case of late payment, a penalty of Rs. 10,000 shall apply.

4. INDEMNIFICATION AND LIABILITY
Provider shall indemnify and hold harmless Client against any third-party claims or damages. In no event shall either party's aggregate liability exceed the total fees paid.

5. ARBITRATION AND GOVERNING LAW
All disputes shall be settled by arbitration before a sole arbitrator in New Delhi under the Arbitration and Conciliation Act, 1996. This Agreement shall be governed by and construed in accordance with the substantive laws of India.

6. NON-COMPETE
The Provider shall not engage in competing business during the term and for a period of one (1) year thereafter.

7. FORCE MAJEURE
Neither party shall be liable for delay or failure caused by acts of god, natural disasters, war, or pandemic.
"""


def test_clause_detection_categories():
    """Verify that important clause finder correctly detects clauses across categories."""
    clauses = extract_important_clauses(SAMPLE_LEGAL_CONTRACT)
    assert len(clauses) == 13
    
    found_types = {c["clause_type"] for c in clauses if c["status"] == "Found"}
    assert "Termination" in found_types
    assert "Confidentiality" in found_types
    assert "Payment / Compensation" in found_types
    assert "Liability" in found_types
    assert "Indemnification" in found_types
    assert "Arbitration / Dispute Resolution" in found_types
    assert "Governing Law" in found_types
    assert "Non-Compete / Restriction" in found_types
    assert "Force Majeure" in found_types

    # Renewal should not be found in this text
    renewal_clause = next(c for c in clauses if c["clause_type"] == "Renewal")
    assert renewal_clause["status"] == "Not Found"
    assert renewal_clause["confidence"] == 0.0


def test_obligation_extraction_modal_patterns():
    """Verify obligations extraction detects modal verbs, parties, and deadlines."""
    obs = extract_obligations(SAMPLE_LEGAL_CONTRACT)
    assert len(obs) > 0

    # Verify fields exist
    for ob in obs:
        assert "responsible_party" in ob
        assert "obligation" in ob
        assert "deadline" in ob
        assert "obligation_type" in ob
        assert "source_sentence" in ob

    # Verify detection of prohibition
    prohibitions = [o for o in obs if o["obligation_type"] == "Prohibition"]
    assert len(prohibitions) > 0


def test_structured_facts_dates_money_deadlines():
    """Verify extraction of dates, monetary sums, and durations with normalized values."""
    facts = extract_structured_facts(SAMPLE_LEGAL_CONTRACT)
    
    dates = facts["dates"]
    money = facts["money"]
    deadlines = facts["deadlines"]

    assert len(dates) > 0
    assert any("2024" in d["value"] for d in dates)

    assert len(money) > 0
    assert any("1,50,000" in m["value"] for m in money)

    assert len(deadlines) > 0
    assert any("30 days" in dl["value"] for dl in deadlines)


def test_document_insights_and_fallbacks():
    """Verify insights synthesis and fallback to 'Not detected' for missing values."""
    class DummyDoc:
        id = 1
        filename = "contract.pdf"
        extracted_text = SAMPLE_LEGAL_CONTRACT
        pages_json = None
        page_count = 2

    class DummyAnalysis:
        id = 1
        status = "completed"

    clauses = extract_important_clauses(SAMPLE_LEGAL_CONTRACT)
    obs = extract_obligations(SAMPLE_LEGAL_CONTRACT)
    facts = extract_structured_facts(SAMPLE_LEGAL_CONTRACT)

    insights = generate_document_insights(
        document=DummyDoc(),
        analysis_run=DummyAnalysis(),
        keywords=[],
        entities=[],
        clauses=clauses,
        obligations=obs,
        facts=facts
    )

    assert insights["document_name"] == "contract.pdf"
    assert "Agreement" in insights["document_type"] or insights["document_type"] != "Not detected"
    assert insights["detected_clauses_count"] >= 5
    assert len(insights["attention_areas"]) > 0
    assert insights["top_keywords"] == ["Not detected"]  # Since keywords was empty list


def test_in_document_search_relevance():
    """Verify document search returns match counts, offsets, and ASTMA TF-IDF ranking."""
    class DummyDoc:
        id = 1
        extracted_text = SAMPLE_LEGAL_CONTRACT
        pages_json = None

    search_res = search_document_text(DummyDoc(), "termination")
    assert search_res["total_matches"] >= 2
    assert len(search_res["matches"]) >= 2
    first_match = search_res["matches"][0]
    assert "snippet" in first_match
    assert first_match["score"] > 0.0

    # Non-existent query
    empty_res = search_document_text(DummyDoc(), "xyznonexistentstring123")
    assert empty_res["total_matches"] == 0
    assert empty_res["matches"] == []


def test_document_comparison_diff():
    """Verify document comparison calculates ASTMA TF-IDF cosine similarity and clause diffs."""
    contract_v2 = SAMPLE_LEGAL_CONTRACT.replace("Rs. 1,50,000", "Rs. 2,00,000").replace("thirty (30) days", "sixty (60) days")

    class DummyDocA:
        id = 1
        filename = "contract_v1.pdf"
        extracted_text = SAMPLE_LEGAL_CONTRACT
        pages_json = None
        word_count = 200
        page_count = 1
        file_type = "pdf"

    class DummyDocB:
        id = 2
        filename = "contract_v2.pdf"
        extracted_text = contract_v2
        pages_json = None
        word_count = 200
        page_count = 1
        file_type = "pdf"

    comp = compare_two_documents(DummyDocA(), None, DummyDocB(), None)
    assert comp["similarity_score"] > 0.85
    assert comp["similarity_percentage"] > 85.0
    assert comp["metadata_comparison"]["filename"]["match"] is False

    # Check clause comparison statuses
    clause_types = {c["clause_type"]: c["status"] for c in comp["clause_comparison"]}
    assert "Termination" in clause_types
    assert clause_types["Termination"] in ("MODIFIED", "UNCHANGED")


def test_report_export_pdf_and_json():
    """Verify PDF and JSON report generation include the mandatory legal disclaimer."""
    class DummyDoc:
        id = 1
        filename = "test_contract.pdf"
        file_type = "pdf"
        file_size = 5000
        word_count = 250
        page_count = 1
        uploaded_at = "2024-06-01"
        extracted_text = SAMPLE_LEGAL_CONTRACT
        pages_json = None

    class DummyAnalysis:
        id = 1
        status = "completed"
        processing_time = 0.45
        total_keywords = 5
        total_entities = 4
        started_at = "2024-06-01"
        completed_at = "2024-06-01"

    clauses = extract_important_clauses(SAMPLE_LEGAL_CONTRACT)
    obs = extract_obligations(SAMPLE_LEGAL_CONTRACT)
    facts = extract_structured_facts(SAMPLE_LEGAL_CONTRACT)
    insights = generate_document_insights(DummyDoc(), DummyAnalysis(), [], [], clauses, obs, facts)

    json_report = generate_analysis_report_json(
        DummyDoc(), DummyAnalysis(), [], [], clauses, obs, facts, insights
    )
    assert "system_disclaimer" in json_report
    assert "not provide legal advice" in json_report["system_disclaimer"].lower()

    pdf_bytes = generate_analysis_report_pdf(json_report)
    assert len(pdf_bytes) > 2000


# ========================================================
# End-to-End API Integration & RBAC Isolation Tests
# ========================================================

def test_phase11_api_endpoints_and_rbac(client, db_session):
    """
    Tests the 7 new endpoints through FastAPI client:
    - Verifies valid user can access insights, clauses, obligations, facts, search, compare, export
    - Verifies cross-user access returns HTTP 403
    """
    # Create two users: user A and user B
    user_a = User(
        name="User A",
        email="usera@lexextract.local",
        password_hash=hash_password("UserPass123!"),
        role="user",
        is_active=True
    )
    user_b = User(
        name="User B",
        email="userb@lexextract.local",
        password_hash=hash_password("UserPass123!"),
        role="user",
        is_active=True
    )
    db_session.add_all([user_a, user_b])
    db_session.commit()

    # User A document and analysis
    doc_a = Document(
        user_id=user_a.id,
        filename="usera_contract.pdf",
        stored_filename="stored_usera.pdf",
        file_type="pdf",
        file_size=2048,
        file_hash="hash_a",
        page_count=1,
        word_count=150,
        status="completed",
        extracted_text=SAMPLE_LEGAL_CONTRACT
    )
    db_session.add(doc_a)
    db_session.commit()

    analysis_a = AnalysisRun(
        document_id=doc_a.id,
        status="completed",
        total_keywords=2,
        total_entities=2
    )
    db_session.add(analysis_a)
    db_session.commit()

    kw1 = ExtractedKeyword(analysis_run_id=analysis_a.id, keyword="termination", final_score=0.9, category="contract", frequency=2, rank=1)
    db_session.add(kw1)
    db_session.commit()

    headers_a = make_auth_header(user_a)
    headers_b = make_auth_header(user_b)

    # 1. Insights Endpoint
    resp_insights = client.get(f"/api/v1/analyses/{analysis_a.id}/insights", headers=headers_a)
    assert resp_insights.status_code == 200
    ins_data = resp_insights.json()
    assert ins_data["document_name"] == "usera_contract.pdf"
    assert ins_data["detected_clauses_count"] >= 5

    # Cross-user access to insights -> 403
    assert client.get(f"/api/v1/analyses/{analysis_a.id}/insights", headers=headers_b).status_code == 403

    # 2. Clauses Endpoint
    resp_clauses = client.get(f"/api/v1/analyses/{analysis_a.id}/clauses", headers=headers_a)
    assert resp_clauses.status_code == 200
    cl_data = resp_clauses.json()
    assert cl_data["total_categories"] == 13
    assert cl_data["total_detected"] >= 5

    # Cross-user access to clauses -> 403
    assert client.get(f"/api/v1/analyses/{analysis_a.id}/clauses", headers=headers_b).status_code == 403

    # 3. Obligations Endpoint
    resp_obs = client.get(f"/api/v1/analyses/{analysis_a.id}/obligations", headers=headers_a)
    assert resp_obs.status_code == 200
    obs_data = resp_obs.json()
    assert obs_data["total"] >= 1

    # Cross-user access to obligations -> 403
    assert client.get(f"/api/v1/analyses/{analysis_a.id}/obligations", headers=headers_b).status_code == 403

    # 4. Facts Endpoint (Dates, Money, Deadlines)
    resp_facts = client.get(f"/api/v1/analyses/{analysis_a.id}/facts", headers=headers_a)
    assert resp_facts.status_code == 200
    facts_data = resp_facts.json()
    assert len(facts_data["dates"]) > 0
    assert len(facts_data["money"]) > 0

    # Cross-user access to facts -> 403
    assert client.get(f"/api/v1/analyses/{analysis_a.id}/facts", headers=headers_b).status_code == 403

    # 5. In-Document Search Endpoint
    resp_search = client.get(f"/api/v1/documents/{doc_a.id}/search?q=arbitration", headers=headers_a)
    assert resp_search.status_code == 200
    s_data = resp_search.json()
    assert s_data["total_matches"] >= 1

    # Cross-user search access -> 403
    assert client.get(f"/api/v1/documents/{doc_a.id}/search?q=arbitration", headers=headers_b).status_code == 403

    # 6. Document Comparison Endpoint
    # Create Doc A2 also belonging to user A
    doc_a2 = Document(
        user_id=user_a.id,
        filename="usera_contract_v2.pdf",
        stored_filename="stored_usera2.pdf",
        file_type="pdf",
        file_size=2048,
        file_hash="hash_a2",
        page_count=1,
        word_count=160,
        status="completed",
        extracted_text=SAMPLE_LEGAL_CONTRACT + "\nAdditional clause."
    )
    db_session.add(doc_a2)
    db_session.commit()

    resp_comp = client.post(
        "/api/v1/documents/compare",
        json={"doc_a_id": doc_a.id, "doc_b_id": doc_a2.id},
        headers=headers_a
    )
    assert resp_comp.status_code == 200
    comp_data = resp_comp.json()
    assert comp_data["similarity_score"] > 0.80

    # User B attempting to compare User A's documents -> 403
    resp_comp_cross = client.post(
        "/api/v1/documents/compare",
        json={"doc_a_id": doc_a.id, "doc_b_id": doc_a2.id},
        headers=headers_b
    )
    assert resp_comp_cross.status_code == 403

    # 7. Export Analysis Report (JSON & PDF)
    resp_exp_json = client.get(f"/api/v1/analyses/{analysis_a.id}/export?format=json", headers=headers_a)
    assert resp_exp_json.status_code == 200
    assert "system_disclaimer" in resp_exp_json.json()

    resp_exp_pdf = client.get(f"/api/v1/analyses/{analysis_a.id}/export?format=pdf", headers=headers_a)
    assert resp_exp_pdf.status_code == 200
    assert resp_exp_pdf.headers["content-type"] == "application/pdf"
    assert len(resp_exp_pdf.content) > 1000

    # Cross-user export -> 403
    assert client.get(f"/api/v1/analyses/{analysis_a.id}/export?format=pdf", headers=headers_b).status_code == 403
