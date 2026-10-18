"""
Evaluation Service for LexExtract ASTMA Benchmark Evaluation.
Implements:
1. Benchmark dataset loading (12 legal documents + gold annotations).
2. Deterministic text and token normalization.
3. Precision, Recall, and F1-score computation with zero-division safeguards.
4. Top-K cutoff evaluation (Top-5, Top-10, Top-20).
5. Keyword algorithm ablation (TF-IDF vs RAKE vs Hybrid).
6. Named Entity Recognition (NER) evaluation with strict category matching.
7. Systematic error classification (False Positives, False Negatives, Type Mismatches).
8. Real wall-clock latency measurement (per-document and aggregate).
"""
import os
import json
import time
import re
import logging
from typing import List, Dict, Any, Optional, Tuple, Set
from app.services.keyword_extractor import extract_keywords
from app.services.entity_extractor import extract_legal_entities
from app.services.candidate_generator import generate_ngram_candidates
from app.services.candidate_filter import filter_candidates
from app.services.tfidf_scorer import score_candidates_with_tfidf
from app.services.rake_scorer import score_candidates_with_rake
from app.services.scoring import normalize_scores

logger = logging.getLogger(__name__)

# Base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EVAL_DIR = os.path.join(BASE_DIR, "data", "evaluation")
DOCS_DIR = os.path.join(EVAL_DIR, "documents")
ANNOTATIONS_DIR = os.path.join(EVAL_DIR, "annotations")
REPORT_PATH = os.path.join(EVAL_DIR, "latest_evaluation_report.json")


def normalize_term(term: str) -> str:
    """
    Normalizes keyword or entity string:
    - Lowercase
    - Strip surrounding punctuation (quotes, periods, commas, colons) and whitespace
    - Preserves internal parenthesis for statutory citations like 'Section 11(6)'
    - Collapse multiple spaces into single space
    """
    if not term:
        return ""
    text = term.strip().lower()
    # Replace newlines, tabs, and multiple spaces with a single space
    text = re.sub(r"\s+", " ", text)
    # Remove leading/trailing quotes, periods, commas, colons, semicolons
    text = text.strip("\"'.,;:")
    return text.strip()


def calculate_metrics(tp: int, fp: int, fn: int) -> Dict[str, float]:
    """
    Computes Precision, Recall, and F1-score with zero-division safeguards.
    """
    precision = float(tp) / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = float(tp) / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2.0 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4)
    }


def load_benchmark_dataset() -> List[Dict[str, Any]]:
    """
    Loads all benchmark documents and paired gold annotations.
    Returns list of dicts:
    [{ "id": str, "title": str, "genre": str, "text": str, "gold_keywords": list, "gold_entities": list }]
    """
    if not os.path.exists(DOCS_DIR) or not os.path.exists(ANNOTATIONS_DIR):
        logger.warning(f"Benchmark directories not found at {EVAL_DIR}")
        return []

    dataset = []
    ann_files = sorted([f for f in os.listdir(ANNOTATIONS_DIR) if f.endswith(".json")])

    for fname in ann_files:
        doc_id = os.path.splitext(fname)[0]
        doc_txt_name = f"{doc_id}.txt"
        doc_txt_path = os.path.join(DOCS_DIR, doc_txt_name)
        ann_path = os.path.join(ANNOTATIONS_DIR, fname)

        if not os.path.exists(doc_txt_path):
            continue

        try:
            with open(ann_path, "r", encoding="utf-8") as af:
                ann_data = json.load(af)
            with open(doc_txt_path, "r", encoding="utf-8") as df:
                doc_text = df.read()

            dataset.append({
                "id": ann_data.get("document_id", doc_id),
                "title": ann_data.get("document_title", doc_id),
                "genre": ann_data.get("genre", "Legal Document"),
                "text": doc_text,
                "gold_keywords": ann_data.get("gold_keywords", []),
                "gold_entities": ann_data.get("gold_entities", [])
            })
        except Exception as exc:
            logger.error(f"Error loading benchmark document {doc_id}: {exc}")

    return dataset


