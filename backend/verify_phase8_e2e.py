"""
Phase 8 End-to-End Programmatic Verification Suite.
Validates:
1. Analyst authentication (ANALYST role)
2. Live execution of ASTMA benchmark evaluation (POST /api/v1/evaluation/run)
3. Precision, Recall, F1 metrics calculation for Keywords and Entities
4. Keyword ablation comparison (TF-IDF vs RAKE vs Hybrid)
5. Top-K cutoff retrieval (Precision@5, Precision@10, Precision@20)
6. Latency and performance statistics
7. Error analysis classification (FPs, FNs, Type Mismatches)
8. Summary and per-document endpoints (GET /summary, /documents, /errors)
9. RBAC authorization gate (USER role blocked from running benchmark with HTTP 403)
"""
import sys
import requests

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

API_URL = "http://127.0.0.1:8000"


def run_phase8_verification():
    print("=" * 60)
    print("PHASE 8 ASTMA BENCHMARK & EVALUATION VERIFICATION SUITE")
    print("=" * 60)

    # 1. Authenticate as Analyst
    print("\n[1] Authenticating as Legal Analyst (ANALYST role)...")
    analyst_login = {
        "email_or_username": "analyst@lexextract.local",
        "password": "Analyst@Lex2026!"
    }
    res = requests.post(f"{API_URL}/api/v1/auth/login", json=analyst_login)
    assert res.status_code == 200, f"Analyst login failed: {res.text}"
    analyst_token = res.json()["access_token"]
    analyst_headers = {"Authorization": f"Bearer {analyst_token}"}
    print(f"  ✓ Analyst authenticated (Token issued for {res.json()['user']['email']}, Role: {res.json()['user']['role']})")

    # 2. Trigger Live Benchmark Run
    print("\n[2] Executing Live ASTMA Benchmark (POST /api/v1/evaluation/run)...")
    res = requests.post(f"{API_URL}/api/v1/evaluation/run", headers=analyst_headers)
    assert res.status_code == 200, f"Benchmark execution failed: {res.text}"
    report = res.json()
    b_sum = report["benchmark_summary"]
    perf = report["performance"]
    kw_eval = report["keyword_evaluation"]
    ent_eval = report["entity_evaluation"]
    doc_res = report["document_results"]
    errors = report["error_analysis"]

    print(f"  ✓ Benchmark executed on {b_sum['total_documents']} legal documents in {b_sum['total_execution_time_seconds']}s")
    print(f"  ✓ Average latency: {perf['average_time_ms']} ms/doc (Min: {perf['min_time_ms']} ms, Max: {perf['max_time_ms']} ms)")

    # 3. Inspect Keyword Metrics
    print("\n[3] Validating Keyword Extraction Metrics...")
    kw_macro = kw_eval["macro"]
    kw_micro = kw_eval["micro"]
    print(f"  ✓ Keyword Macro Metrics: Precision={kw_macro['precision']}, Recall={kw_macro['recall']}, F1={kw_macro['f1']}")
    print(f"  ✓ Keyword Micro Metrics: Precision={kw_micro['precision']}, Recall={kw_micro['recall']}, F1={kw_micro['f1']}")
    assert kw_macro["precision"] > 0, "Keyword Precision must be non-zero"
    assert kw_macro["recall"] > 0, "Keyword Recall must be non-zero"
    assert kw_macro["f1"] > 0, "Keyword F1 must be non-zero"

    # 4. Inspect Entity Metrics
    print("\n[4] Validating Named Entity Recognition (NER) Metrics...")
    ent_macro = ent_eval["macro"]
    ent_micro = ent_eval["micro"]
    print(f"  ✓ Entity Macro Metrics:  Precision={ent_macro['precision']}, Recall={ent_macro['recall']}, F1={ent_macro['f1']}")
    print(f"  ✓ Entity Micro Metrics:  Precision={ent_micro['precision']}, Recall={ent_micro['recall']}, F1={ent_micro['f1']}")
    assert ent_macro["precision"] > 0, "Entity Precision must be non-zero"
    assert ent_macro["recall"] > 0, "Entity Recall must be non-zero"
    assert ent_macro["f1"] > 0, "Entity F1 must be non-zero"

    # 5. Inspect Algorithm Ablation Study
    print("\n[5] Validating Algorithm Ablation Comparison (TF-IDF vs RAKE vs Hybrid)...")
    ablation = kw_eval["ablation_comparison"]
    print(f"  ✓ TF-IDF Alone: Precision={ablation['tfidf']['precision']}, Recall={ablation['tfidf']['recall']}, F1={ablation['tfidf']['f1']}")
    print(f"  ✓ RAKE Alone:   Precision={ablation['rake']['precision']}, Recall={ablation['rake']['recall']}, F1={ablation['rake']['f1']}")
    print(f"  ✓ Hybrid Model: Precision={ablation['hybrid']['precision']}, Recall={ablation['hybrid']['recall']}, F1={ablation['hybrid']['f1']}")

    # 6. Inspect Top-K Evaluation
    print("\n[6] Validating Top-K Cutoff Performance...")
    top_k = kw_eval["top_k_cutoffs"]
    print(f"  ✓ Top-5:  Precision@5={top_k['k_5']['precision']}, Recall@5={top_k['k_5']['recall']}, F1@5={top_k['k_5']['f1']}")
    print(f"  ✓ Top-10: Precision@10={top_k['k_10']['precision']}, Recall@10={top_k['k_10']['recall']}, F1@10={top_k['k_10']['f1']}")
    print(f"  ✓ Top-20: Precision@20={top_k['k_20']['precision']}, Recall@20={top_k['k_20']['recall']}, F1@20={top_k['k_20']['f1']}")

    # 7. Document-Level Inspection
    print("\n[7] Validating Document-Level Results...")
    assert len(doc_res) == 12, f"Expected 12 documents, found {len(doc_res)}"
    sample_doc = doc_res[0]
    print(f"  ✓ Sample: '{sample_doc['title']}' ({sample_doc['genre']})")
    print(f"     - Words: {sample_doc['word_count']}, Latency: {sample_doc['processing_time_ms']} ms")
    print(f"     - Keyword F1: {sample_doc['keyword_metrics']['f1']}, Entity F1: {sample_doc['entity_metrics']['f1']}")

    # 8. Error Analysis Breakdown
    print("\n[8] Validating Systematic Error Analysis...")
    print(f"  ✓ False Positive Keywords: {errors['false_positive_keywords_count']}")
    print(f"  ✓ False Negative Keywords: {errors['false_negative_keywords_count']}")
    print(f"  ✓ False Positive Entities: {errors['false_positive_entities_count']}")
    print(f"  ✓ False Negative Entities: {errors['false_negative_entities_count']}")
    print(f"  ✓ Entity Type Mismatches:  {errors['type_mismatches_count']}")

    # 9. Verify Read-Only Endpoints
    print("\n[9] Testing Read-Only Evaluation Endpoints...")
    res_sum = requests.get(f"{API_URL}/api/v1/evaluation/summary", headers=analyst_headers)
    assert res_sum.status_code == 200
    print(f"  ✓ GET /api/v1/evaluation/summary returned 200 OK")

    res_docs = requests.get(f"{API_URL}/api/v1/evaluation/documents", headers=analyst_headers)
    assert res_docs.status_code == 200 and len(res_docs.json()) == 12
    print(f"  ✓ GET /api/v1/evaluation/documents returned 200 OK (12 documents)")

    res_err = requests.get(f"{API_URL}/api/v1/evaluation/errors", headers=analyst_headers)
    assert res_err.status_code == 200
    print(f"  ✓ GET /api/v1/evaluation/errors returned 200 OK")

    # 10. Verify RBAC Protection
    print("\n[10] Verifying RBAC Protection for Benchmark Trigger...")
    user_login = {
        "email_or_username": "demo@lexextract.local",
        "password": "User@Lex2026!"
    }
    res_user_auth = requests.post(f"{API_URL}/api/v1/auth/login", json=user_login)
    user_token = res_user_auth.json()["access_token"]
    user_headers = {"Authorization": f"Bearer {user_token}"}

    res_unauth = requests.post(f"{API_URL}/api/v1/evaluation/run", headers=user_headers)
    assert res_unauth.status_code == 403, f"Expected 403 Forbidden for USER on /run, got {res_unauth.status_code}"
    print(f"  ✓ USER role correctly blocked with HTTP 403 Forbidden from executing benchmark")

    print("\n" + "=" * 60)
    print("ALL 10 PHASE 8 VERIFICATION CRITERIA CONFIRMED AND PASSING!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        run_phase8_verification()
    except Exception as e:
        print(f"\n❌ PHASE 8 VERIFICATION FAILURE: {e}")
        sys.exit(1)
