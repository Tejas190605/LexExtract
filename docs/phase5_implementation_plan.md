# Implementation Plan — Phase 5: LexExtract Legal Entity Extraction Engine

**Project Title:** LexExtract – Legal Document Keyword Extractor  
**Phase:** Phase 5 – Legal Entity Extraction Engine  
**Status:** In Progress / Ready for Execution  

---

## 1. Executive Summary & Objective

The objective of Phase 5 is to implement a domain-aware, explainable **Legal Entity Extraction Engine** for LexExtract. The engine complements the Phase 4 keyword extraction engine by identifying structured, legally significant entities and statutory references from normalized document prose.

Rather than relying purely on generic NER or training opaque deep-learning models, LexExtract implements a **hybrid architecture**:
1. **spaCy Statistical NER:** Using a lightweight English model (`en_core_web_sm`) to extract general named entities (`PERSON`, `ORGANIZATION`, `LOCATION`, `DATE`, `MONEY`).
2. **Rule-Based Legal Extraction Engine:** Using compiled regular expressions and domain gazetteers to capture statutory and structural legal entities (`SECTION`, `ARTICLE`, `ACT`, `LAW`, `CASE_REFERENCE`, `COURT`, `CONTRACT`, `LEGAL_ROLE`).
3. **Entity Normalization:** Standardizing capitalization, whitespace, and statutory abbreviations (e.g., `Sec. 302` ➔ `Section 302`, `PLAINTIFF` ➔ `plaintiff`).
4. **Entity Deduplication & Conflict Resolution:** Merging duplicate mentions across spaCy and rule-based extractors, giving domain precedence to legal rules (e.g., classifying *Supreme Court of India* as `COURT` rather than generic `ORGANIZATION`).
5. **Heuristic Confidence & Source Tracking:** Assigning explainable confidence scores and logging the extraction origin (`spacy`, `regex`, `dictionary`, `hybrid`).
6. **Relational Persistence & API Integration:** Persisting extracted entities in `ExtractedEntity`, updating `AnalysisRun.total_entities`, and providing structured REST endpoints.
7. **Institutional Editorial UI:** Extending `AnalysisResultsPage` with a dual-tabbed interface (Keywords vs. Entities), entity type filtering, and frequency count summaries.

### Strict Scope Control (Deferred to Later Phases)
- NO custom deep-learning model training or transformer fine-tuning (`en_core_web_trf`, Legal-BERT).
- NO LLM APIs, embeddings, vector databases, or RAG.
- NO external entity linking (Wikidata, Indian Kanoon, court dockets).
- NO interactive synchronized document highlighting -> Phase 8.
- NO authentication, JWT, or RBAC -> Phase 6.
- NO audit logging service -> Phase 7.
- NO OCR.

---

## 2. Hybrid Entity Extraction Architecture

```
                    ┌─────────────────────────────────┐
                    │ Preprocessed Legal Document Text│
                    └────────────────┬────────────────┘
                                     │
               ┌─────────────────────┴─────────────────────┐
               ▼                                           ▼
┌─────────────────────────────┐             ┌─────────────────────────────┐
│ 1. spaCy Statistical NER    │             │ 2. Legal Rule Engine        │
│    Model: en_core_web_sm    │             │    - Compiled Regex         │
│    - PERSON, ORG, GPE, DATE │             │    - Legal Gazetteers       │
│    - Initial confidence 0.75│             │    - Initial confidence 0.90│
└──────────────┬──────────────┘             └──────────────┬──────────────┘
               │                                           │
               │ (PERSON, ORG, LOC, DATE, MONEY)           │ (SECTION, ARTICLE, ACT, LAW,
               │                                           │  CASE_REF, COURT, ROLE, CONTRACT)
               └─────────────────────┬─────────────────────┘
                                     │
                                     ▼
                    ┌─────────────────────────────────┐
                    │ 3. Entity Normalizer            │
                    │    - Clean whitespace & quotes  │
                    │    - Expand citations (Sec.➔Sec)│
                    │    - Canonical case mapping     │
                    └────────────────┬────────────────┘
                                     │
                                     ▼
                    ┌─────────────────────────────────┐
                    │ 4. Entity Deduplicator          │
                    │    - Span overlap resolution    │
                    │    - Domain precedence (COURT>ORG)│
                    │    - Hybrid agreement boost     │
                    └────────────────┬────────────────┘
                                     │
                                     ▼
                    ┌─────────────────────────────────┐
                    │ 5. Ranked & Classified Entities │
                    │    (text, norm, type, conf, src)│
                    └────────────────┬────────────────┘
                                     │
                                     ▼
                    ┌─────────────────────────────────┐
                    │ 6. Database Storage & Runs      │
                    │    - AnalysisRun.total_entities │
                    │    - ExtractedEntity records    │
                    └─────────────────────────────────┘
```

