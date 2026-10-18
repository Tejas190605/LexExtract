# LexExtract — Final Test Plan & Quality Assurance Inventory

## 1. Test Suite Summary
- **Total Automated Backend Tests:** 98 tests
- **Passing Status:** 98 / 98 PASS (100%)
- **Test Execution Time:** 29.30 seconds
- **Frontend Production Compilation:** 1,559 modules transformed, 0 lint/syntax errors
- **E2E Browser Verification:** Complete 15-step flow verified by browser automation

---

## 2. Test Inventory by Category

### Category 1: Authentication & Identity (`tests/test_auth.py` — 14 Tests)
| Test ID | Scenario | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :--- | :---: |
| `AUTH-01` | JWT Generation & Token Decoding | Issued JWT contains user ID and role claims | Decoded claims match user profile | **PASS** |
| `AUTH-02` | Expired Token Rejection | Expired token rejected | Returns HTTP 401 Unauthorized | **PASS** |
| `AUTH-03` | Malformed Token Rejection | Tampered token signature rejected | Returns HTTP 401 Unauthorized | **PASS** |
| `AUTH-04` | User Registration Success | Valid registration yields new user | Returns HTTP 201 Created | **PASS** |
| `AUTH-05` | Duplicate Email Registration | Same email rejected | Returns HTTP 400 Bad Request | **PASS** |
| `AUTH-06` | Duplicate Username Registration | Same username rejected | Returns HTTP 400 Bad Request | **PASS** |
| `AUTH-07` | Password Length Validation | Passwords < 8 chars rejected | Returns HTTP 422 Unprocessable | **PASS** |
| `AUTH-08` | User Login Success | Correct password returns JWT | Returns HTTP 200 + access token | **PASS** |
| `AUTH-09` | Invalid Password Rejection | Wrong password rejected | Returns HTTP 401 Unauthorized | **PASS** |
| `AUTH-10` | Unknown User Login Rejection | Nonexistent username rejected | Returns HTTP 401 Unauthorized | **PASS** |
| `AUTH-11` | Inactive User Login Rejection | Deactivated user blocked from login | Returns HTTP 401 Unauthorized | **PASS** |
| `AUTH-12` | `/auth/me` with Valid Token | Returns authenticated user profile | Profile matches claims | **PASS** |
| `AUTH-13` | `/auth/me` without Token | Unauthenticated access rejected | Returns HTTP 401 Unauthorized | **PASS** |
| `AUTH-14` | Password Hash Redaction | User responses omit password hash | `password_hash` never exposed | **PASS** |

### Category 2: Authorization, RBAC & Data Isolation (`tests/test_authorization.py` — 10 Tests)
| Test ID | Scenario | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :--- | :---: |
| `RBAC-01` | Protected Endpoint without Token | Block unauthenticated access | Returns HTTP 401 Unauthorized | **PASS** |
| `RBAC-02` | Normal User Accessing Admin Endpoints | Non-admin blocked from `/admin/*` | Returns HTTP 403 Forbidden | **PASS** |
| `RBAC-03` | Analyst Accessing Admin Endpoints | Analyst blocked from user admin | Returns HTTP 403 Forbidden | **PASS** |
| `RBAC-04` | Admin Accessing Admin Endpoints | Admin granted audit/user access | Returns HTTP 200 OK | **PASS** |
| `RBAC-05` | User Accessing Own Document | User views own document | Returns HTTP 200 OK | **PASS** |
| `RBAC-06` | Cross-User Document Metadata Isolation | User B blocked from User A doc | Returns HTTP 403 Forbidden | **PASS** |
| `RBAC-07` | Cross-User Analysis Isolation | User B blocked from User A analysis | Returns HTTP 403 Forbidden | **PASS** |
| `RBAC-08` | Admin Super-Access to Any Document | Admin can inspect any document | Returns HTTP 200 OK | **PASS** |
| `RBAC-09` | Safeguard: Deactivating Last Admin | Cannot deactivate sole admin | Returns HTTP 400 Bad Request | **PASS** |
| `RBAC-10` | Safeguard: Demoting Last Admin | Cannot demote sole admin role | Returns HTTP 400 Bad Request | **PASS** |

