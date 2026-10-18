from typing import Dict, Any, List
import docx


def extract_docx_text(file_path: str) -> Dict[str, Any]:
    """
    Extracts text from Microsoft Word (.docx) documents, including paragraphs and tables.
    DOCX has no explicit native page stream, so page_count is explicitly None.
    Returns:
        {
            "file_type": "docx",
            "page_count": None,
            "pages": List[Dict[str, Any]],
            "raw_text": str,
            "warning": Optional[str]
        }
    """
    try:
        doc = docx.Document(file_path)
    except Exception as exc:
        raise ValueError(f"Corrupt or unreadable DOCX document: {exc}")

    extracted_chunks: List[str] = []

    # 1. Extract paragraphs
    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()
        if text:
            extracted_chunks.append(text)

    # 2. Extract tables where present
    for table in doc.tables:
        for row in table.rows:
            row_cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if row_cells:
                # Join row cells with separator to preserve table context
                extracted_chunks.append(" | ".join(row_cells))

    raw_text = "\n\n".join(extracted_chunks)

    warning = None
    if not raw_text.strip():
        warning = "DOCX file contains no extractable paragraphs or table text."

    # Return structured representation without fabricating page numbers
    pages = [{
        "page_number": 1,
        "text": raw_text
    }]

    return {
        "file_type": "docx",
        "page_count": None,  # Strictly None for DOCX
        "pages": pages,
        "raw_text": raw_text,
        "warning": warning
    }
