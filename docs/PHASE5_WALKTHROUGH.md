# Phase 5 Walkthrough — Legal Entity Extraction Engine

**Project:** LexExtract — Legal Document Keyword & Entity Extractor  
**Phase:** Phase 5 — Legal Entity Extraction Engine  
**Status:** Completed, Verified, and Tested  

---

## 1. Phase Objective

The primary objective of Phase 5 was to construct a robust, deterministic, and explainable **Legal Entity Extraction Engine** for LexExtract:
- Ingest normalized legal document text from ingested PDF/DOCX files.
- Identify legally significant entities and formal citations across 13 controlled legal entity types.
- Combine statistical Named Entity Recognition (spaCy `en_core_web_sm`) with domain-specific legal regular expressions and curated gazetteer lexicons.
- Perform statutory normalization, casing standardization, and whitespace cleaning.
- Deduplicate overlapping entities, enforce legal domain precedence (e.g., classifying *Supreme Court of India* as `COURT` rather than generic `ORGANIZATION`), and apply hybrid confidence boosting.
- Persist extracted entities in the SQLite database (`ExtractedEntity`) and update run aggregates (`AnalysisRun.total_entities`).
- Expose RESTful endpoints for entity querying (`GET /api/v1/analyses/{analysis_id}/entities`) and category aggregations (`GET /api/v1/analyses/{analysis_id}/entities/summary`).
- Upgrade the frontend into a dual-tabbed legal editorial workspace displaying both **Top Legal Keywords** and **Extracted Legal Entities** with dynamic filtering and summary cards.

---

## 2. Hybrid Extraction Architecture

```
                    ┌───────────────────────────────┐
                    │      Legal Document Text      │
                    └───────────────┬───────────────┘
                                    │
                        ┌───────────┴───────────┐
                        ▼                       ▼
              ┌───────────────────┐   ┌───────────────────┐
              │     spaCy NER     │   │ Legal Rule Engine │
              │ (en_core_web_sm)  │   │  Regex & Lexicons │
              └─────────┬─────────┘   └─────────┬─────────┘
                        │                       │
                        │ PERSON, ORG, GPE,     │ SECTION, ARTICLE, ACT,
                        │ DATE, MONEY           │ COURT, CASE_REFERENCE,
                        │                       │ CONTRACT, LEGAL_ROLE
                        └───────────┬───────────┘
                                    ▼
                      ┌───────────────────────────┐
                      │    Entity Normalization   │
                      │  - Citation standardization│
                      │  - Whitespace & casing     │
                      └─────────────┬─────────────┘
                                    ▼
                      ┌───────────────────────────┐
                      │    Entity Deduplication   │
                      │  - Overlap resolution     │
                      │  - Domain rule precedence │
                      │  - Hybrid boost (0.98)    │
                      └─────────────┬─────────────┘
                                    ▼
                      ┌───────────────────────────┐
                      │   Relational Persistence  │
                      │  (ExtractedEntity table)  │
                      │  (AnalysisRun count)      │
                      └─────────────┬─────────────┘
                                    ▼
                      ┌───────────────────────────┐
                      │      Dual-Tabbed UI       │
                      │  (Keywords + Entities)    │
                      └───────────────────────────┘
```

---

## 3. Controlled Entity Taxonomy (13 Types)

LexExtract enforces a strict, controlled taxonomy of 13 practical legal entity types:

