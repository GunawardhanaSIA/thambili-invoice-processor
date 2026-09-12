"""Detect whether a PDF is text-based or scanned, and extract its text.

Text-based PDFs are read directly with PyMuPDF (fitz), which is fast and free.
Scanned PDFs (image-only pages) are rasterized with PyMuPDF and OCR'd with
EasyOCR (also free, pure-Python/pip install, no external binary required —
its model weights are downloaded automatically on first use).
"""

from dataclasses import dataclass
from functools import lru_cache

import easyocr
import fitz  # PyMuPDF
import numpy as np

# A page is considered "text" if it yields at least this many extractable
# characters; otherwise it's treated as a scanned/image page.
MIN_CHARS_PER_PAGE = 20


@dataclass
class ExtractionResult:
    pdf_type: str  # "text" or "scanned"
    page_count: int
    text: str


@lru_cache(maxsize=1)
def _get_ocr_reader() -> easyocr.Reader:
    return easyocr.Reader(["en"])


def _page_to_array(page: fitz.Page, dpi: int) -> np.ndarray:
    zoom = dpi / 72
    matrix = fitz.Matrix(zoom, zoom)
    pixmap = page.get_pixmap(matrix=matrix)
    return np.frombuffer(pixmap.samples, dtype=np.uint8).reshape(
        pixmap.height, pixmap.width, pixmap.n
    )


def extract_pdf_text(pdf_bytes: bytes, ocr_dpi: int = 300) -> ExtractionResult:
    """Detect PDF type and extract its text.

    A PDF is classified as "text" if every page already contains extractable
    text (native PDF text layer). If any page has no meaningful text layer,
    the whole document is treated as scanned and OCR is used for the pages
    that lack one.
    """
    document = fitz.open(stream=pdf_bytes, filetype="pdf")
    try:
        page_texts: list[str] = []
        is_scanned = False

        for page in document:
            page_text = page.get_text().strip()
            if len(page_text) >= MIN_CHARS_PER_PAGE:
                page_texts.append(page_text)
            else:
                is_scanned = True
                image = _page_to_array(page, ocr_dpi)
                ocr_lines = _get_ocr_reader().readtext(image, detail=0)
                page_texts.append("\n".join(ocr_lines).strip())

        return ExtractionResult(
            pdf_type="scanned" if is_scanned else "text",
            page_count=document.page_count,
            text="\n\n".join(page_texts).strip(),
        )
    finally:
        document.close()