### Category 3: Database & Relationships (`tests/test_database.py` — 12 Tests)
| Test ID | Scenario | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :--- | :---: |
| `DB-01` | Schema Table Creation | All tables initialized | All 6 tables verified in SQLite | **PASS** |
| `DB-02` | User Entity Integrity | Enforce unique email/username | Uniqueness constraints verified | **PASS** |
| `DB-03` | Document-User Relationship | Foreign key references user | Owner relationship intact | **PASS** |
| `DB-04` | Analysis-Run Relationship | Keywords/Entities linked to run | Foreign key cascade works | **PASS** |
| `DB-05` | Audit Log Referencing User | User ID tied to audit record | Traceability maintained | **PASS** |
| `DB-06` | User API Response Sanitization | Sensitive attributes excluded | `password_hash` excluded | **PASS** |
| `DB-07` | Database Operational Health Probe | Connection check returns True | Database report healthy | **PASS** |
| `DB-08` | Admin User Listing Sanitization | Directory omits credentials | Hashes absent from JSON | **PASS** |
| `DB-09` | Document Catalog Listing | Returns user-scoped documents | Filtered by owner ID | **PASS** |
| `DB-10` | Analysis 404 Handling | Nonexistent analysis returns 404 | Returns HTTP 404 Not Found | **PASS** |
| `DB-11` | Cascade Deletion on Document | Deleting document clears runs | Child records purged | **PASS** |
| `DB-12` | Document Retrieval by ID | Single document fetch | Matches stored record | **PASS** |

### Category 4: Document Ingestion & Text Processing (`tests/test_document_ingestion.py` — 13 Tests)
| Test ID | Scenario | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :--- | :---: |
| `ING-01` | Citation-Aware Normalization | Preserves statutory citations | `Section 11(6)` preserved | **PASS** |
| `ING-02` | Legal Tokenizer | Boundary-aware token stream | Hyphens and quotes preserved | **PASS** |
| `ING-03` | Word Count Calculation | Accurate token count | Token count matches regex | **PASS** |
| `ING-04` | Ingestion File Type Validation | Whitelist `.pdf` and `.docx` | Only allowed MIME types pass | **PASS** |
| `ING-05` | PDF File Ingestion | Valid PDF text extracted | Word count > 0, pages parsed | **PASS** |
| `ING-06` | DOCX File Ingestion | Valid DOCX text extracted | Paragraphs combined cleanly | **PASS** |
| `ING-07` | Unsupported File Extension Rejection | `.exe` or `.txt` rejected | Returns HTTP 400 Bad Request | **PASS** |
| `ING-08` | Empty File Upload Rejection | 0-byte file rejected | Returns HTTP 400 Bad Request | **PASS** |
| `ING-09` | Oversized File Upload Rejection | >25 MB upload blocked | Returns HTTP 400 Bad Request | **PASS** |
| `ING-10` | Text & Metadata Retrieval Endpoints | Read extracted text by ID | Returns text and page array | **PASS** |
| `ING-11` | Corrupt PDF Error Handling | Malformed PDF handled safely | Returns HTTP 400 with detail | **PASS** |
| `ING-12` | Corrupt DOCX Error Handling | Malformed DOCX handled safely | Returns HTTP 400 with detail | **PASS** |
| `ING-13` | Nonexistent Document Text Query | Query missing doc ID | Returns HTTP 404 Not Found | **PASS** |

### Category 5: Keyword Extraction Engine (`tests/test_keyword_extraction.py` — 12 Tests)
| Test ID | Scenario | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :--- | :---: |
| `KW-01` | Candidate Generation N-Grams | Generates 1, 2, and 3-grams | Phrases extracted correctly | **PASS** |
| `KW-02` | Stopword & Noise Filtering | Strips filler words | Non-informative tokens purged | **PASS** |
| `KW-03` | Legal Vocabulary Preservation | Retains legal prepositions | Legal terms preserved | **PASS** |
| `KW-04` | RAKE Co-occurrence Scoring | Graph degree-frequency score | Multitoken phrases scored | **PASS** |
| `KW-05` | TF-IDF Scoring with Corpus | Reference corpus IDF applied | Informative words prioritized | **PASS** |
| `KW-06` | Legal Dictionary Matching | Categorizes legal terms | Categories assigned properly | **PASS** |
| `KW-07` | Score Normalization | Scales scores to $[0.0, 1.0]$ | All scores within bounds | **PASS** |
| `KW-08` | Token-Aware Frequency | Accurate term counts | Matches raw text frequency | **PASS** |
| `KW-09` | Weighted Fusion Formula | $0.35 + 0.35 + 0.30$ fusion | Accurate composite score | **PASS** |
| `KW-10` | Deterministic Viva Test Case | Consistent extraction order | Matches expected ranking | **PASS** |
| `KW-11` | End-to-End Keyword API Flow | Trigger analysis and retrieve | Returns ranked keyword list | **PASS** |
| `KW-12` | Empty Document Extraction Grace | Empty document handled safely | Returns HTTP 400 Bad Request | **PASS** |

