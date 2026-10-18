import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from main import app
from app.models.user import User
from app.models.document import Document
from app.models.analysis import AnalysisRun
from app.models.keyword import ExtractedKeyword
from app.services.candidate_generator import generate_ngram_candidates
from app.services.candidate_filter import filter_candidates, clean_candidate, is_statutory_citation
from app.services.rake_scorer import score_candidates_with_rake
from app.services.tfidf_scorer import score_candidates_with_tfidf
from app.services.legal_scorer import get_legal_score_and_category, score_candidates_with_lexicon
from app.services.scoring import normalize_scores, calculate_token_aware_frequency, compute_final_scores
from app.services.keyword_extractor import extract_keywords

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
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    # Seed test user
    test_user = User(
        name="Test Lawyer",
        email="testlawyer@lexextract.local",
        password_hash="testpasshash",
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

def test_candidate_generation_ngrams():
    text = "The plaintiff filed a petition against the defendant."
    candidates = generate_ngram_candidates(text, min_n=1, max_n=3)
    # Check unigram, bigram, trigram presence
    assert "plaintiff" in candidates
    assert "petition" in candidates
    assert any("plaintiff filed" in c for c in candidates)
    assert any("plaintiff filed a" in c for c in candidates)


def test_candidate_filter_stopwords_and_noise():
    # Stopwords only should be filtered
    assert clean_candidate("and") is None
    assert clean_candidate("of the") is None
    # Numeric noise
    assert clean_candidate("2024") is None
    assert clean_candidate("12345") is None
    # Punctuation only
    assert clean_candidate("---") is None


def test_candidate_filter_legal_preservation():
    # Statutory references must be preserved
    assert clean_candidate("Section 302") == "Section 302"
    assert clean_candidate("Article 14") == "Article 14"
    assert clean_candidate("Section 10(2)") == "Section 10(2)"
    assert is_statutory_citation("Section 302") is True
    assert is_statutory_citation("Article 14") is True

    # Multi-word legal phrases with internal stopwords
    assert clean_candidate("breach of contract") == "breach of contract"
    assert clean_candidate("articles of association") == "articles of association"

    # Leading/trailing stopword stripping
    assert clean_candidate("of the agreement") == "agreement"
    assert clean_candidate("breach of the") == "breach"


def test_rake_scoring_cooccurrence():
    text = "Breach of contract entitles the non-defaulting party to liquidated damages."
    candidates = ["breach of contract", "liquidated damages", "contract"]
    scores = score_candidates_with_rake(candidates, text)

    assert "breach of contract" in scores
    assert "liquidated damages" in scores
    assert scores["breach of contract"] > 0
    assert scores["liquidated damages"] > 0


def test_tfidf_scoring_with_reference_corpus():
    doc_text = "The Lessee agrees to pay rent for the commercial lease premises to the Lessor."
    candidates = ["lease", "lessee", "lessor", "rent"]
    scores = score_candidates_with_tfidf(candidates, doc_text)

    for cand in candidates:
        assert cand in scores
        assert scores[cand] >= 0.0


def test_legal_dictionary_matching_and_category():
    # Exact multi-word match
    score, cat = get_legal_score_and_category("breach of contract")
    assert score == 1.0
    assert cat == "contract"

    # Exact unigram match
    score, cat = get_legal_score_and_category("jurisdiction")
    assert score == 0.85
    assert cat == "litigation"

    # Statutory citation match
    score, cat = get_legal_score_and_category("Section 302")
    assert score == 0.90
    assert cat == "procedure"

    # Non-dictionary candidate
    score, cat = get_legal_score_and_category("quantum computer")
    assert score == 0.0
    assert cat == "other"


def test_score_normalization():
    # Normal case
    raw = {"a": 2.0, "b": 4.0, "c": 6.0}
    norm = normalize_scores(raw)
    assert norm["a"] == 0.0
    assert norm["b"] == 0.5
    assert norm["c"] == 1.0

    # Edge case: all values equal (no division by zero)
    raw_equal = {"a": 3.0, "b": 3.0}
    norm_equal = normalize_scores(raw_equal)
    assert norm_equal["a"] == 1.0
    assert norm_equal["b"] == 1.0

    # Edge case: all zeros
    raw_zero = {"a": 0.0, "b": 0.0}
    norm_zero = normalize_scores(raw_zero)
    assert norm_zero["a"] == 0.0
    assert norm_zero["b"] == 0.0


def test_token_aware_frequency():
    text = "The contract was signed. The contractual obligations were clear. Another contract followed."
    # 'contract' should match exactly 2 times, not 3 (ignoring 'contractual')
    freq = calculate_token_aware_frequency("contract", text)
    assert freq == 2

    # Case-insensitive
    freq_upper = calculate_token_aware_frequency("Contract", text)
    assert freq_upper == 2


def test_weighted_fusion_formula():
    text = "This contract involves mutual consideration and obligations."
    norm_tfidf = {"contract": 0.8}
    norm_rake = {"contract": 0.6}
    lex_scores = {"contract": (0.85, "contract")}

    results = compute_final_scores(norm_tfidf, norm_rake, lex_scores, text)
    assert len(results) == 1
    item = results[0]

    # Formula: 0.40 * 0.8 + 0.35 * 0.6 + 0.25 * 0.85 = 0.32 + 0.21 + 0.2125 = 0.7425
    expected_score = round((0.40 * 0.8) + (0.35 * 0.6) + (0.25 * 0.85), 4)
    assert item["final_score"] == expected_score
    assert item["category"] == "contract"


# ===========================================================================
# 2. Integration Tests & Deterministic Viva Test Case
# ===========================================================================

def test_deterministic_viva_legal_case():
    """
    Test Case as required by Phase 4 Specification Section 34:
    'This agreement is entered into between the plaintiff and defendant.
     The parties agree that any dispute arising from breach of contract shall be
     subject to arbitration. The court shall have jurisdiction over proceedings
     relating to termination of this agreement.'
    """
    text = (
        "This agreement is entered into between the plaintiff and defendant. "
        "The parties agree that any dispute arising from breach of contract shall be "
        "subject to arbitration. The court shall have jurisdiction over proceedings "
        "relating to termination of this agreement."
    )

    extracted = extract_keywords(text, top_k=20)
    keywords_found = {k["keyword"].lower() for k in extracted}

    # Verify key legal candidates are identified
    assert "breach of contract" in keywords_found
    assert "agreement" in keywords_found
    assert "plaintiff" in keywords_found
    assert "defendant" in keywords_found
    assert "arbitration" in keywords_found
    assert "jurisdiction" in keywords_found
    assert "dispute" in keywords_found

    # Verify scores are bounded in [0.0, 1.0] and sorted descending
    final_scores = [k["final_score"] for k in extracted]
    assert all(0.0 <= s <= 1.0 for s in final_scores)
    assert final_scores == sorted(final_scores, reverse=True)


def test_end_to_end_analysis_api_flow(client, db_session):
    # 1. Create a Document with extracted text in test database
    user = db_session.query(User).first()
    legal_text = (
        "This agreement is entered into between the plaintiff and defendant. "
        "The parties agree that any dispute arising from breach of contract shall be "
        "subject to arbitration. The court shall have jurisdiction over proceedings "
        "relating to termination of this agreement."
    )
    doc = Document(
        user_id=user.id,
        filename="contract_dispute.pdf",
        stored_filename="uuid_contract_dispute.pdf",
        file_type="pdf",
        file_size=2048,
        file_hash="mockhash1234567890",
        page_count=1,
        word_count=45,
        status="completed",
        extracted_text=legal_text
    )
    db_session.add(doc)
    db_session.commit()
    db_session.refresh(doc)

    # 2. Trigger analysis via POST /api/v1/analyses/{document_id}
    post_res = client.post(f"/api/v1/analyses/{doc.id}")
    assert post_res.status_code == 200
    data = post_res.json()

    analysis_id = data["analysis_id"]
    assert data["document_id"] == doc.id
    assert data["status"] == "completed"
    assert data["total_keywords"] > 0
    assert data["processing_time"] is not None

    # 3. Retrieve analysis summary via GET /api/v1/analyses/{analysis_id}
    summary_res = client.get(f"/api/v1/analyses/{analysis_id}")
    assert summary_res.status_code == 200
    summary_data = summary_res.json()
    assert summary_data["analysis_id"] == analysis_id
    assert summary_data["total_entities"] >= 0  # Phase 5 populated entities
    assert summary_data["status"] == "completed"

    # 4. Retrieve keyword results via GET /api/v1/analyses/{analysis_id}/keywords
    kw_res = client.get(f"/api/v1/analyses/{analysis_id}/keywords?limit=10")
    assert kw_res.status_code == 200
    kw_data = kw_res.json()
    assert kw_data["analysis_id"] == analysis_id
    assert len(kw_data["keywords"]) <= 10
    top_kw = kw_data["keywords"][0]
    assert "keyword" in top_kw
    assert "category" in top_kw
    assert "final_score" in top_kw
    assert "tfidf_score" in top_kw
    assert "rake_score" in top_kw
    assert "lexicon_score" in top_kw

    # 5. Test category filter query param
    cat_res = client.get(f"/api/v1/analyses/{analysis_id}/keywords?category=contract")
    assert cat_res.status_code == 200
    cat_data = cat_res.json()
    for item in cat_data["keywords"]:
        assert item["category"].lower() == "contract"

    # 6. Re-analysis creates a new AnalysisRun and preserves history
    re_res = client.post(f"/api/v1/analyses/{doc.id}")
    assert re_res.status_code == 200
    re_data = re_res.json()
    second_analysis_id = re_data["analysis_id"]
    assert second_analysis_id != analysis_id

    # Verify both runs are registered for document
    history_res = client.get(f"/api/v1/analyses/document/{doc.id}")
    assert history_res.status_code == 200
    history_runs = history_res.json()
    assert len(history_runs) == 2
    run_ids = [r["id"] for r in history_runs]
    assert analysis_id in run_ids
    assert second_analysis_id in run_ids


def test_analysis_fails_gracefully_on_empty_document(client, db_session):
    user = db_session.query(User).first()
    empty_doc = Document(
        user_id=user.id,
        filename="empty.pdf",
        stored_filename="uuid_empty.pdf",
        file_type="pdf",
        file_size=100,
        file_hash="emptyhash",
        page_count=1,
        word_count=0,
        status="completed",
        extracted_text=""
    )
    db_session.add(empty_doc)
    db_session.commit()
    db_session.refresh(empty_doc)

    res = client.post(f"/api/v1/analyses/{empty_doc.id}")
    assert res.status_code == 400
    assert "no extracted text" in res.json()["detail"].lower()
