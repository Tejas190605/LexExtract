import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db, init_db
from main import app
from app.models.user import User
from app.models.document import Document
from app.models.analysis import AnalysisRun
from app.models.entity import ExtractedEntity
from app.services.spacy_service import extract_spacy_entities, is_spacy_available
from app.services.legal_entity_rules import extract_regex_and_gazetteer_entities
from app.services.entity_normalizer import normalize_entity_text, normalize_entity_record
from app.services.entity_deduplicator import deduplicate_and_merge_entities
from app.services.entity_extractor import extract_legal_entities

# ---------------------------------------------------------------------------
# Test Database Setup
# ---------------------------------------------------------------------------
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    init_db(target_engine=engine)
    session = TestingSessionLocal()

    # Seed test lawyer user
    test_user = User(
        name="Advocate Test",
        email="advocate@lexextract.local",
        password_hash="testpasshash5",
        role="user",
        is_active=True
    )
    session.add(test_user)
    session.commit()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    def override_get_current_user():
        from app.core.deps import get_current_user
        user = db_session.query(User).first()
        if not user:
            user = User(username="test_lawyer", email="lawyer@test.local", full_name="Lawyer", password_hash="h", role="USER")
            db_session.add(user)
            db_session.commit()
        return user

    from app.core.deps import get_current_user
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# ===========================================================================
# 1. Unit Tests
# ===========================================================================

def test_spacy_service_initialization_and_entities():
    # If spaCy is available, verify it extracts entities
    assert is_spacy_available() is True
    text = "John Smith visited London on 12 May 2024 to negotiate with Acme Corp."
    ents = extract_spacy_entities(text)
    types_found = {e["entity_type"] for e in ents}

    assert "PERSON" in types_found
    assert "LOCATION" in types_found or "ORGANIZATION" in types_found
    assert "DATE" in types_found


def test_section_extraction():
    text = "The charge was framed under Section 302 and Sec. 138 of the statute."
    ents = extract_regex_and_gazetteer_entities(text)
    sections = [e for e in ents if e["entity_type"] == "SECTION"]
    section_texts = [s["text"] for s in sections]

    assert any("Section 302" in st for st in section_texts)
    assert any("Sec. 138" in st for st in section_texts)


def test_article_extraction():
    text = "The petitioner claims violation of fundamental rights under Article 14 and Art. 21."
    ents = extract_regex_and_gazetteer_entities(text)
    articles = [e for e in ents if e["entity_type"] == "ARTICLE"]
    article_texts = [a["text"] for a in articles]

    assert any("Article 14" in at for at in article_texts)
    assert any("Art. 21" in at for at in article_texts)


def test_act_and_law_extraction():
    text = "The agreement is enforceable under the Indian Contract Act and the Code of Civil Procedure."
    ents = extract_regex_and_gazetteer_entities(text)
    acts = [e for e in ents if e["entity_type"] in ("ACT", "LAW")]
    act_texts = [a["text"] for a in acts]

    assert "Indian Contract Act" in act_texts
    assert "Code of Civil Procedure" in act_texts


def test_court_extraction():
    text = "The appeal was presented before the Supreme Court of India and subsequently the High Court."
    ents = extract_regex_and_gazetteer_entities(text)
    courts = [e for e in ents if e["entity_type"] == "COURT"]
    court_texts = [c["text"] for c in courts]

    assert "Supreme Court of India" in court_texts
    assert "High Court" in court_texts


def test_case_reference_extraction():
    text = "The registry listed Case No. ABC/123/2026 and Petition No. 45/2025 for urgent hearing."
    ents = extract_regex_and_gazetteer_entities(text)
    cases = [e for e in ents if e["entity_type"] == "CASE_REFERENCE"]
    case_texts = [c["text"] for c in cases]

    assert "Case No. ABC/123/2026" in case_texts
    assert "Petition No. 45/2025" in case_texts


def test_money_extraction():
    text = "The arbitral award directed payment of ₹50,000, Rs. 10,000, and $5,000 in liquidated damages."
    ents = extract_regex_and_gazetteer_entities(text)
    money_ents = [e for e in ents if e["entity_type"] == "MONEY"]
    money_texts = [m["text"].replace(" ", "") for m in money_ents]

    assert any("₹50,000" in mt for mt in money_texts)
    assert any("Rs.10,000" in mt or "10,000" in mt for mt in money_texts)