1. **`PERSON`**: Natural persons, advocates, witnesses, judges, and named individuals (e.g., *Rajesh Sharma*).
2. **`ORGANIZATION`**: Corporations, registered companies, trade bodies, and institutional authorities (e.g., *Tata Consultancy Services*, *Reserve Bank of India*).
3. **`LOCATION`**: Geopolitical entities, cities, states, jurisdictions, and countries (e.g., *New Delhi*, *India*, *Maharashtra*).
4. **`DATE`**: Calendar dates, execution dates, effective periods, and deadlines (e.g., *15 January 2026*, *01/01/2026*).
5. **`MONEY`**: Currency quantities and financial figures with symbols or ISO currency codes (e.g., *₹50,000*, *Rs. 50,000*, *INR 50,000*, *$10,000*).
6. **`SECTION`**: Specific statutory section and subsection citations (e.g., *Section 302*, *Section 10(2)*, *Sec. 73*).
7. **`ARTICLE`**: Constitutional article provisions and numbered sub-articles (e.g., *Article 14*, *Article 21*, *Article 19(1)(a)*).
8. **`ACT`**: Formally named legislative statutes (e.g., *Indian Contract Act*, *Companies Act, 2013*, *Copyright Act*).
9. **`LAW`**: Broader statutory instruments, constitutional laws, or legislative bodies of rules (e.g., *Indian Penal Code*, *Constitution of India*).
10. **`COURT`**: Judicial courts, forums, and specialized tribunals (e.g., *Supreme Court of India*, *High Court of Delhi*, *National Company Law Tribunal*).
11. **`CASE_REFERENCE`**: Formal docket numbers, petition citations, and suit identifiers (e.g., *Case No. 123/2026*, *Petition No. 45/2025*, *Appeal No. 12 of 2026*).
12. **`CONTRACT`**: Standard named legal agreement types (e.g., *Employment Agreement*, *Non-Disclosure Agreement*, *Service Agreement*).
13. **`LEGAL_ROLE`**: Procedural adversarial roles in litigation or contract execution (e.g., *plaintiff*, *defendant*, *petitioner*, *respondent*, *appellant*, *accused*).

---

## 4. spaCy Implementation & Caching

- **Model Selection:** `en_core_web_sm` (small English statistical model; ~12 MB). Transformer models (`en_core_web_trf`) and heavy LLMs are strictly avoided.
- **Singleton Architecture:** Implemented in `backend/app/services/spacy_service.py` via `SpacyService.get_nlp()`. The language pipeline is loaded once during application startup and cached for all subsequent document analyses.
- **Label Mapping:**
  - `PERSON` $\rightarrow$ `PERSON`
  - `ORG` $\rightarrow$ `ORGANIZATION`
  - `GPE`, `LOC` $\rightarrow$ `LOCATION`
  - `DATE` $\rightarrow$ `DATE`
  - `MONEY` $\rightarrow$ `MONEY`
  - Unmapped spaCy labels (e.g., `ORDINAL`, `CARDINAL`, `PRODUCT`, `EVENT`) are filtered out to avoid cluttering the legal taxonomy.
- **Resilience:** If the spaCy package or model is missing or fails to load, `SpacyService` logs an informative diagnostic error and returns an empty list, allowing the rule-based extractor to continue functioning without crashing the application.

---

## 5. Legal Rule Engine (`legal_entity_rules.py`)

The rule engine uses precompiled regular expressions and curated domain gazetteers to extract domain structures that statistical models routinely miss or misclassify.

### Compiled Regex Patterns:
- **Sections:** `(?:Sections?|Secs?\.?)\s+(\d+[A-Z]?(?:\(\d+\))*(?:\([a-z]\))*)`
- **Articles:** `(?:Articles?|Art\.?)\s+(\d+[A-Z]?(?:\(\d+\))*(?:\([a-z]\))*)`
- **Case Citations:** `(?:(?:Civil|Criminal|Special|Writ|Arbitration)\s+)?(?:Case|Petition|Appeal|Suit|Application)\s+No\.?\s+[A-Za-z0-9\/\-]+(?:\s+of\s+\d{4})?`
- **Currencies:** `(?:₹|Rs\.?|INR|\$|USD|EUR|GBP)\s*[\d,]+(?:\.\d{1,2})?`
- **Dates:** `\b(?:\d{1,2}(?:st|nd|rd|th)?[\/\-]\d{1,2}[\/\-]\d{2,4}|\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s,]+\d{4})\b`

### Legal Gazetteers:
- **Acts & Laws:** *Indian Contract Act, Indian Penal Code, Code of Civil Procedure, Code of Criminal Procedure, Companies Act, Arbitration and Conciliation Act, Information Technology Act, Consumer Protection Act, Transfer of Property Act, Specific Relief Act, Copyright Act, Patents Act, Trade Marks Act*.
- **Courts:** *Supreme Court of India, High Court, District Court, Sessions Court, Civil Court, Family Court, Commercial Court, National Company Law Tribunal, Consumer Court, Debt Recovery Tribunal*.
- **Contracts:** *Employment Agreement, Service Agreement, Lease Agreement, Non-Disclosure Agreement, Confidentiality Agreement, Sale Agreement, Purchase Agreement, Loan Agreement, Partnership Agreement, Licensing Agreement*.
- **Legal Roles:** *plaintiff, defendant, petitioner, respondent, appellant, accused, complainant, claimant, applicant, responding party, opposite party*.

