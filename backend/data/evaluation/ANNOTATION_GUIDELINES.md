# LexExtract Ground-Truth Annotation Guidelines

## 1. Overview & Dataset Purpose
This document establishes the formal annotation rules for the LexExtract Curated Legal Benchmark Dataset.
The dataset is designed specifically for academic evaluation in Advanced Software Testing & Mining Architecture (ASTMA).

The ground-truth annotations represent **curated project-level ground truth** annotated by legal and technical domain practitioners. It is not claimed to be an externally certified national legal corpus, but a rigorous, consistent benchmark designed to test Information Retrieval (IR) and Named Entity Recognition (NER) extraction algorithms.

---

## 2. Keyword Annotation Criteria

### 2.1 What Counts as a Legal Keyword
1. **Core Legal Concepts & Doctrines:** Substantive or procedural legal concepts central to the document's legal operative effect (e.g., *indemnity*, *arbitration*, *confidentiality*, *jurisdiction*, *force majeure*, *anticipatory bail*, *prima facie*).
2. **Defined Legal Roles & Parties:** Procedural designations (e.g., *lessor*, *lessee*, *petitioner*, *respondent*, *disclosing party*, *guarantor*).
3. **Subject Matter Nominals:** Domain-specific terms identifying the subject matter of the agreement or dispute (e.g., *demised premises*, *proprietary information*, *security deposit*, *deficiency in service*, *trademark infringement*).
4. **Remedies & Liabilities:** Terms expressing legal consequences, sanctions, or relief (e.g., *liquidated damages*, *injunctive relief*, *specific performance*, *compound interest*, *severability*).

### 2.2 What Does NOT Count as a Keyword
1. **Generic Business or Functional Stopwords:** Words that provide no distinct legal meaning (e.g., *company*, *business*, *day*, *month*, *information*, *time*, *work*, *matter*, *process*).
2. **Isolated Numerals or Dates:** Raw numbers or standalone dates without legal nominal anchors (e.g., *2026*, *thirty*, *first*).
3. **Common Verbs & Adverbs:** Action verbs outside established legal phrases (e.g., *provide*, *make*, *send*, *agree*, *shall be*, *including*).
4. **Excessively Long Clauses:** Phrases longer than 4 tokens (e.g., *"failure to pay the amount within thirty days"* is not a keyword; *"liquidated damages"* or *"default in payment"* is).

### 2.3 Keyword Normalization Rules
- **Lowercased:** Gold keywords are recorded in canonical lowercase form (e.g., `commercial lease`).
- **Lemmatization / Singular Preference:** Prefer singular base forms unless plural carries distinct legal meaning (e.g., `liquidated damages`).
- **Length Constraint:** 1 to 3 words ($1 \le n \le 3$ n-grams), matching the candidate generation boundaries of the extraction pipeline.

---

## 3. Legal Entity Annotation Criteria

The taxonomy strictly corresponds to the 13 supported entity types in LexExtract:

| Entity Type | Definition & Inclusions | Exclusions |
| :--- | :--- | :--- |
| `COURT` | Judicial bodies, tribunals, and appellate benches (e.g., *Supreme Court of India*, *High Court of Delhi*, *National Consumer Disputes Redressal Commission*). | Administrative ministries, law firms. |
| `STATUTE` / `ACT` | Named legislative acts, codes, ordinances, and constitutional statutes (e.g., *Arbitration and Conciliation Act 1996*, *Indian Penal Code*, *Companies Act 2013*). | Informal references (e.g., *the law*). |
| `SECTION` | Statutory sections, sub-sections, rules, orders, or clauses (e.g., *Section 11*, *Section 302*, *Order XXXIX Rule 1*). | General section headers without numbers. |
| `ARTICLE` | Constitutional articles (e.g., *Article 14*, *Article 21*, *Article 226*). | Journal articles or commercial articles. |
| `CASE_REFERENCE`| Formal case citations, petition numbers, suit numbers (e.g., *Commercial Suit No. 402 of 2026*, *Criminal Appeal No. 89/2024*). | Unnumbered references. |
| `PERSON` | Natural persons, judges, advocates, witnesses, individual parties (e.g., *Hon'ble Mr. Justice Sanjay Kishan Kaul*, *Priya Sen*, *Vikram Malhotra*). | Corporate entities or agencies. |
| `ORGANIZATION` | Corporate entities, partnerships, registered societies, government bodies (e.g., *Alpha Legal Systems Pvt Ltd*, *Reserve Bank of India*, *Ministry of Law*). | Courts or natural persons. |
| `LOCATION` | Jurisdictional territories, cities, states, countries, court seats (e.g., *New Delhi*, *Gurugram, Haryana*, *Mumbai*). | General street descriptions without city/state. |
| `DATE` | Standardized calendar dates specifying execution, filing, or deadline (e.g., *15th October 2026*, *1st January 2024*). | Relative expressions like *yesterday*. |
| `MONEY` | Currency figures with denomination symbols or currency codes (e.g., *Rs. 4,50,000*, *₹25,00,000*, *USD 50,000*). | Quantities without currency (e.g., *500 shares*). |
| `CONTRACT` | Named contract and instrument types (e.g., *Non-Disclosure Agreement*, *Commercial Lease Agreement*, *Power of Attorney*). | Generic word *agreement*. |
| `LEGAL_ROLE` | Procedural designations of parties (e.g., *Petitioner*, *Respondent*, *Appellant*, *Defendant*, *Lessor*, *Arbitrator*). | Informal job titles. |
| `LAW` | Broader constitutional doctrines, conventions, or customary legal frameworks (e.g., *Constitution of India*, *UNCITRAL Model Law*). | Generic phrases. |

### 3.1 Entity Text Boundaries
- Span annotations include the complete nominal phrase without trailing punctuation (e.g., `"High Court of Delhi"` rather than `"High Court of Delhi,"`).
- Prefixes like `"Hon'ble"` or `"M/s"` may be included if integral to the natural mention.
