# LexExtract — 60-Second Elevator Pitch (Concept Guide)

## Concept Overview
*This explanation is designed to be delivered comfortably in under 60 seconds without sounding rehearsed.*

---

## The 60-Second Explanation

> "Legal contracts and court judgments are long, complex documents filled with archaic language and dense statutory citations. Standard NLP tools struggle with them because generic text cleaning strips out essential punctuation—damaging citations like *Section 11(6)*—and off-the-shelf entity taggers often misclassify high courts as generic commercial companies.
>
> We developed **LexExtract**, an intelligent legal document processing and information retrieval system built on a Three-Tier enterprise architecture using React 18, FastAPI, and SQLAlchemy. 
>
> When a practitioner uploads a PDF or Word document, our citation-preserving parser extracts the text. A tri-model scoring engine fuses TF-IDF, RAKE graph scoring, and a 1,200-term legal lexicon to extract ranked concepts, while specialized gazetteers paired with spaCy extract courts, statutes, and monetary figures.
>
> Users can inspect highlighted terms in an interactive document viewer, and analysts can run a real empirical IR evaluation against a 12-document legal ground-truth benchmark. 
>
> The system enforces role-based access control, document isolation, and audit logging, and is verified by 98 passing backend tests."

---

## Memory Anchors (Key Points to Remember)
1. **The Problem:** Long legal briefs; generic NLP breaks citations like `Section 11(6)` and misclassifies courts.
2. **The Architecture:** Three-Tier (React SPA + FastAPI + SQLAlchemy ORM).
3. **The Extraction Engine:** TF-IDF + RAKE + 1,200-term legal lexicon for keywords; spaCy + regex gazetteers for 13 entity types.
4. **The User Experience:** Interactive highlighted document viewer with multi-layer overlays.
5. **The Academic Rigor:** Built-in ASTMA evaluation benchmark (12 documents) and 98 passing automated tests.
