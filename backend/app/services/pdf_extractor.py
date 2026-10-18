from typing import Dict, Any, List
import pymupdf


def extract_pdf_text(file_path: str) -> Dict[str, Any]:
    """
    Extracts structured page-by-page text from a PDF file using PyMuPDF.
    Returns:
        {
            "file_type": "pdf",
            "page_count": int,
            "pages": List[Dict[str, Any]],
            "raw_text": str,
            "warning": Optional[str]
        }
    """
    try:
        doc = pymupdf.open(file_path)
    except Exception as exc:
        raise ValueError(f"Corrupt or unreadable PDF document: {exc}")

    try:
        page_count = doc.page_count
        pages: List[Dict[str, Any]] = []
        combined_text_chunks: List[str] = []

        for page_idx in range(page_count):
            page = doc.load_page(page_idx)
            page_text = page.get_text("text") or ""
            pages.append({
                "page_number": page_idx + 1,
                "text": page_text
            })
            if page_text.strip():
                combined_text_chunks.append(page_text)

        raw_text = "\n\n".join(combined_text_chunks)

        # Detect image-only / scanned PDFs without extractable text
        warning = None
        if not raw_text.strip():
            warning = "PDF contains little or no extractable text. OCR is not enabled in this version."

        return {
            "file_type": "pdf",
            "page_count": page_count,
            "pages": pages,
            "raw_text": raw_text,
            "warning": warning
        }
    finally:
        doc.close()
