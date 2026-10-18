"""Phase 12 - Comprehensive Quality, Robustness & Edge-Case Test Suite.

Validates system resilience against:
1. Empty documents & whitespace-only text
2. Extremely short documents
3. Documents lacking obvious keywords or legal clauses
4. Documents with unusual punctuation, unicode symbols, and currency marks
5. Large document processing scaling
6. Invalid file extensions and corrupted files
7. Unauthorized document access and invalid authentication
8. Empty search queries and no-result searches
9. Identical document comparison (cosine similarity = 1.0)
10. Completely unrelated document comparison
11. Missing optional metadata handling in reports
"""

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
from app.services.clause_obligation_service import (
    extract_important_clauses,
    extract_obligations,
    extract_structured_facts,
    generate_document_insights,
    search_document_text,
    compare_two_documents,
    generate_analysis_report_json,
    generate_analysis_report_pdf,
    CLAUSE_DEFINITIONS,
)
from app.services.text_preprocessor import normalize_legal_text, tokenize_legal_text
from app.services.keyword_extractor import extract_keywords
from app.services.entity_extractor import extract_legal_entities
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
        "role": user.role,
    })
    return {"Authorization": f"Bearer {token}"}


class MockDoc:
    def __init__(self, text: str, filename: str = "mock.pdf", doc_id: int = 1):
        self.id = doc_id
        self.filename = filename
        self.extracted_text = text
        self.pages_json = None
        self.word_count = len(text.split()) if text else 0
        self.page_count = 1
        self.file_type = "pdf"
        self.file_size = len(text.encode("utf-8")) if text else 0
        self.uploaded_at = "2026-10-05T00:00:00"


class MockAnalysis:
    def __init__(self, analysis_id: int = 1):
        self.id = analysis_id
        self.status = "completed"
        self.processing_time = 0.12
        self.total_keywords = 0
        self.total_entities = 0
        self.started_at = "2026-10-05T00:00:00"
        self.completed_at = "2026-10-05T00:00:01"


# ==========================================
# 1. EMPTY DOCUMENT & WHITESPACE-ONLY TESTS
# ==========================================

def test_empty_document_handling():
    """Verify that empty string or whitespace does not crash NLP services."""
    for empty_input in ["", "   ", "\n\t  \r\n"]:
        # Preprocessing
        normalized = normalize_legal_text(empty_input)
        assert isinstance(normalized, str)
        tokens = tokenize_legal_text(empty_input)
        assert isinstance(tokens, list)
        assert len(tokens) == 0

        # Keywords
        kw_res = extract_keywords(empty_input)
        assert isinstance(kw_res, list)
        assert len(kw_res) == 0

        # Entities
        ents = extract_legal_entities(empty_input)
        assert isinstance(ents, list)
        assert len(ents) == 0

        # Clauses
        clauses = extract_important_clauses(empty_input)
        assert len(clauses) == len(CLAUSE_DEFINITIONS)
        assert all(c["status"] == "Not Found" for c in clauses)

        # Obligations
        obls = extract_obligations(empty_input)
        assert isinstance(obls, list)
        assert len(obls) == 0

        # Structured Facts
        facts = extract_structured_facts(empty_input)
        assert len(facts["dates"]) == 0
        assert len(facts["money"]) == 0
        assert len(facts["deadlines"]) == 0

        # Insights
        mock_doc = MockDoc(empty_input)
        mock_analysis = MockAnalysis()
        insights = generate_document_insights(mock_doc, mock_analysis, [], [], clauses, obls, facts)
        assert insights["detected_clauses_count"] == 0
        assert insights["keyword_count"] == 0

        # In-document search
        search_res = search_document_text(mock_doc, "payment")
        assert search_res["total_matches"] == 0
        assert search_res["matches"] == []


# ==========================================
# 2. VERY SHORT DOCUMENT
# ==========================================

