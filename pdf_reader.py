import os
import pymupdf


def extract_pages(pdf_path: str) -> list[dict]:
    """Return one record per page: file name, page number (starting at 1), text."""
    file_name = os.path.basename(pdf_path)
    pages = []
    with pymupdf.open(pdf_path) as doc:
        for number, page in enumerate(doc, start=1):
            text = page.get_text().strip()
            pages.append({"file": file_name, "page": number, "text": text})
    return pages