def evaluate_single_document_keywords(
    predicted_keywords: List[str],
    gold_keywords: List[str],
    cutoffs: List[int] = [5, 10, 20]
) -> Dict[str, Any]:
    """
    Evaluates keyword predictions against gold standard.
    Produces unconstrained and top-K metrics plus error analysis.
    """
    norm_gold = set(normalize_term(k) for k in gold_keywords if normalize_term(k))
    norm_preds = [normalize_term(k) for k in predicted_keywords if normalize_term(k)]
    # Deduplicate predictions preserving order
    dedup_preds = []
    seen = set()
    for p in norm_preds:
        if p not in seen:
            dedup_preds.append(p)
            seen.add(p)

    # 1. Unconstrained evaluation
    pred_set = set(dedup_preds)
    tp_items = sorted(list(pred_set.intersection(norm_gold)))
    fp_items = sorted(list(pred_set - norm_gold))
    fn_items = sorted(list(norm_gold - pred_set))

    unconstrained_metrics = calculate_metrics(len(tp_items), len(fp_items), len(fn_items))

    # 2. Cutoff evaluation (Top-K)
    at_k = {}
    for k in cutoffs:
        top_slice = set(dedup_preds[:k])
        k_tp = len(top_slice.intersection(norm_gold))
        k_fp = len(top_slice - norm_gold)
        k_fn = len(norm_gold - top_slice)
        k_metrics = calculate_metrics(k_tp, k_fp, k_fn)
        at_k[f"k_{k}"] = {
            "k": k,
            "precision": k_metrics["precision"],
            "recall": k_metrics["recall"],
            "f1": k_metrics["f1"],
            "tp": k_tp,
            "fp": k_fp,
            "fn": k_fn
        }

    return {
        "precision": unconstrained_metrics["precision"],
        "recall": unconstrained_metrics["recall"],
        "f1": unconstrained_metrics["f1"],
        "tp": len(tp_items),
        "fp": len(fp_items),
        "fn": len(fn_items),
        "tp_items": tp_items,
        "fp_items": fp_items,
        "fn_items": fn_items,
        "top_k": at_k
    }