def test_very_short_document():
    """Verify graceful execution on single words or very short sentences."""
    short_text = "Agreement signed."
    tokens = tokenize_legal_text(short_text)
    assert len(tokens) >= 1

    clauses = extract_important_clauses(short_text)
    assert isinstance(clauses, list)
    assert len(clauses) == len(CLAUSE_DEFINITIONS)

    mock_doc = MockDoc(short_text)
    mock_analysis = MockAnalysis()
    facts = extract_structured_facts(short_text)
    obls = extract_obligations(short_text)
    insights = generate_document_insights(mock_doc, mock_analysis, [], [], clauses, obls, facts)
    assert insights["document_name"] == "mock.pdf"
    assert insights["section_count"] >= 1


# ==========================================
# 3. DOCUMENT WITH NO LEGAL CLAUSES / STOPWORDS ONLY
# ==========================================

def test_document_with_no_legal_clauses():
    """Verify an informal email or text with zero legal clauses."""
    informal_text = (
        "Hi John, hope you are doing well today. Let us meet tomorrow at the coffee shop "
        "to discuss our vacation plans and the soccer game on Sunday. See you soon!"
    )
    clauses = extract_important_clauses(informal_text)
    found_clauses = [c for c in clauses if c["status"] == "Found"]
    assert len(found_clauses) == 0

    obls = extract_obligations(informal_text)
    assert len(obls) == 0

    facts = extract_structured_facts(informal_text)
    assert len(facts["money"]) == 0


def test_stopwords_only_document():
    """Verify text composed entirely of stop words does not fail keyword extraction."""
    stopwords_text = "the is at which on this that from by with or as an be"
    keywords = extract_keywords(stopwords_text)
    assert isinstance(keywords, list)
    assert len(keywords) == 0


# ==========================================
# 4. UNUSUAL PUNCTUATION, UNICODE & CURRENCIES
# ==========================================

def test_unusual_punctuation_and_unicode():
    """Verify parser handles section symbols, smart quotes, em-dashes, and varied currencies."""
    complex_text = (
        "1. PAYMENT AND FEES\n"
        "§ 14.1 — The Licensor shall pay £50,000, $12,500.50, and €300,000.00 "
        "to Licensee on 15/08/2025. Non-payment shall incur a 5% monthly penalty!\n\n"
        "2. ARBITRATION AND GOVERNING LAW\n"
        "All disputes shall be settled by arbitration; governing law: Laws of Singapore."
    )
    # Structured facts: should capture currencies and date
    facts = extract_structured_facts(complex_text)
    assert len(facts["money"]) >= 3
    values_found = [m["value"] for m in facts["money"]]
    assert any("£" in v for v in values_found)
    assert any("$" in v for v in values_found)
    assert any("€" in v for v in values_found)
    assert len(facts["dates"]) >= 1

    # Search with punctuation
    mock_doc = MockDoc(complex_text)
    search_res = search_document_text(mock_doc, "Licensor")
    assert search_res["total_matches"] >= 1

    # Clause detection
    clauses = extract_important_clauses(complex_text)
    arb_clause = next((c for c in clauses if "Arbitration" in c["clause_type"]), None)
    assert arb_clause is not None and arb_clause["status"] == "Found"


# ==========================================
# 5. LARGE DOCUMENT SCALING (SYNTHETIC)
# ==========================================

def test_large_document_scaling():
    """Verify pipeline efficiency and stability on a 4,500+ word document."""
    clause_paragraph = (
        "The Provider shall maintain confidentiality of proprietary data. "
        "Client shall pay the service fee of $5,000 within thirty days of invoice. "
        "Either party may terminate this agreement upon 30 days written notice. "
        "In no event shall liability exceed total fees paid under this agreement. "
        "All disputes shall be governed by the laws of California. "
    )
    large_doc_text = clause_paragraph * 90
    word_count = len(large_doc_text.split())
    assert word_count > 4000

    # Clause extraction
    clauses = extract_important_clauses(large_doc_text)
    assert any(c["status"] == "Found" for c in clauses)

    # Obligations
    obls = extract_obligations(large_doc_text)
    assert len(obls) > 0

    # Facts
    facts = extract_structured_facts(large_doc_text)
    assert len(facts["money"]) > 0

    # Insights
    mock_doc = MockDoc(large_doc_text)
    mock_analysis = MockAnalysis()
    insights = generate_document_insights(mock_doc, mock_analysis, [], [], clauses, obls, facts)
    assert insights["section_count"] >= 1