def test_date_extraction():
    text = "The deed was signed on 15 January 2026 and notarized on 01/02/2026."
    ents = extract_regex_and_gazetteer_entities(text)
    dates = [e for e in ents if e["entity_type"] == "DATE"]
    date_texts = [d["text"] for d in dates]

    assert any("15 January 2026" in dt for dt in date_texts)
    assert any("01/02/2026" in dt for dt in date_texts)


def test_legal_role_extraction():
    text = "The plaintiff alleged default while the defendant denied all liability as the respondent."
    ents = extract_regex_and_gazetteer_entities(text)
    roles = [e for e in ents if e["entity_type"] == "LEGAL_ROLE"]
    role_texts = [r["text"].lower() for r in roles]

    assert "plaintiff" in role_texts
    assert "defendant" in role_texts
    assert "respondent" in role_texts


def test_contract_extraction():
    text = "The parties executed an Employment Agreement and a Non-Disclosure Agreement."
    ents = extract_regex_and_gazetteer_entities(text)
    contracts = [e for e in ents if e["entity_type"] == "CONTRACT"]
    contract_texts = [c["text"] for c in contracts]

    assert "Employment Agreement" in contract_texts
    assert "Non-Disclosure Agreement" in contract_texts


def test_entity_normalization():
    # Abbreviations expanded
    assert normalize_entity_text("Sec. 302", "SECTION") == "Section 302"
    assert normalize_entity_text("Art. 14", "ARTICLE") == "Article 14"
    # Legal role casing
    assert normalize_entity_text("PLAINTIFF", "LEGAL_ROLE") == "plaintiff"
    # Whitespace and quotes stripped
    assert normalize_entity_text("  \"Supreme Court of India\"  ", "COURT") == "Supreme Court of India"
    # Currency symbols
    assert normalize_entity_text("₹ 50,000", "MONEY") == "₹50,000"


def test_deduplication_and_precedence():
    candidates = [
        # spaCy extracted ORG, rule extracted COURT for same span
        {"text": "Supreme Court of India", "normalized_text": "Supreme Court of India", "entity_type": "ORGANIZATION", "confidence": 0.75, "source": "spacy", "start_position": 10, "end_position": 32},
        {"text": "Supreme Court of India", "normalized_text": "Supreme Court of India", "entity_type": "COURT", "confidence": 0.95, "source": "dictionary", "start_position": 10, "end_position": 32},
        # Case variation duplicates
        {"text": "Plaintiff", "normalized_text": "plaintiff", "entity_type": "LEGAL_ROLE", "confidence": 0.90, "source": "dictionary", "start_position": 50, "end_position": 59},
        {"text": "PLAINTIFF", "normalized_text": "plaintiff", "entity_type": "LEGAL_ROLE", "confidence": 0.90, "source": "dictionary", "start_position": 80, "end_position": 89}
    ]

    deduped = deduplicate_and_merge_entities(candidates)
    by_norm = {d["normalized_text"]: d for d in deduped}

    # Supreme Court of India resolves to COURT (domain precedence) and gets hybrid boost
    assert "Supreme Court of India" in by_norm
    sc = by_norm["Supreme Court of India"]
    assert sc["entity_type"] == "COURT"
    assert sc["source"] == "hybrid"
    assert sc["confidence"] >= 0.95

    # Plaintiff deduplicates into 1 entity with frequency 2
    assert "plaintiff" in by_norm
    assert by_norm["plaintiff"]["frequency"] == 2


# ===========================================================================
# 2. Deterministic Viva Test Case (Section 36)
# ===========================================================================

