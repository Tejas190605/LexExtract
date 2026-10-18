import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Singleton / Application-level cache for spaCy NLP model
_SPACY_NLP_CACHE = None
_SPACY_INITIALIZATION_ATTEMPTED = False
_SPACY_AVAILABLE = False

# Mapping from spaCy's standard OntoNotes 5.0 label set to LexExtract Legal Taxonomy
SPACY_TO_LEGAL_TYPE_MAP: Dict[str, str] = {
    "PERSON": "PERSON",
    "ORG": "ORGANIZATION",
    "GPE": "LOCATION",
    "LOC": "LOCATION",
    "DATE": "DATE",
    "MONEY": "MONEY"
}


def get_spacy_nlp():
    """
    Initializes and returns the shared spaCy model instance (en_core_web_sm).
    Guarantees the model is loaded only once across the application lifecycle.
    If the model is unavailable, logs a descriptive warning and disables spaCy extraction
    gracefully without crashing the server.
    """
    global _SPACY_NLP_CACHE, _SPACY_INITIALIZATION_ATTEMPTED, _SPACY_AVAILABLE

    if _SPACY_INITIALIZATION_ATTEMPTED:
        return _SPACY_NLP_CACHE

    _SPACY_INITIALIZATION_ATTEMPTED = True

    try:
        import spacy
        logger.info("Initializing spaCy model 'en_core_web_sm' for legal entity extraction...")
        # Disable unneeded pipeline components for speed (tagger, parser, lemmatizer)
        # Retain ner
        _SPACY_NLP_CACHE = spacy.load("en_core_web_sm", disable=["tagger", "parser", "attribute_ruler", "lemmatizer"])
        _SPACY_AVAILABLE = True
        logger.info("spaCy model 'en_core_web_sm' successfully initialized.")
    except Exception as exc:
        logger.warning(
            f"spaCy model 'en_core_web_sm' could not be loaded: {exc}. "
            "Statistical NER will be disabled. To install, run: python -m spacy download en_core_web_sm"
        )
        _SPACY_NLP_CACHE = None
        _SPACY_AVAILABLE = False

    return _SPACY_NLP_CACHE


def is_spacy_available() -> bool:
    """Returns True if the spaCy model is initialized and available."""
    get_spacy_nlp()
    return _SPACY_AVAILABLE


def extract_spacy_entities(text: str) -> List[Dict[str, Any]]:
    """
    Extracts statistical named entities using spaCy and maps labels into
    LexExtract's controlled legal taxonomy.

    Returns:
    [
      {
        "text": ent.text,
        "entity_type": mapped_type,
        "confidence": 0.75,
        "source": "spacy",
        "start_position": ent.start_char,
        "end_position": ent.end_char
      }
    ]
    """
    if not text:
        return []

    nlp = get_spacy_nlp()
    if nlp is None:
        return []

    # Run spaCy doc
    doc = nlp(text)
    entities: List[Dict[str, Any]] = []

    for ent in doc.ents:
        mapped_type = SPACY_TO_LEGAL_TYPE_MAP.get(ent.label_)
        if not mapped_type:
            continue

        clean_text = ent.text.strip()
        if not clean_text or len(clean_text) <= 1:
            continue

        entities.append({
            "text": clean_text,
            "entity_type": mapped_type,
            "confidence": 0.75,
            "source": "spacy",
            "start_position": ent.start_char,
            "end_position": ent.end_char
        })

    return entities