### Category 6: Named Entity Recognition (`tests/test_entity_extraction.py` — 14 Tests)
| Test ID | Scenario | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :--- | :---: |
| `NER-01` | spaCy Service Initialization | Model loads successfully | Base entities extracted | **PASS** |
| `NER-02` | Statutory Section Extraction | Regex matches `Section \d+` | Sections tagged as `SECTION` | **PASS** |
| `NER-03` | Constitutional Article Extraction | Matches `Article \d+` | Tagged as `ARTICLE` | **PASS** |
| `NER-04` | Act & Statutory Law Extraction | Matches `[Name] Act, [Year]` | Tagged as `ACT` | **PASS** |
| `NER-05` | Judicial Court Extraction | Matches Indian & Apex Courts | Tagged as `COURT` | **PASS** |
| `NER-06` | Case Reference Extraction | Matches `W.P.(C) No. \d+` | Tagged as `CASE_NUMBER` | **PASS** |
| `NER-07` | Monetary Value Extraction | Matches Indian Rupee formats | Tagged as `MONETARY_VALUE` | **PASS** |
| `NER-08` | Date Extraction | Matches calendar dates | Tagged as `DATE` | **PASS** |
| `NER-09` | Legal Role Extraction | Matches procedural roles | Tagged as `LEGAL_ROLE` | **PASS** |
| `NER-10` | Contract Type Extraction | Matches agreement genres | Tagged as `CONTRACT_TYPE` | **PASS** |
| `NER-11` | Entity Normalization | Lowercase + whitespace trim | Canonical form stored | **PASS** |
| `NER-12` | Deduplication & Precedence | Longest-match overrides generic | Domain rules take priority | **PASS** |
| `NER-13` | Deterministic Viva Entity Case | Consistent test brief extraction | Matches expected entity set | **PASS** |
| `NER-14` | End-to-End Entity API Flow | Full extraction pipeline call | Persists entities in DB | **PASS** |

### Category 7: ASTMA IR Evaluation & Benchmarking (`tests/test_evaluation.py` — 13 Tests)
| Test ID | Scenario | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :--- | :---: |
| `EVAL-01` | Zero-Division Arithmetic Safeguard | Returns $0.0$ on zero division | Precision, Recall, $F_1 = 0.0$ | **PASS** |
| `EVAL-02` | Perfect Extraction Match | Identical gold and predicted | Precision, Recall, $F_1 = 1.0$ | **PASS** |
| `EVAL-03` | Partial Extraction Match | Disjoint and overlapping sets | Accurate fractional metrics | **PASS** |
| `EVAL-04` | Term Normalization Invariance | Case & whitespace invariance | Equal normalized matches | **PASS** |
| `EVAL-05` | Single Doc Keyword Evaluation | Real extractor against gold | Computes TP, FP, FN, $F_1$ | **PASS** |
| `EVAL-06` | Empty Predictions Keyword Eval | Zero candidate keywords | Recall = 0.0, FN = gold count | **PASS** |
| `EVAL-07` | Single Doc Entity Evaluation | Strict text + type matching | Mismatches marked as errors | **PASS** |
| `EVAL-08` | Benchmark Dataset Integrity | 12 docs and 12 paired JSONs | All files exist and are valid | **PASS** |
| `EVAL-09` | Evaluation API Unauthenticated | Reject unauthenticated calls | Returns HTTP 401 Unauthorized | **PASS** |
| `EVAL-10` | Evaluation API Summary Query | Authenticated analyst query | Returns macro/micro summary | **PASS** |
| `EVAL-11` | Evaluation API Documents List | List document-level metrics | Returns 12 document records | **PASS** |
| `EVAL-12` | Evaluation API Error Query | Query false positive/negatives | Returns classified error lists | **PASS** |
| `EVAL-13` | Benchmark Trigger RBAC | User role blocked from `/run` | Returns HTTP 403 Forbidden | **PASS** |

### Category 8: Health & Audit Observability (`tests/test_health.py` & `tests/test_audit.py` — 10 Tests)
| Test ID | Scenario | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :--- | :---: |
| `HLTH-01` | Root Service Welcome Probe | Welcome info on `/` | Returns status 'running' | **PASS** |
| `HLTH-02` | System Operational Health Probe | Database connectivity report | Returns status 'healthy' | **PASS** |
| `HLTH-03` | API v1 Architecture Discovery | Returns tier & phase info | Confirms Phase 9 architecture | **PASS** |
| `AUD-01` | Audit Event Creation | Records action in database | AuditLog row committed | **PASS** |
| `AUD-02` | Audit Event Filtering by Action | Filter audit events by enum | Filtered query matches | **PASS** |
| `AUD-03` | Audit Event Filtering by Status | Filter by SUCCESS or FAILURE | Accurate status partitioning | **PASS** |
| `AUD-04` | Audit Log Pagination | Offset and limit parameters | Returns sliced log array | **PASS** |
| `AUD-05` | Sensitive Data Masking in Audit | Passwords excluded from logs | Secrets completely absent | **PASS** |
| `AUD-06` | Admin Audit Log Query API | Admin views `/admin/audit-logs` | Returns HTTP 200 + log list | **PASS** |
| `AUD-07` | Audit Event on Unauthorized Action | Security attempt logged | Records `UNAUTHORIZED_ACCESS` | **PASS** |