def test_deterministic_viva_entity_case():
    """
    Test Case as required by Phase 5 Specification Section 36:
    'Rajesh Sharma filed a petition before the Supreme Court of India on 15 January 2026.
     The dispute concerns breach of the Indian Contract Act. The plaintiff seeks ₹50,000
     under Section 73. Case No. ABC/123/2026 is pending before the court.'
    """
    text = (
        "Rajesh Sharma filed a petition before the Supreme Court of India on 15 January 2026. "
        "The dispute concerns breach of the Indian Contract Act. The plaintiff seeks ₹50,000 "
        "under Section 73. Case No. ABC/123/2026 is pending before the court."
    )

    entities = extract_legal_entities(text)
    entities_by_type = {e["entity_type"]: e["normalized_text"] for e in entities}

    assert "PERSON" in entities_by_type
    assert "Rajesh Sharma" in entities_by_type["PERSON"]

    assert "COURT" in entities_by_type
    assert "Supreme Court of India" in entities_by_type["COURT"]

    assert "DATE" in entities_by_type
    assert "15 January 2026" in entities_by_type["DATE"]

    assert "ACT" in entities_by_type
    assert "Indian Contract Act" in entities_by_type["ACT"]

    assert "MONEY" in entities_by_type
    assert "₹50,000" in entities_by_type["MONEY"]

    assert "SECTION" in entities_by_type
    assert "Section 73" in entities_by_type["SECTION"]

    assert "CASE_REFERENCE" in entities_by_type
    assert "Case No. ABC/123/2026" in entities_by_type["CASE_REFERENCE"]

    assert "LEGAL_ROLE" in entities_by_type
    assert "plaintiff" in entities_by_type["LEGAL_ROLE"]


# ===========================================================================
# 3. Integration Tests & API Verification
# ===========================================================================

def test_end_to_end_entity_analysis_api_flow(client, db_session):
    user = db_session.query(User).first()
    legal_text = (
        "Rajesh Sharma filed a petition before the Supreme Court of India on 15 January 2026. "
        "The dispute concerns breach of the Indian Contract Act. The plaintiff seeks ₹50,000 "
        "under Section 73. Case No. ABC/123/2026 is pending before the court."
    )
    doc = Document(
        user_id=user.id,
        filename="supreme_court_petition.pdf",
        stored_filename="uuid_supreme_court_petition.pdf",
        file_type="pdf",
        file_size=2048,
        file_hash="mockhashviva98765",
        page_count=1,
        word_count=45,
        status="completed",
        extracted_text=legal_text
    )
    db_session.add(doc)
    db_session.commit()
    db_session.refresh(doc)

    # 1. Trigger analysis: POST /api/v1/analyses/{document_id}
    res = client.post(f"/api/v1/analyses/{doc.id}")
    assert res.status_code == 200
    data = res.json()
    analysis_id = data["analysis_id"]

    assert data["status"] == "completed"
    assert data["total_keywords"] > 0
    assert data["total_entities"] > 0

    # 2. Check summary endpoint: GET /api/v1/analyses/{analysis_id}
    sum_res = client.get(f"/api/v1/analyses/{analysis_id}")
    assert sum_res.status_code == 200
    sum_data = sum_res.json()
    assert sum_data["total_entities"] == data["total_entities"]
    assert sum_data["total_keywords"] == data["total_keywords"]

    # 3. Check entity list endpoint: GET /api/v1/analyses/{analysis_id}/entities
    ent_res = client.get(f"/api/v1/analyses/{analysis_id}/entities")
    assert ent_res.status_code == 200
    ent_data = ent_res.json()
    assert ent_data["analysis_id"] == analysis_id
    assert ent_data["total"] > 0
    first_ent = ent_data["entities"][0]
    assert "text" in first_ent
    assert "normalized_text" in first_ent
    assert "entity_type" in first_ent
    assert "confidence" in first_ent
    assert "source" in first_ent

    # 4. Check entity filtering: GET /api/v1/analyses/{analysis_id}/entities?type=COURT
    court_res = client.get(f"/api/v1/analyses/{analysis_id}/entities?type=COURT")
    assert court_res.status_code == 200
    court_data = court_res.json()
    for ent in court_data["entities"]:
        assert ent["entity_type"] == "COURT"

    # 5. Check entity type summary: GET /api/v1/analyses/{analysis_id}/entities/summary
    t_summary_res = client.get(f"/api/v1/analyses/{analysis_id}/entities/summary")
    assert t_summary_res.status_code == 200
    t_summary = t_summary_res.json()
    assert isinstance(t_summary, dict)
    assert "COURT" in t_summary
    assert "SECTION" in t_summary
    assert "PERSON" in t_summary

    # 6. Verify keywords from Phase 4 still function on same analysis run
    kw_res = client.get(f"/api/v1/analyses/{analysis_id}/keywords")
    assert kw_res.status_code == 200
    assert len(kw_res.json()["keywords"]) > 0