---

## 3. Entity Taxonomy & Definitions

LexExtract enforces a controlled 13-category legal entity taxonomy:

| Entity Type | Definition & Scope | Example Matches | Detection Mechanism |
|---|---|---|---|
| `PERSON` | Individual human names (lawyers, judges, witnesses, parties) | *Rajesh Sharma*, *John Doe*, *Justice D.Y. Chandrachud* | spaCy `PERSON` |
| `ORGANIZATION` | Corporate entities, government agencies, firms, banks | *Infosys Ltd.*, *Reserve Bank of India*, *State Bank* | spaCy `ORG` |
| `LOCATION` | Cities, states, jurisdictions, physical addresses | *New Delhi*, *Mumbai*, *Karnataka*, *India* | spaCy `GPE`, `LOC` |
| `DATE` | Specific dates, filing dates, hearing periods | *15 January 2026*, *01/01/2026*, *15-01-2026* | spaCy `DATE` + Regex |
| `MONEY` | Monetary figures, damages, contract values, fees | *₹50,000*, *Rs. 50,000*, *INR 10,00,000*, *$10,000* | spaCy `MONEY` + Regex |
| `LAW` | General legal codes, doctrines, rules, and statutory instruments | *Code of Civil Procedure*, *Penal Code*, *Constitution* | Legal Gazetteer + Regex |
| `ACT` | Formally enacted legislative Acts or statutes | *Indian Contract Act*, *Companies Act, 2013*, *Arbitration Act* | Legal Gazetteer + Regex |
| `SECTION` | Specific statutory clauses, sub-clauses, or section numbers | *Section 302*, *Section 10(2)*, *Section 73*, *Sec. 138* | Compiled Regex |
| `ARTICLE` | Constitutional articles and international convention provisions | *Article 14*, *Article 21*, *Article 19(1)(a)* | Compiled Regex |
| `CASE_REFERENCE` | Formal docket, petition, appeal, or case numbers | *Case No. 123/2026*, *Petition No. 45/2025*, *Suit 101/24* | Compiled Regex |
| `COURT` | Judicial forums, appellate benches, tribunals, courts | *Supreme Court of India*, *High Court of Delhi*, *District Court* | Legal Gazetteer + Regex |
| `CONTRACT` | Specifically named contractual instruments and agreements | *Employment Agreement*, *Lease Deed*, *Non-Disclosure Agreement* | Legal Gazetteer + Regex |
| `LEGAL_ROLE` | Procedural capacities of litigants and parties | *plaintiff*, *defendant*, *petitioner*, *respondent*, *appellant* | Legal Gazetteer + Regex |

---

## 4. Rule-Based & Gazetteer Extraction Specifications

### 4.1 Section & Article Patterns
- `SECTION`: Pattern matches prefixes `(?:Section|Sec\.|Sec)\s+(\d+[A-Za-z]?(?:\s*\([0-9a-zA-Z]+\))*|\d+)`.
  - Normalization: `Sec. 302` or `Sec 302` normalized to `Section 302`.
- `ARTICLE`: Pattern matches `(?:Article|Art\.|Art)\s+(\d+[A-Za-z]?(?:\s*\([0-9a-zA-Z]+\))*|\d+)`.
  - Normalization: `Art. 14` normalized to `Article 14`.

### 4.2 Act & Law Gazetters
- Curated list of Indian & Common Law statutes:
  - *Indian Contract Act*, *Indian Penal Code*, *Code of Civil Procedure*, *Code of Criminal Procedure*, *Companies Act*, *Arbitration and Conciliation Act*, *Information Technology Act*, *Consumer Protection Act*, *Transfer of Property Act*, *Specific Relief Act*, *Negotiable Instruments Act*, *Copyright Act*, *Patents Act*, *Trade Marks Act*.
- Identified as `ACT` when matching a specific Act name, or `LAW` for general procedural codes.

### 4.3 Court & Tribunal Patterns
- Curated gazetteer:
  - *Supreme Court of India*, *Supreme Court*, *High Court*, *District Court*, *Sessions Court*, *Civil Court*, *Family Court*, *Commercial Court*, *National Company Law Tribunal*, *NCLT*, *Consumer Disputes Redressal Forum*, *Arbitral Tribunal*.
- Rule engine prioritizes `COURT` over spaCy's generic `ORGANIZATION`.