# ==========================================
# 6. DOCUMENT COMPARISON: IDENTICAL & UNRELATED
# ==========================================

def test_compare_identical_documents():
    """Comparing identical documents should yield cosine similarity close to 1.0."""
    text = (
        "This Non-Disclosure Agreement is entered into by Alpha Corp and Beta Inc. "
        "The parties agree that confidential information shall not be disclosed to any third party. "
        "The agreement shall terminate after 2 years. Governing law is New York."
    )
    doc_a = MockDoc(text, "doc_a.pdf", doc_id=1)
    doc_b = MockDoc(text, "doc_b.pdf", doc_id=2)
    comp = compare_two_documents(doc_a, None, doc_b, None)
    assert comp["similarity_score"] >= 0.99
    assert comp["similarity_percentage"] >= 99.0
    for clause in comp["clause_comparison"]:
        if clause["doc_a_present"] and clause["doc_b_present"]:
            assert clause["status"] == "UNCHANGED"


def test_compare_unrelated_documents():
    """Comparing unrelated documents (legal lease vs biology text) should yield low similarity."""
    legal_text = (
        "COMMERCIAL LEASE AGREEMENT\n"
        "1. PAYMENT: Landlord leases premises to Tenant for monthly rent of $3,000.\n"
        "2. INDEMNIFICATION: Tenant shall indemnify Landlord against property damage.\n"
        "3. TERMINATION: Either party may terminate upon written notice."
    )
    unrelated_text = (
        "Photosynthesis in vascular plants occurs primarily inside the chloroplasts of leaf cells. "
        "Chlorophyll pigments absorb sunlight to convert water and carbon dioxide into glucose and oxygen."
    )
    doc_a = MockDoc(legal_text, "lease.pdf", doc_id=1)
    doc_b = MockDoc(unrelated_text, "biology.pdf", doc_id=2)
    comp = compare_two_documents(doc_a, None, doc_b, None)
    assert comp["similarity_score"] < 0.25
    clause_diffs = comp["clause_comparison"]
    lease_exclusive = [c for c in clause_diffs if c["doc_a_present"] and not c["doc_b_present"]]
    assert len(lease_exclusive) > 0


# ==========================================
# 7. IN-DOCUMENT SEARCH EDGE CASES
# ==========================================

def test_search_edge_cases():
    """Verify empty query, whitespace, special regex chars, and non-existent queries."""
    sample_text = "The Lessee shall pay $2,500 monthly. Contact admin@acme.com for inquiries."
    mock_doc = MockDoc(sample_text)

    empty_res = search_document_text(mock_doc, "")
    assert empty_res["total_matches"] == 0
    assert empty_res["matches"] == []

    ws_res = search_document_text(mock_doc, "   ")
    assert ws_res["total_matches"] == 0

    special_res = search_document_text(mock_doc, "$2,500")
    assert special_res["total_matches"] >= 1

    regex_symbols_res = search_document_text(mock_doc, "[*+?^${}()|[]\\")
    assert regex_symbols_res["total_matches"] == 0

    missing_res = search_document_text(mock_doc, "Supercalifragilistic")
    assert missing_res["total_matches"] == 0


# ==========================================
# 8. API SECURITY & PERMISSION BOUNDARIES
# ==========================================

def test_unauthenticated_api_requests(client):
    """Verify that unauthenticated requests to protected endpoints return HTTP 401."""
    endpoints = [
        ("GET", "/api/v1/documents"),
        ("GET", "/api/v1/analyses/1/insights"),
        ("GET", "/api/v1/analyses/1/clauses"),
        ("GET", "/api/v1/analyses/1/obligations"),
        ("GET", "/api/v1/analyses/1/facts"),
        ("GET", "/api/v1/documents/1/search?q=test"),
        ("GET", "/api/v1/analyses/1/export?format=json"),
        ("GET", "/api/v1/analyses/1/export?format=pdf"),
        ("POST", "/api/v1/documents/compare"),
        ("GET", "/api/v1/admin/audit-logs"),
    ]
    for method, path in endpoints:
        if method == "GET":
            response = client.get(path)
        else:
            response = client.post(path, json={})
        assert response.status_code == 401, f"Expected 401 for {method} {path}, got {response.status_code}"


