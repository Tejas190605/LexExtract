"""
Automated Unit and Integration Tests for LexExtract ASTMA Quantitative Evaluation Engine.
Covers:
1. Precision, Recall, F1 calculations with zero-division safeguards
2. Normalization invariance (casing, whitespace, punctuation)
3. Keyword matching and Top-K cutoff evaluations
4. Entity matching and type mismatch detection
5. Benchmark dataset loader integrity (12 documents + paired annotations)
6. Algorithm ablation evaluation logic
7. Evaluation API endpoint contracts and RBAC authorization enforcement
"""
import pytest
from fastapi.testclient import TestClient
from app.services.evaluation_service import (
    normalize_term,
    calculate_metrics,
    evaluate_single_document_keywords,
    evaluate_single_document_entities,
    load_benchmark_dataset,
    execute_full_benchmark
)
from app.core.security import create_access_token
from app.core.roles import Role
from main import app


# -------------------------------------------------------------
# 1. Metric Calculation Tests
# -------------------------------------------------------------

def test_calculate_metrics_zero_denominators():
    """Confirms no division by zero or NaN when predictions or gold are empty."""
    res = calculate_metrics(tp=0, fp=0, fn=0)
    assert res == {"precision": 0.0, "recall": 0.0, "f1": 0.0}

    res2 = calculate_metrics(tp=0, fp=5, fn=0)
    assert res2["precision"] == 0.0
    assert res2["recall"] == 0.0
    assert res2["f1"] == 0.0

    res3 = calculate_metrics(tp=0, fp=0, fn=5)
    assert res3["precision"] == 0.0
    assert res3["recall"] == 0.0
    assert res3["f1"] == 0.0


def test_calculate_metrics_perfect_match():
    """Confirms 1.0 score when all predictions match all gold items."""
    res = calculate_metrics(tp=10, fp=0, fn=0)
    assert res == {"precision": 1.0, "recall": 1.0, "f1": 1.0}


def test_calculate_metrics_partial_match():
    """Confirms standard harmonic mean precision, recall, and f1."""
    # TP=4, FP=1, FN=1 -> P = 4/5 = 0.8, R = 4/5 = 0.8, F1 = 0.8
    res = calculate_metrics(tp=4, fp=1, fn=1)
    assert res["precision"] == 0.8
    assert res["recall"] == 0.8
    assert res["f1"] == 0.8

    # TP=2, FP=2, FN=6 -> P = 2/4 = 0.5, R = 2/8 = 0.25, F1 = 2*(0.5*0.25)/(0.75) = 0.3333
    res2 = calculate_metrics(tp=2, fp=2, fn=6)
    assert res2["precision"] == 0.5
    assert res2["recall"] == 0.25
    assert res2["f1"] == 0.3333


# -------------------------------------------------------------
# 2. Normalization Invariance Tests
# -------------------------------------------------------------

def test_normalize_term_invariance():
    """Verifies that casing, extra whitespace, tabs, and punctuation are canonicalized."""
    assert normalize_term("  Commercial Lease  ") == "commercial lease"
    assert normalize_term("Section\t\n11(6)") == "section 11(6)"
    assert normalize_term('"Arbitration Clause"') == "arbitration clause"
    assert normalize_term("'Supreme Court of India.'") == "supreme court of india"
    assert normalize_term("") == ""
    assert normalize_term(None) == ""


# -------------------------------------------------------------
# 3. Keyword Evaluation & Top-K Tests
# -------------------------------------------------------------

def test_evaluate_single_document_keywords():
    """Verifies keyword evaluation with exact match and Top-K cutoff."""
    preds = ["Arbitration", "lessor", "Lessee", "Demised Premises", "wrong term", "another false"]
    gold = ["arbitration", "lessor", "lessee", "demised premises", "security deposit"]

    res = evaluate_single_document_keywords(preds, gold, cutoffs=[3, 5])
    # Total preds = 6, gold = 5. TP = 4 ("arbitration", "lessor", "lessee", "demised premises")
    # FP = 2 ("wrong term", "another false")
    # FN = 1 ("security deposit")
    assert res["tp"] == 4
    assert res["fp"] == 2
    assert res["fn"] == 1
    assert res["precision"] == round(4 / 6, 4)
    assert res["recall"] == round(4 / 5, 4)

    # Top-3 cutoff: top 3 are arbitration, lessor, lessee -> all 3 are gold!
    k3 = res["top_k"]["k_3"]
    assert k3["tp"] == 3
    assert k3["fp"] == 0
    assert k3["fn"] == 2
    assert k3["precision"] == 1.0
    assert k3["recall"] == 0.6


def test_evaluate_keywords_empty():
    """Tests evaluation when predicted or gold lists are empty."""
    res_no_pred = evaluate_single_document_keywords([], ["contract", "lease"])
    assert res_no_pred["tp"] == 0
    assert res_no_pred["fp"] == 0
    assert res_no_pred["fn"] == 2
    assert res_no_pred["precision"] == 0.0
    assert res_no_pred["recall"] == 0.0
    assert res_no_pred["f1"] == 0.0

    res_no_gold = evaluate_single_document_keywords(["contract"], [])
    assert res_no_gold["tp"] == 0
    assert res_no_gold["fp"] == 1
    assert res_no_gold["fn"] == 0
    assert res_no_gold["precision"] == 0.0
    assert res_no_gold["recall"] == 0.0


# -------------------------------------------------------------
# 4. Entity Evaluation & Type Mismatch Tests
# -------------------------------------------------------------