---

## 6. Normalization & Deduplication

### Normalization (`entity_normalizer.py`):
1. **Citation Standardizing:** Expands abbreviations (e.g., `Sec. 302` or `Sec 302` $\rightarrow$ `Section 302`, `Art. 14` $\rightarrow$ `Article 14`).
2. **Whitespace Collapsing:** Strips leading/trailing spaces and condenses internal tabs/spaces.
3. **Role Normalization:** Canonicalizes legal roles to lower-case (e.g., `PLAINTIFF`, `Plaintiff` $\rightarrow$ `plaintiff`).
4. **Casing Preservation:** Preserves original capitalization for natural persons, courts, and corporate entities.

### Deduplication & Domain Precedence (`entity_deduplicator.py`):
- **Span Conflict Resolution:** When spaCy and the legal rule engine extract overlapping character spans, the system evaluates domain evidence.
- **Court / Act Precedence:** If spaCy extracts *Supreme Court of India* as `ORG`, and the rule engine extracts it as `COURT`, the legal type `COURT` overrides `ORG`.
- **Hybrid Boosting:** When both engines agree on the same span, the entity's confidence is boosted to `0.98` and its source is tagged as `"hybrid"`.
- **Case-Insensitive Uniqueness:** Grouping by `(normalized_text.lower(), entity_type)` ensures duplicate occurrences across the text are cleanly deduplicated, retaining the highest confidence score and the first character offset.

---

## 7. Explainable Confidence Scoring Strategy

Confidence scores reflect transparent heuristics based on the evidentiary rigor of the extraction channel:

| Channel / Evidence | Heuristic Confidence | Provenance Source |
| :--- | :--- | :--- |
| **Statistical NER (spaCy)** | `0.75` | `"spacy"` |
| **Domain Gazetteer Match** | `0.95` | `"dictionary"` |
| **Compiled Regex Citation** | `0.90`–`0.95` | `"regex"` |
| **Hybrid Agreement (spaCy + Rule Engine)** | `0.98` | `"hybrid"` |

*Academic Note:* These scores are heuristic confidence indicators designed for explainable ranking and user transparency; they are not statistically calibrated Bayesian posterior probabilities.

---

## 8. Database Architecture & Migrations

### Model: `ExtractedEntity` (`backend/app/models/entity.py`)
```python
class ExtractedEntity(Base):
    __tablename__ = "extracted_entities"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analysis_runs.id"), nullable=False)
    text = Column(String(255), nullable=False)
    normalized_text = Column(String(255), nullable=True)
    entity_type = Column(String(50), nullable=False)
    confidence = Column(Float, nullable=False, default=1.0)
    source = Column(String(50), nullable=False, default="rule")
    start_position = Column(Integer, nullable=True)
    end_position = Column(Integer, nullable=True)
```

### Safe Schema Evolution:
`init_db()` in `backend/app/core/database.py` was updated with safe SQLite `PRAGMA table_info` checks that automatically add `normalized_text`, `confidence`, and `source` columns if they are absent, preserving existing development data.

---

## 9. REST API Endpoints

### 1. Initiate Unified Analysis
`POST /api/v1/analyses/{document_id}`
- **Behavior:** Executes keyword extraction pipeline followed by entity extraction pipeline.
- **Response:**
  ```json
  {
    "analysis_id": 1,
    "status": "completed",
    "total_keywords": 20,
    "total_entities": 29,
    "processing_time": 0.045
  }
  ```

### 2. Query Extracted Entities
`GET /api/v1/analyses/{analysis_id}/entities?type=PERSON&limit=50`
- **Response:**
  ```json
  {
    "analysis_id": 1,
    "total": 3,
    "entities": [
      {
        "text": "Rajesh Sharma",
        "normalized_text": "Rajesh Sharma",
        "entity_type": "PERSON",
        "confidence": 0.85,
        "source": "spacy",
        "start_position": 0,
        "end_position": 13
      }
    ]
  }
  ```

### 3. Entity Type Summary
`GET /api/v1/analyses/{analysis_id}/entities/summary`
- **Response:**
  ```json
  {
    "ACT": 2,
    "CONTRACT": 1,
    "COURT": 2,
    "DATE": 6,
    "LEGAL_ROLE": 4,
    "LOCATION": 3,
    "MONEY": 3,
    "ORGANIZATION": 4,
    "PERSON": 4,
    "SECTION": 5
  }
  ```