def evaluate_single_document_entities(
    predicted_entities: List[Dict[str, Any]],
    gold_entities: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Evaluates entity predictions against gold standard.
    Criteria:
    - Text match: normalized_text
    - Type match: exact entity_type equality
    """
    # Key = (norm_text, entity_type)
    gold_tuples = {}
    for ge in gold_entities:
        nt = normalize_term(ge.get("text", ""))
        et = (ge.get("type") or ge.get("entity_type") or "").strip().upper()
        if nt and et:
            gold_tuples[(nt, et)] = ge

    pred_tuples = {}
    for pe in predicted_entities:
        nt = normalize_term(pe.get("text", "") or pe.get("normalized_text", ""))
        et = (pe.get("entity_type") or pe.get("type") or "").strip().upper()
        if nt and et:
            pred_tuples[(nt, et)] = pe

    tp_items = []
    fp_items = []
    type_mismatches = []

    gold_set = set(gold_tuples.keys())
    pred_set = set(pred_tuples.keys())

    # Exact matches
    matched_pairs = pred_set.intersection(gold_set)
    for pair in matched_pairs:
        tp_items.append({
            "text": pair[0],
            "entity_type": pair[1],
            "confidence": pred_tuples[pair].get("confidence", 1.0)
        })

    # Unmatched predictions: check for type mismatches
    gold_text_to_types = {}
    for (t, et) in gold_set:
        gold_text_to_types.setdefault(t, set()).add(et)

    pred_text_to_types = {}
    for (t, et) in pred_set:
        pred_text_to_types.setdefault(t, set()).add(et)

    unmatched_preds = pred_set - gold_set
    for (p_text, p_type) in unmatched_preds:
        if p_text in gold_text_to_types:
            type_mismatches.append({
                "text": p_text,
                "predicted_type": p_type,
                "gold_types": sorted(list(gold_text_to_types[p_text])),
                "confidence": pred_tuples[(p_text, p_type)].get("confidence", 0.75)
            })
        else:
            fp_items.append({
                "text": p_text,
                "entity_type": p_type,
                "confidence": pred_tuples[(p_text, p_type)].get("confidence", 0.75)
            })

    # Unmatched gold: purely missed entities (text not detected at all)
    fn_items = []
    unmatched_gold = gold_set - pred_set
    for (g_text, g_type) in unmatched_gold:
        if g_text not in pred_text_to_types:
            fn_items.append({
                "text": g_text,
                "entity_type": g_type
            })

    # Total predicted = TP + FP + type_mismatches
    # Total gold = TP + FN + type_mismatches
    total_preds = len(pred_set)
    total_gold = len(gold_set)

    precision = float(len(tp_items)) / total_preds if total_preds > 0 else 0.0
    recall = float(len(tp_items)) / total_gold if total_gold > 0 else 0.0
    f1 = (2.0 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "tp": len(tp_items),
        "fp": len(fp_items) + len(type_mismatches),
        "fn": len(fn_items) + len(type_mismatches),
        "pure_fn_count": len(fn_items),
        "pure_fp_count": len(fp_items),
        "type_mismatch_count": len(type_mismatches),
        "tp_items": tp_items,
        "fp_items": fp_items,
        "fn_items": fn_items,
        "type_mismatches": type_mismatches
    }


def run_keyword_ablation_evaluation(
    dataset: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Compares standalone keyword scoring techniques:
    1. TF-IDF Alone
    2. RAKE Alone
    3. Full Hybrid Fusion (TF-IDF + RAKE + Lexicon)
    """
    tfidf_tps, tfidf_fps, tfidf_fns = 0, 0, 0
    rake_tps, rake_fps, rake_fns = 0, 0, 0
    hybrid_tps, hybrid_fps, hybrid_fns = 0, 0, 0

    for doc in dataset:
        text = doc["text"]
        gold = [normalize_term(k) for k in doc["gold_keywords"] if normalize_term(k)]
        gold_set = set(gold)
        if not gold_set:
            continue

        raw_candidates = generate_ngram_candidates(text, min_n=1, max_n=3)
        filtered = filter_candidates(raw_candidates)
        if not filtered:
            continue

        # 1. TF-IDF
        raw_tfidf = score_candidates_with_tfidf(filtered, text)
        norm_tfidf = normalize_scores(raw_tfidf)
        sorted_tfidf = [normalize_term(k) for k, _ in sorted(norm_tfidf.items(), key=lambda x: x[1], reverse=True)[:20]]
        t_set = set(sorted_tfidf)
        tfidf_tps += len(t_set.intersection(gold_set))
        tfidf_fps += len(t_set - gold_set)
        tfidf_fns += len(gold_set - t_set)

        # 2. RAKE
        raw_rake = score_candidates_with_rake(filtered, text)
        norm_rake = normalize_scores(raw_rake)
        sorted_rake = [normalize_term(k) for k, _ in sorted(norm_rake.items(), key=lambda x: x[1], reverse=True)[:20]]
        r_set = set(sorted_rake)
        rake_tps += len(r_set.intersection(gold_set))
        rake_fps += len(r_set - gold_set)
        rake_fns += len(gold_set - r_set)

        # 3. Hybrid Production Pipeline
        hybrid_keywords = extract_keywords(text, top_k=20)
        sorted_hybrid = [normalize_term(kw["keyword"]) for kw in hybrid_keywords if normalize_term(kw["keyword"])]
        h_set = set(sorted_hybrid)
        hybrid_tps += len(h_set.intersection(gold_set))
        hybrid_fps += len(h_set - gold_set)
        hybrid_fns += len(gold_set - h_set)

    return {
        "tfidf": calculate_metrics(tfidf_tps, tfidf_fps, tfidf_fns),
        "rake": calculate_metrics(rake_tps, rake_fps, rake_fns),
        "hybrid": calculate_metrics(hybrid_tps, hybrid_fps, hybrid_fns)
    }


def execute_full_benchmark() -> Dict[str, Any]:
    """
    Executes benchmark evaluation on all 12 curated documents:
    1. Runs production keyword & entity extraction.
    2. Measures latencies.
    3. Evaluates Precision, Recall, and F1.
    4. Computes Top-K cutoffs.
    5. Runs ablation comparison.
    6. Produces per-document and error analysis logs.
    7. Persists results to latest_evaluation_report.json.
    """
    benchmark_start = time.perf_counter()
    dataset = load_benchmark_dataset()

    if not dataset:
        raise ValueError("No benchmark documents found in evaluation directory.")

    doc_evaluations = []
    total_latencies = []
    kw_latencies = []
    ent_latencies = []

    # Aggregates
    kw_tp_total, kw_fp_total, kw_fn_total = 0, 0, 0
    ent_tp_total, ent_fp_total, ent_fn_total = 0, 0, 0

    all_fp_keywords = []
    all_fn_keywords = []
    all_fp_entities = []
    all_fn_entities = []
    all_type_mismatches = []

    for doc in dataset:
        doc_start = time.perf_counter()

        # Step 1: Run keyword extraction and measure time
        t_kw_start = time.perf_counter()
        extracted_kw = extract_keywords(doc["text"], top_k=20)
        kw_time_ms = round((time.perf_counter() - t_kw_start) * 1000, 2)
        kw_latencies.append(kw_time_ms)

        # Step 2: Run entity extraction and measure time
        t_ent_start = time.perf_counter()
        extracted_ent = extract_legal_entities(doc["text"])
        ent_time_ms = round((time.perf_counter() - t_ent_start) * 1000, 2)
        ent_latencies.append(ent_time_ms)

        total_doc_time_ms = round((time.perf_counter() - doc_start) * 1000, 2)
        total_latencies.append(total_doc_time_ms)

        # Step 3: Evaluate keywords
        pred_kw_names = [k["keyword"] for k in extracted_kw]
        kw_result = evaluate_single_document_keywords(pred_kw_names, doc["gold_keywords"])
        kw_tp_total += kw_result["tp"]
        kw_fp_total += kw_result["fp"]
        kw_fn_total += kw_result["fn"]

        # Collect keyword errors
        for fp in kw_result["fp_items"]:
            all_fp_keywords.append({"document_id": doc["id"], "keyword": fp})
        for fn in kw_result["fn_items"]:
            all_fn_keywords.append({"document_id": doc["id"], "keyword": fn})

        # Step 4: Evaluate entities
        ent_result = evaluate_single_document_entities(extracted_ent, doc["gold_entities"])
        ent_tp_total += ent_result["tp"]
        ent_fp_total += ent_result["fp"]
        ent_fn_total += ent_result["fn"]

        # Collect entity errors
        for fp in ent_result["fp_items"]:
            all_fp_entities.append({"document_id": doc["id"], "text": fp["text"], "type": fp["entity_type"]})
        for fn in ent_result["fn_items"]:
            all_fn_entities.append({"document_id": doc["id"], "text": fn["text"], "type": fn["entity_type"]})
        for mm in ent_result["type_mismatches"]:
            all_type_mismatches.append({
                "document_id": doc["id"],
                "text": mm["text"],
                "predicted_type": mm["predicted_type"],
                "gold_types": mm["gold_types"]
            })

        doc_evaluations.append({
            "document_id": doc["id"],
            "title": doc["title"],
            "genre": doc["genre"],
            "word_count": len(doc["text"].split()),
            "processing_time_ms": total_doc_time_ms,
            "keyword_metrics": {
                "precision": kw_result["precision"],
                "recall": kw_result["recall"],
                "f1": kw_result["f1"],
                "predicted_count": len(extracted_kw),
                "gold_count": len(doc["gold_keywords"]),
                "tp": kw_result["tp"],
                "fp": kw_result["fp"],
                "fn": kw_result["fn"],
                "top_k": kw_result["top_k"]
            },
            "entity_metrics": {
                "precision": ent_result["precision"],
                "recall": ent_result["recall"],
                "f1": ent_result["f1"],
                "predicted_count": len(extracted_ent),
                "gold_count": len(doc["gold_entities"]),
                "tp": ent_result["tp"],
                "fp": ent_result["fp"],
                "fn": ent_result["fn"]
            }
        })

    # Overall Global Metrics (Micro pooling)
    overall_kw = calculate_metrics(kw_tp_total, kw_fp_total, kw_fn_total)
    overall_ent = calculate_metrics(ent_tp_total, ent_fp_total, ent_fn_total)

    # Macro Averages (Mean of per-document scores)
    macro_kw_p = round(sum(d["keyword_metrics"]["precision"] for d in doc_evaluations) / len(doc_evaluations), 4)
    macro_kw_r = round(sum(d["keyword_metrics"]["recall"] for d in doc_evaluations) / len(doc_evaluations), 4)
    macro_kw_f1 = round(sum(d["keyword_metrics"]["f1"] for d in doc_evaluations) / len(doc_evaluations), 4)

    macro_ent_p = round(sum(d["entity_metrics"]["precision"] for d in doc_evaluations) / len(doc_evaluations), 4)
    macro_ent_r = round(sum(d["entity_metrics"]["recall"] for d in doc_evaluations) / len(doc_evaluations), 4)
    macro_ent_f1 = round(sum(d["entity_metrics"]["f1"] for d in doc_evaluations) / len(doc_evaluations), 4)

    # Top-K Cutoff Averages across corpus
    top_k_averages = {}
    for k in [5, 10, 20]:
        k_key = f"k_{k}"
        k_p = round(sum(d["keyword_metrics"]["top_k"][k_key]["precision"] for d in doc_evaluations) / len(doc_evaluations), 4)
        k_r = round(sum(d["keyword_metrics"]["top_k"][k_key]["recall"] for d in doc_evaluations) / len(doc_evaluations), 4)
        k_f1 = round(sum(d["keyword_metrics"]["top_k"][k_key]["f1"] for d in doc_evaluations) / len(doc_evaluations), 4)
        top_k_averages[k_key] = {"k": k, "precision": k_p, "recall": k_r, "f1": k_f1}

    # Run Algorithm Ablation Comparison
    ablation = run_keyword_ablation_evaluation(dataset)

    total_duration_sec = round(time.perf_counter() - benchmark_start, 3)

    report = {
        "benchmark_summary": {
            "dataset_name": "LexExtract Curated Legal Benchmark Corpus (v1.0)",
            "total_documents": len(dataset),
            "execution_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "total_execution_time_seconds": total_duration_sec
        },
        "performance": {
            "average_time_ms": round(sum(total_latencies) / len(total_latencies), 1),
            "min_time_ms": min(total_latencies),
            "max_time_ms": max(total_latencies),
            "avg_keyword_time_ms": round(sum(kw_latencies) / len(kw_latencies), 1),
            "avg_entity_time_ms": round(sum(ent_latencies) / len(ent_latencies), 1)
        },
        "keyword_evaluation": {
            "micro": overall_kw,
            "macro": {
                "precision": macro_kw_p,
                "recall": macro_kw_r,
                "f1": macro_kw_f1
            },
            "top_k_cutoffs": top_k_averages,
            "ablation_comparison": ablation
        },
        "entity_evaluation": {
            "micro": overall_ent,
            "macro": {
                "precision": macro_ent_p,
                "recall": macro_ent_r,
                "f1": macro_ent_f1
            }
        },
        "document_results": doc_evaluations,
        "error_analysis": {
            "false_positive_keywords_count": len(all_fp_keywords),
            "false_negative_keywords_count": len(all_fn_keywords),
            "false_positive_entities_count": len(all_fp_entities),
            "false_negative_entities_count": len(all_fn_entities),
            "type_mismatches_count": len(all_type_mismatches),
            "sample_fp_keywords": all_fp_keywords[:20],
            "sample_fn_keywords": all_fn_keywords[:20],
            "sample_fp_entities": all_fp_entities[:20],
            "sample_fn_entities": all_fn_entities[:20],
            "sample_type_mismatches": all_type_mismatches[:20]
        }
    }

    # Save to disk
    try:
        with open(REPORT_PATH, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
    except Exception as save_err:
        logger.warning(f"Could not persist evaluation report: {save_err}")

    return report


def get_latest_evaluation_report() -> Optional[Dict[str, Any]]:
    """
    Retrieves the persisted benchmark evaluation report.
    If none exists, executes the benchmark to generate the baseline report.
    """
    if os.path.exists(REPORT_PATH):
        try:
            with open(REPORT_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return execute_full_benchmark()