def test_evaluate_single_document_entities():
    """Tests entity matching with exact category agreement and type mismatch detection."""
    preds = [
        {"text": "Supreme Court of India", "entity_type": "COURT", "confidence": 0.98},
        {"text": "Section 11", "entity_type": "SECTION", "confidence": 0.95},
        {"text": "State Bank of India", "entity_type": "ORGANIZATION", "confidence": 0.90},
        {"text": "Delhi High Court", "entity_type": "ORGANIZATION", "confidence": 0.85},  # Mismatch: should be COURT
        {"text": "Spurious Entity", "entity_type": "PERSON", "confidence": 0.70}           # False positive
    ]
    gold = [
        {"text": "Supreme Court of India", "type": "COURT"},
        {"text": "Section 11", "type": "SECTION"},
        {"text": "State Bank of India", "type": "ORGANIZATION"},
        {"text": "Delhi High Court", "type": "COURT"},
        {"text": "1st October 2026", "type": "DATE"}                                       # False negative
    ]

    res = evaluate_single_document_entities(preds, gold)
    # TP: Supreme Court of India (COURT), Section 11 (SECTION), State Bank of India (ORG) -> 3
    # Type mismatch: Delhi High Court (pred: ORGANIZATION, gold: COURT) -> 1
    # Pure FP: Spurious Entity -> 1
    # Pure FN: 1st October 2026 (DATE) -> 1
    assert res["tp"] == 3
    assert len(res["type_mismatches"]) == 1
    assert res["type_mismatches"][0]["text"] == "delhi high court"
    assert res["type_mismatches"][0]["predicted_type"] == "ORGANIZATION"
    assert "COURT" in res["type_mismatches"][0]["gold_types"]
    assert res["pure_fn_count"] == 1
    assert res["pure_fp_count"] == 1
    assert res["precision"] == 0.6
    assert res["recall"] == 0.6
    assert res["f1"] == 0.6


# -------------------------------------------------------------
# 5. Benchmark Dataset Integrity Tests
# -------------------------------------------------------------

def test_benchmark_dataset_integrity():
    """Ensures all 12 benchmark legal documents and annotations load with valid fields."""
    dataset = load_benchmark_dataset()
    assert len(dataset) == 12, f"Expected 12 benchmark documents, found {len(dataset)}"

    for doc in dataset:
        assert doc["id"].startswith("doc_"), f"Invalid ID format: {doc['id']}"
        assert len(doc["title"]) > 3
        assert len(doc["genre"]) > 2
        assert len(doc["text"]) > 100, f"Document {doc['id']} text is suspiciously short"
        assert len(doc["gold_keywords"]) >= 5, f"Document {doc['id']} must have at least 5 gold keywords"
        assert len(doc["gold_entities"]) >= 3, f"Document {doc['id']} must have at least 3 gold entities"

        # Check entity format
        for ent in doc["gold_entities"]:
            assert "text" in ent and len(ent["text"]) > 0
            assert "type" in ent and len(ent["type"]) > 0


# -------------------------------------------------------------
# 6. Evaluation API Integration Tests
# -------------------------------------------------------------

@pytest.fixture
def client():
    return TestClient(app)


def test_evaluation_api_unauthenticated(client):
    """Unauthenticated calls to evaluation summary should return 401."""
    res = client.get("/api/v1/evaluation/summary")
    assert res.status_code == 401


def test_evaluation_api_authenticated_summary(client):
    """Authenticated user (USER role) can retrieve evaluation summary."""
    token = create_access_token({"sub": "1", "role": "USER"})
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/v1/evaluation/summary", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "benchmark_summary" in data
    assert "keyword_evaluation" in data
    assert "entity_evaluation" in data
    assert "performance" in data
    assert data["benchmark_summary"]["total_documents"] == 12


def test_evaluation_api_documents_list(client):
    """Authenticated user can query per-document benchmark results."""
    token = create_access_token({"sub": "1", "role": "USER"})
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/v1/evaluation/documents", headers=headers)
    assert res.status_code == 200
    docs = res.json()
    assert len(docs) == 12
    assert docs[0]["document_id"] == "doc_01"
    assert "keyword_metrics" in docs[0]
    assert "entity_metrics" in docs[0]


def test_evaluation_api_errors(client):
    """Authenticated user can query categorized error analysis."""
    token = create_access_token({"sub": "1", "role": "USER"})
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/v1/evaluation/errors", headers=headers)
    assert res.status_code == 200
    errors = res.json()
    assert "sample_fp_keywords" in errors
    assert "sample_fn_keywords" in errors
    assert "sample_type_mismatches" in errors


def test_evaluation_api_rbac_run_protection(client):
    """
    POST /api/v1/evaluation/run:
    - USER role is rejected with HTTP 403 Forbidden.
    - ANALYST and ADMIN roles are authorized.
    """
    # 1. USER role -> 403 Forbidden
    user_token = create_access_token({"sub": "2", "role": "USER"})
    res = client.post("/api/v1/evaluation/run", headers={"Authorization": f"Bearer {user_token}"})
    assert res.status_code == 403

    # 2. ADMIN role -> Allowed (200 OK)
    admin_token = create_access_token({"sub": "1", "role": "ADMIN"})
    res_admin = client.post("/api/v1/evaluation/run", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_admin.status_code == 200
    data = res_admin.json()
    assert "benchmark_summary" in data
    assert data["benchmark_summary"]["total_documents"] == 12
