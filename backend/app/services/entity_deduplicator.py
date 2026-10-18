from typing import List, Dict, Any, Tuple
from collections import defaultdict

# Precedence hierarchy: Domain legal rules take precedence over generic statistical spaCy labels
DOMAIN_RULE_TYPES = {
    "COURT", "ACT", "LAW", "SECTION", "ARTICLE", "CASE_REFERENCE", "LEGAL_ROLE", "CONTRACT"
}
GENERIC_SPACY_TYPES = {
    "ORGANIZATION", "PERSON", "LOCATION"
}


def deduplicate_and_merge_entities(candidate_entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Consolidates candidate entities extracted from spaCy, Regex, and Legal Gazetteers:
    1. Resolves span overlaps and label conflicts (e.g. spaCy ORG vs. Legal COURT -> resolves to COURT).
    2. Groups mentions by canonical normalized text.
    3. Calculates aggregate frequency.
    4. Computes explainable heuristic confidence:
       - spaCy statistical entity: 0.75
       - Rule / Regex pattern: 0.90
       - Legal gazetteer dictionary: 0.95
       - Hybrid agreement (spaCy + rule overlap): 0.98
    5. Sets source to 'spacy', 'regex', 'dictionary', or 'hybrid'.
    """
    if not candidate_entities:
        return []

    # Step 1: Resolve span overlaps
    # Sort candidates by span start ascending, span length descending
    sorted_candidates = sorted(
        candidate_entities,
        key=lambda x: (x.get("start_position", 0), -(x.get("end_position", 0) - x.get("start_position", 0)))
    )

    resolved_occurrences: List[Dict[str, Any]] = []

    for cand in sorted_candidates:
        cand_start = cand.get("start_position", 0)
        cand_end = cand.get("end_position", 0)
        cand_type = cand.get("entity_type", "OTHER")

        overlap_found = False
        for idx, existing in enumerate(resolved_occurrences):
            ex_start = existing.get("start_position", 0)
            ex_end = existing.get("end_position", 0)
            ex_type = existing.get("entity_type", "OTHER")

            # Check if spans overlap significantly
            if max(cand_start, ex_start) < min(cand_end, ex_end):
                overlap_found = True
                # Case A: Rule entity conflicts with generic spaCy entity (e.g. COURT vs ORG)
                if cand_type in DOMAIN_RULE_TYPES and ex_type in GENERIC_SPACY_TYPES:
                    # Domain rule wins, mark hybrid agreement
                    resolved_occurrences[idx] = {
                        "text": cand.get("text", existing.get("text")),
                        "normalized_text": cand.get("normalized_text", existing.get("normalized_text")),
                        "entity_type": cand_type,
                        "confidence": 0.98,
                        "source": "hybrid",
                        "start_position": min(cand_start, ex_start),
                        "end_position": max(cand_end, ex_end)
                    }
                elif ex_type in DOMAIN_RULE_TYPES and cand_type in GENERIC_SPACY_TYPES:
                    # Existing domain rule wins, boost confidence
                    resolved_occurrences[idx]["confidence"] = 0.98
                    resolved_occurrences[idx]["source"] = "hybrid"
                elif cand_type == ex_type:
                    # Agreement on type across sources
                    resolved_occurrences[idx]["confidence"] = max(existing.get("confidence", 0.75), 0.98)
                    resolved_occurrences[idx]["source"] = "hybrid"
                break

        if not overlap_found:
            resolved_occurrences.append(cand)

    # Step 2: Group distinct mentions by (normalized_text_lower, entity_type)
    grouped: Dict[Tuple[str, str], Dict[str, Any]] = {}
    occurrence_counts: Dict[Tuple[str, str], int] = defaultdict(int)

    for occ in resolved_occurrences:
        norm = occ.get("normalized_text", "").strip()
        ent_type = occ.get("entity_type", "OTHER")
        if not norm:
            continue

        key = (norm.lower(), ent_type)
        occurrence_counts[key] += 1

        if key not in grouped:
            grouped[key] = {
                "text": occ.get("text", norm),
                "normalized_text": norm,
                "entity_type": ent_type,
                "confidence": occ.get("confidence", 0.85),
                "source": occ.get("source", "rule"),
                "start_position": occ.get("start_position", 0),
                "end_position": occ.get("end_position", 0)
            }
        else:
            # Keep highest confidence and update hybrid status if observed across multiple sources
            if occ.get("source") != grouped[key]["source"]:
                grouped[key]["source"] = "hybrid"
                grouped[key]["confidence"] = max(grouped[key]["confidence"], 0.98)
            else:
                grouped[key]["confidence"] = max(grouped[key]["confidence"], occ.get("confidence", 0.85))

    # Build final list
    final_entities: List[Dict[str, Any]] = []
    for key, data in grouped.items():
        data["frequency"] = occurrence_counts[key]
        data["confidence"] = round(data["confidence"], 2)
        final_entities.append(data)

    # Sort primarily by frequency DESC, secondarily by confidence DESC
    final_entities.sort(key=lambda x: (x["frequency"], x["confidence"]), reverse=True)
    return final_entities
