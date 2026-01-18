from pathlib import Path
from typing import List

from pypdf import PdfReader


def load_pdf_pages(path: Path) -> List[str]:
    reader = PdfReader(str(path))
    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    return pages
