import chromadb
from sentence_transformers import SentenceTransformer

from pdf_reader import extract_pages
from chunker import chunk_pages

_model = SentenceTransformer("all-MiniLM-L6-v2")
_client = chromadb.PersistentClient(path="chroma_db")
_col = _client.get_or_create_collection(
    name="citedoc", metadata={"hnsw:space": "cosine"}
)


def _embed(texts: list[str]) -> list[list[float]]:
    return _model.encode(texts, normalize_embeddings=True).tolist()


def index_pdf(pdf_path: str, confidential: bool = True) -> int:
    """Index one PDF. Re-indexing the same file replaces it, with no duplicates."""
    chunks = chunk_pages(extract_pages(pdf_path))
    if not chunks:
        return 0
    _col.delete(where={"file": chunks[0]["file"]})
    _col.upsert(
        ids=[c["id"] for c in chunks],
        documents=[c["text"] for c in chunks],
        embeddings=_embed([c["text"] for c in chunks]),
        metadatas=[
            {"file": c["file"], "page": c["page"], "confidential": confidential}
            for c in chunks
        ],
    )
    return len(chunks)


def search(question: str, k: int = 5, public_only: bool = False) -> list[dict]:
    kwargs = {}
    if public_only:
        kwargs["where"] = {"confidential": False}
    res = _col.query(query_embeddings=_embed([question]), n_results=k, **kwargs)
    hits = []
    for text, meta, dist in zip(
        res["documents"][0], res["metadatas"][0], res["distances"][0]
    ):
        hits.append({
            "file": meta["file"],
            "page": meta["page"],
            "text": text,
            "score": round(1 - dist, 3),
        })
    return hits


def list_documents() -> dict:
    """Return {file name: is_confidential}. A missing flag counts as confidential."""
    metas = _col.get(include=["metadatas"])["metadatas"]
    docs = {}
    for m in metas:
        docs[m["file"]] = m.get("confidential", True)
    return docs


def count() -> int:
    return _col.count()