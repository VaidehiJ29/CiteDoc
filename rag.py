from store import search
from llm import generate

TOP_K = 5
CLOUD_PROVIDERS = {"gemini"}  # anything listed here can never see confidential documents
MIN_SCORE = 0.25  # provisional: we tune this with real tests
NOT_FOUND = "I couldn't find this in your documents."


def build_prompt(question: str, hits: list[dict]) -> str:
    sources = "\n\n".join(
        f"[{i}] ({h['file']}, page {h['page']})\n{h['text']}"
        for i, h in enumerate(hits, start=1)
    )
    return f"""You answer questions using ONLY the numbered sources below.

Rules:
- If the sources do not contain the answer, reply with exactly: {NOT_FOUND}
- Never use outside knowledge, even if you know the answer.
- End every sentence with a source number like [1] or [2]. Do not write any sentence you cannot support with a source.
- Be concise.

SOURCES:
{sources}

QUESTION: {question}

ANSWER:"""


def ask(question: str, provider: str = "gemini") -> dict:
    public_only = provider in CLOUD_PROVIDERS
    hits = [
        h
        for h in search(question, k=TOP_K, public_only=public_only)
        if h["score"] >= MIN_SCORE
    ]
    if not hits:
        return {"answer": NOT_FOUND, "sources": []}
    answer = generate(build_prompt(question, hits), provider=provider)
    if answer.strip().startswith(NOT_FOUND):
        return {"answer": NOT_FOUND, "sources": []}
    return {"answer": answer, "sources": hits}