### 4.4 Case Reference Patterns
- Conservative patterns:
  - `(?:Case|Petition|Appeal|Civil Suit|Criminal Appeal|Writ Petition)\s+No\.?\s+[A-Za-z0-9/\-]+(?:\s+of\s+\d{4})?`
  - E.g. *Case No. ABC/123/2026*, *Petition No. 45/2025*, *Appeal No. 12 of 2026*.

### 4.5 Money & Currency Patterns
- Regex: `(?:₹|Rs\.|Rs|INR|\$|USD)\s*[\d,]+(?:\.\d+)?(?:\s*(?:crore|lakh|million|billion))?`
- Normalized text preserves standard symbol without trailing whitespace.

### 4.6 Legal Role Patterns
- Word-boundary matching for procedural designations:
  - `plaintiff`, `defendant`, `petitioner`, `respondent`, `appellant`, `accused`, `complainant`, `claimant`, `applicant`, `opposite party`.
- Canonical normalization: lowercased (e.g. *PLAINTIFF* ➔ *plaintiff*).

---

## 5. Deduplication, Precedence & Confidence Scoring

### 5.1 Heuristic Confidence Calibration
- **spaCy Model Entity:** Base confidence `0.75`
- **Rule/Regex Match:** Base confidence `0.90`
- **Exact Gazetteer Match:** Base confidence `0.95`
- **Hybrid Agreement (spaCy + Rule Match):** Boosted confidence `0.98` (e.g., when spaCy detects a name and a legal gazetteer verifies it).

### 5.2 Conflict Resolution & Domain Precedence
- When spaCy extracts an entity overlapping with a legal rule match:
  - If rule classifies as `COURT` and spaCy classifies as `ORG` ➔ Rule wins (`COURT`, confidence `0.95`, source `hybrid`).
  - If rule classifies as `ACT`/`LAW` and spaCy classifies as `ORG` ➔ Rule wins (`ACT`, confidence `0.95`, source `hybrid`).
  - If rule classifies as `LEGAL_ROLE` and spaCy classifies as `PERSON` ➔ Rule wins (`LEGAL_ROLE`, confidence `0.90`, source `regex`).
  - If non-conflicting ➔ Keep both distinctly.

---

## 6. Database Flow & Schema Upgrades

### 6.1 `ExtractedEntity` Model Enhancements
Add backward-compatible columns to `backend/app/models/entity.py`:
- `normalized_text = Column(String(255), nullable=True)`
- `confidence = Column(Float, default=1.0, nullable=False)`
- `source = Column(String(50), default="rule", nullable=False)`
- Existing columns preserved: `id`, `analysis_run_id`, `entity_text`, `entity_type`, `frequency`, `page_number`, `start_position`, `end_position`.
- Update `init_db()` in `database.py` with idempotent `ALTER TABLE` checks for SQLite.

### 6.2 Analysis Pipeline Integration
In `backend/app/api/v1/endpoints/analysis.py`:
1. Document text is extracted.
2. `keyword_extractor.extract_keywords()` runs.
3. `entity_extractor.extract_entities()` runs.
4. Keywords stored in `extracted_keywords`.
5. Entities stored in `extracted_entities`.
6. `AnalysisRun` record updated:
   - `total_keywords = len(keywords)`
   - `total_entities = len(entities)`
   - `status = "completed"`
   - `processing_time = round(duration, 3)`

---

## 7. REST API Endpoints

### 7.1 `GET /api/v1/analyses/{analysis_id}/entities`
- **Query Parameters:** `type: Optional[str] = None`, `limit: int = 50`
- **Response Format:**
  ```json
  {
    "analysis_id": 1,
    "total": 12,
    "entities": [
      {
        "text": "Rajesh Sharma",
        "normalized_text": "Rajesh Sharma",
        "entity_type": "PERSON",
        "confidence": 0.75,
        "source": "spacy",
        "frequency": 2
      }
    ]
  }
  ```

### 7.2 `GET /api/v1/analyses/{analysis_id}/entities/summary`
- **Response Format:**
  ```json
  {
    "analysis_id": 1,
    "total_entities": 12,
    "type_counts": {
      "PERSON": 2,
      "COURT": 1,
      "SECTION": 3,
      "ACT": 1,
      "DATE": 2,
      "MONEY": 1,
      "LEGAL_ROLE": 2
    }
  }
  ```

---

## 8. Frontend Presentation (AnalysisResultsPage.jsx)

