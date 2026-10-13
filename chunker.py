def _split(text: str, max_chars: int, overlap: int) -> list[str]:
    pieces = []
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        if end < len(text):
            # try to end on a sentence boundary instead of mid-sentence
            cut = text.rfind(". ", start + max_chars // 2, end)
            if cut != -1:
                end = cut + 1
        piece = text[start:end].strip()
        if piece:
            pieces.append(piece)
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return pieces


def chunk_pages(pages: list[dict], max_chars: int = 800, overlap: int = 150) -> list[dict]:
    chunks = []
    for p in pages:
        text = " ".join(p["text"].split())  # tidy up line breaks and extra spaces
        if len(text) < 20:
            continue  # empty or scanned page: nothing to index
        for i, piece in enumerate(_split(text, max_chars, overlap)):
            chunks.append({
                "id": f"{p['file']}::p{p['page']}::c{i}",
                "file": p["file"],
                "page": p["page"],
                "text": piece,
            })
    return chunks