---

## 10. Frontend Presentation Tier

`frontend/src/pages/AnalysisResultsPage.jsx` was enhanced into an integrated, dual-tabbed legal analytical workspace:
1. **Dual Navigation Tabs:** Toggle smoothly between **Top Legal Keywords (N)** and **Extracted Legal Entities (N)**.
2. **Entity Summary Badges:** Top grid displaying instant entity counts broken down by category (`ACT`, `SECTION`, `COURT`, `DATE`, `MONEY`, `PERSON`, etc.).
3. **Dynamic Filtering:** Dropdown allowing filtering by all 13 entity types without page reloads.
4. **Professional Entity Table:** Displays Entity Text, Entity Type, Confidence (with colored visual progress bar), and Provenance Badge (`spacy`, `regex`, `dictionary`, `hybrid`).

---

## 11. Deterministic Verification & Test Results

### Deterministic Test Text:
> *"Rajesh Sharma filed a petition before the Supreme Court of India on 15 January 2026. The dispute concerns breach of the Indian Contract Act. The plaintiff seeks ₹50,000 under Section 73. Case No. ABC/123/2026 is pending before the court."*

### Verified Entity Extraction:
| Detected Entity | Normalized Form | Entity Type | Confidence | Source |
| :--- | :--- | :--- | :--- | :--- |
| **Rajesh Sharma** | Rajesh Sharma | `PERSON` | 0.85 | `spacy` |
| **Supreme Court of India** | Supreme Court of India | `COURT` | 0.98 | `hybrid` |
| **15 January 2026** | 15 January 2026 | `DATE` | 0.95 | `regex` |
| **Indian Contract Act** | Indian Contract Act | `ACT` | 0.95 | `dictionary` |
| **₹50,000** | ₹50,000 | `MONEY` | 0.95 | `regex` |
| **Section 73** | Section 73 | `SECTION` | 0.95 | `regex` |
| **Case No. ABC/123/2026** | Case No. ABC/123/2026 | `CASE_REFERENCE` | 0.95 | `regex` |
| **plaintiff** | plaintiff | `LEGAL_ROLE` | 0.95 | `dictionary` |

### Test Suite Execution:
- Unit & Integration Tests: `backend/tests/test_entity_extraction.py` (14 deterministic tests).
- Total Backend Tests: **54 / 54 passing**.
  - Database & Models: 15 tests
  - Document Ingestion: 9 tests
  - Health: 2 tests
  - Keyword Extraction: 14 tests
  - Entity Extraction: 14 tests

---

## 12. Curriculum Integration

### Advanced Social, Text and Media Analytics (ASTMA)
- **Hybrid Information Extraction:** Explains the engineering trade-off between statistical Named Entity Recognition (effective for open-domain names and places) versus deterministic rule engines (critical for closed-domain statutory references, docket numbers, and judicial hierarchies).
- **Entity Normalization:** Demonstrates token normalization and canonicalization to standardize variance across citation conventions (*Sec. 302* vs *Section 302*).
- **Confidence Calibration Heuristics:** Showcases multi-channel evidence weighting where cross-channel agreement (*hybrid*) yields boosted confidence.

### Enterprise Systems (ES)
- **Three-Tier Architecture:** Complete separation between the Presentation Tier (React), Application Tier (FastAPI orchestrating modular NLP services), and Data Tier (SQLAlchemy/SQLite).
- **Service-Oriented Design:** `SpacyService`, `LegalEntityRuleEngine`, `EntityNormalizer`, and `EntityDeduplicator` operate as isolated, reusable single-responsibility services coordinated by `EntityExtractor`.
- **Relational Integrity:** Extracted entities are linked via foreign keys to `AnalysisRun`, maintaining referential consistency and cascade behaviors.

---

## 13. Limitations & Phase 6 Boundary

- **Academic Scope:** This is a lightweight rule-enhanced NER engine designed for academic demonstration and reproducible college defense, not an enterprise legal intelligence product.
- **Phase 6 Boundary:** User authentication, JWT security tokens, role-based access control (RBAC), and user-attributed audit logging are strictly deferred to **Phase 6**.
- **Phase 8 Boundary:** In-document interactive visual text highlighting is strictly deferred to **Phase 8**.