- Dual-Tab Interface:
  - **Keywords Tab:** Retains existing Phase 4 table, rank, category, frequency, and expandable score breakdown.
  - **Entities Tab:** Displays newly implemented legal entities table:
    - Entity Text
    - Normalized Text
    - Entity Type badge (color-coded by type)
    - Confidence progress indicator (e.g. `95%`)
    - Source badge (`spacy`, `regex`, `dictionary`, `hybrid`)
    - Frequency
- **Entity Type Filter Dropdown:** Filter by `All`, `PERSON`, `ORGANIZATION`, `COURT`, `ACT`, `SECTION`, `ARTICLE`, `CASE_REFERENCE`, `MONEY`, `DATE`, `LEGAL_ROLE`, `CONTRACT`.
- **Entity Count Summary Bar:** Compact counter badges showing detection tallies per category.
- **Header Metadata Banner:** Displays both `total_keywords` and `total_entities`.

---

## 9. Testing Strategy

### 9.1 Unit Tests (`backend/tests/test_entity_extraction.py`)
1. `test_spacy_service_initialization`: Verify model loads and maps labels cleanly.
2. `test_section_extraction`: Verify `Section 302`, `Section 10(2)`, `Sec. 138`.
3. `test_article_extraction`: Verify `Article 14`, `Article 21`.
4. `test_act_law_extraction`: Verify `Indian Contract Act`, `Companies Act, 2013`.
5. `test_court_extraction`: Verify `Supreme Court of India`, `High Court`.
6. `test_case_reference_extraction`: Verify `Case No. ABC/123/2026`.
7. `test_money_extraction`: Verify `₹50,000`, `Rs. 50,000`, `$10,000`.
8. `test_date_extraction`: Verify standard legal dates.
9. `test_legal_role_extraction`: Verify `plaintiff`, `defendant`, `appellant`.
10. `test_contract_extraction`: Verify `Employment Agreement`, `Non-Disclosure Agreement`.
11. `test_entity_normalization`: Verify case and citation expansion.
12. `test_entity_deduplication_and_precedence`: Verify `Supreme Court of India` resolves to `COURT` over `ORGANIZATION`.
13. `test_deterministic_viva_entity_case`:
    Text: *"Rajesh Sharma filed a petition before the Supreme Court of India on 15 January 2026. The dispute concerns breach of the Indian Contract Act. The plaintiff seeks ₹50,000 under Section 73. Case No. ABC/123/2026 is pending before the court."*
    Verify all expected entity types are detected.

### 9.2 Integration Tests
- End-to-end analysis triggering `POST /api/v1/analyses/{document_id}`:
  - Both keywords and entities extracted.
  - `AnalysisRun.total_entities > 0`.
  - `GET /api/v1/analyses/{analysis_id}/entities` returns real records.
  - `GET /api/v1/analyses/{analysis_id}/entities/summary` returns accurate frequency counts.
  - Category filtering on entities works.
  - Re-analysis creates distinct entity sets.

---

## 10. Acceptance Criteria Checklist

- [ ] `spacy` added to `requirements.txt` and installed in virtualenv.
- [ ] Small English spaCy model (`en_core_web_sm`) downloaded and initialized once with error fallback.
- [ ] `ExtractedEntity` model updated with `normalized_text`, `confidence`, `source`.
- [ ] Database migration adds new columns safely to SQLite table.
- [ ] `backend/app/services/spacy_service.py` implemented.
- [ ] `backend/app/services/legal_entity_rules.py` implemented with compiled regex and gazetteers.
- [ ] `backend/app/services/entity_normalizer.py` implemented.
- [ ] `backend/app/services/entity_deduplicator.py` implemented.
- [ ] `backend/app/services/entity_extractor.py` implemented orchestrating hybrid pipeline.
- [ ] `AnalysisRun.total_entities` populated upon analysis completion.
- [ ] REST API endpoints implemented:
  - `GET /api/v1/analyses/{analysis_id}/entities`
  - `GET /api/v1/analyses/{analysis_id}/entities/summary`
- [ ] Frontend `AnalysisResultsPage` features tabbed Keywords & Entities views.
- [ ] Entity filter dropdown and type summary badges functioning.
- [ ] Zero mock data in entity flow.
- [ ] All unit and integration tests pass cleanly (`pytest`).
- [ ] Full regression tests across Phases 1, 2, 3, 4 pass.
- [ ] `npm run build` succeeds.
- [ ] Browser verification passes with live entity visualization.
- [ ] Documentation updated (`README.md`, `docs/PHASE5_WALKTHROUGH.md`).
- [ ] Phase 6 (Security & JWT) remains strictly untouched.