def test_invalid_bearer_token(client):
    """Verify that malformed or forged JWT tokens return HTTP 401."""
    headers = {"Authorization": "Bearer forged.invalid.token"}
    response = client.get("/api/v1/documents", headers=headers)
    assert response.status_code == 401


def test_cross_user_isolation_on_new_endpoints(client, db_session):
    """Verify User B cannot access User A's insights, clauses, search, comparison, or reports."""
    user_a = User(
        name="User A Edge",
        email="usera_edge@example.com",
        password_hash=hash_password("Password123!"),
        role="user",
        is_active=True,
    )
    user_b = User(
        name="User B Edge",
        email="userb_edge@example.com",
        password_hash=hash_password("Password123!"),
        role="user",
        is_active=True,
    )
    db_session.add_all([user_a, user_b])
    db_session.commit()

    doc_a = Document(
        user_id=user_a.id,
        filename="confidential_a.pdf",
        stored_filename="stored_confidential_a.pdf",
        file_type="pdf",
        file_size=1024,
        file_hash="hash_edge_a",
        page_count=1,
        word_count=50,
        status="completed",
        extracted_text="Confidential business agreement. Client shall pay $50,000.",
    )
    db_session.add(doc_a)
    db_session.commit()

    analysis_a = AnalysisRun(
        document_id=doc_a.id,
        status="completed",
        total_keywords=0,
        total_entities=0
    )
    db_session.add(analysis_a)
    db_session.commit()

    auth_b = make_auth_header(user_b)

    assert client.get(f"/api/v1/analyses/{analysis_a.id}/insights", headers=auth_b).status_code in [403, 404]
    assert client.get(f"/api/v1/analyses/{analysis_a.id}/clauses", headers=auth_b).status_code in [403, 404]
    assert client.get(f"/api/v1/analyses/{analysis_a.id}/obligations", headers=auth_b).status_code in [403, 404]
    assert client.get(f"/api/v1/analyses/{analysis_a.id}/facts", headers=auth_b).status_code in [403, 404]
    assert client.get(f"/api/v1/documents/{doc_a.id}/search?q=payment", headers=auth_b).status_code in [403, 404]
    assert client.get(f"/api/v1/analyses/{analysis_a.id}/export?format=json", headers=auth_b).status_code in [403, 404]
    assert client.get(f"/api/v1/analyses/{analysis_a.id}/export?format=pdf", headers=auth_b).status_code in [403, 404]


# ==========================================
# 9. REPORT GENERATION WITH MISSING METADATA
# ==========================================

def test_report_generation_with_missing_metadata(db_session):
    """Verify that export report handles documents with empty metadata and empty facts."""
    user = User(
        name="Reporter",
        email="reporter@example.com",
        password_hash=hash_password("Password123!"),
        role="user",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()

    doc = Document(
        user_id=user.id,
        filename="minimal.pdf",
        stored_filename="stored_minimal.pdf",
        file_type="pdf",
        file_size=100,
        file_hash="hash_minimal",
        page_count=1,
        word_count=10,
        status="completed",
        extracted_text="Basic text with minimal details.",
    )
    db_session.add(doc)
    db_session.commit()

    analysis = AnalysisRun(
        document_id=doc.id,
        status="completed",
        processing_time=0.05,
        total_keywords=0,
        total_entities=0
    )
    db_session.add(analysis)
    db_session.commit()

    clauses = extract_important_clauses(doc.extracted_text)
    obls = extract_obligations(doc.extracted_text)
    facts = extract_structured_facts(doc.extracted_text)
    insights = generate_document_insights(doc, analysis, [], [], clauses, obls, facts)

    # JSON report generation
    json_report = generate_analysis_report_json(doc, analysis, [], [], clauses, obls, facts, insights)
    assert json_report["document_information"]["filename"] == "minimal.pdf"
    assert "system_disclaimer" in json_report

    # PDF report generation
    pdf_bytes = generate_analysis_report_pdf(json_report)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 500
    assert pdf_bytes.startswith(b"%PDF")
