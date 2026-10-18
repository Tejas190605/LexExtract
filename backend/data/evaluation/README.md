# LexExtract Curated Legal Benchmark Dataset

This directory contains the gold-standard corpus and annotations for evaluating the LexExtract Information Retrieval and Named Entity Recognition pipelines.

## Directory Structure
- `documents/`: Contains 12 plain-text legal document excerpts (`doc_01.txt` through `doc_12.txt`) spanning multiple legal genres.
- `annotations/`: Contains 12 JSON files (`doc_01.json` through `doc_12.json`) containing gold keywords and gold entities.
- `ANNOTATION_GUIDELINES.md`: Formal criteria governing what terms and entities qualify for inclusion.

## Document Genres & Coverage
1. **Commercial Contracts:** Lease Agreement (`doc_01`), Employment Agreement (`doc_02`), Non-Disclosure Agreement (`doc_05`).
2. **Judicial Decisions & Briefs:** Delhi High Court Judgment (`doc_03`), Supreme Court Criminal Appeal (`doc_04`), Consumer Dispute Order (`doc_08`).
3. **Dispute Resolution & Notices:** Arbitration Invocation Notice (`doc_06`), Cease & Desist Trademark Notice (`doc_09`).
4. **Commercial Finance & Deeds:** Loan & Mortgage Deed (`doc_07`), General Power of Attorney (`doc_11`), Partnership Dissolution (`doc_12`).
5. **Statutory Instruments:** Legislative Ordinance Excerpt (`doc_10`).

## Annotation Structure
Each annotation file adheres to the schema:
```json
{
  "document_id": "doc_01",
  "document_title": "Commercial Lease Agreement",
  "genre": "Contract",
  "gold_keywords": ["keyword_1", "keyword_2", ...],
  "gold_entities": [
    { "text": "Supreme Court of India", "type": "COURT" },
    { "text": "Section 11", "type": "SECTION" }
  ]
}
```
