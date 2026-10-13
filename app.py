import os
import re
import streamlit as st

from store import index_pdf, count, list_documents
from rag import ask
from llm import LLMError

st.set_page_config(page_title="CiteDoc", page_icon="📄")
st.title("CiteDoc")
st.caption("Ask your PDFs. Get answers with page-numbered proof.")

os.makedirs("data", exist_ok=True)


def cited_numbers(answer: str) -> list[int]:
    nums = set()
    for group in re.findall(r"\[([\d,\s]+)\]", answer):
        nums.update(int(n) for n in re.findall(r"\d+", group))
    return sorted(nums)


def show_sources(sources: list[dict], answer: str):
    cited = [n for n in cited_numbers(answer) if 1 <= n <= len(sources)]
    if not cited:
        return
    with st.expander(f"Sources ({len(cited)})"):
        for n in cited:
            s = sources[n - 1]
            st.markdown(f"**[{n}] {s['file']}, page {s['page']}**  (match {s['score']})")
            st.write(s["text"])


# ---------- sidebar ----------
with st.sidebar:
    st.header("Documents")
    files = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)
    mark_conf = st.checkbox("These files are confidential", value=True)
    if files and st.button("Index uploaded PDFs"):
        for f in files:
            path = os.path.join("data", os.path.basename(f.name))
            with open(path, "wb") as out:
                out.write(f.getbuffer())
            with st.spinner(f"Indexing {f.name}..."):
                n = index_pdf(path, confidential=mark_conf)
            if n:
                st.success(f"{f.name}: {n} chunks")
            else:
                st.warning(f"{f.name}: no text found (scanned PDF?)")

    docs = list_documents()
    st.write(f"Chunks in database: {count()}")
    if docs:
        st.subheader("Indexed documents")
        for name, conf in sorted(docs.items()):
            st.write(("🔒 " if conf else "🌐 ") + name)

    st.header("Answer with")
    mode = st.radio(
        "Model", ["Local (Ollama)", "Cloud (Gemini)"], index=0, label_visibility="collapsed"
    )
    if mode.startswith("Cloud"):
        st.warning("Cloud mode sends your question and matching passages to Google.")
        hidden = sum(1 for c in docs.values() if c)
        if hidden:
            st.info(f"{hidden} confidential document(s) are excluded in cloud mode.")
    else:
        st.info("Local mode: nothing leaves your computer. Answers take a few minutes.")

provider = "gemini" if mode.startswith("Cloud") else "ollama"

# ---------- chat ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])
        if m["role"] == "assistant":
            show_sources(m.get("sources", []), m["content"])

question = st.chat_input("Ask a question about your documents")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching and answering..."):
            try:
                result = ask(question, provider=provider)
                answer, sources = result["answer"], result["sources"]
            except LLMError as e:
                answer, sources = f"Sorry, the model call failed: {e}", []
        st.write(answer)
        show_sources(sources, answer)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer, "sources": sources}
    )