# CiteDoc

**Ask your PDFs. Get answers with page-numbered proof.**

CiteDoc is a small retrieval-augmented generation (RAG) app. It finds the passages in your PDFs that match a question, then has a language model answer using *only* those passages, citing file and page. If the documents don't contain the answer, it says so instead of guessing.



## Why this exists

A generic chatbot can't see your files and may confidently invent an answer. CiteDoc searches your documents first and shows the exact passages behind every answer, so you can check them.

## Privacy by design

Each document is marked **confidential** or **public** when you upload it.

- **Local mode** (default): questions are answered by a model running on your own computer through [Ollama](https://ollama.com). Nothing leaves your machine.
- **Cloud mode**: answers come from the Gemini API. In this mode, confidential documents are **excluded from search before anything is sent**, so their text can never reach the cloud model, whatever is ticked in the sidebar.
- New uploads default to confidential, and a document with a missing flag is treated as confidential.

## How it works

1. **Read** each PDF page by page (PyMuPDF), keeping file name and page number.
2. **Chunk** each page into ~800-character passages with overlap. Chunks never cross a page boundary.
3. **Embed** the chunks locally with `all-MiniLM-L6-v2` and store them in ChromaDB.
4. **Search**: embed the question and fetch the 5 most similar passages. If the best match scores below a cutoff, answer "I couldn't find this in your documents" without calling any model.
5. **Answer**: the model gets the passages and strict rules (use only these sources, cite `[n]`, refuse if unsupported).

No LangChain or similar framework, so every step is plain Python.

## Setup (Windows, Python 3.12)

```
git clone <your-repo-url>
cd citedoc
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Cloud mode (optional):** create a free key in Google AI Studio and put it in a `.env` file:

```
GEMINI_API_KEY=your_key_here
```

Free-tier limits and terms change, and free-tier content may be used by Google to improve its products, so use cloud mode only with non-confidential files.

**Local mode:** install [Ollama](https://ollama.com), then:

```
ollama pull llama3.1:8b
```

Optional: set the `OLLAMA_MODELS` environment variable first to store the model on another drive.

## Run

```
streamlit run app.py
```

Upload a PDF in the sidebar, choose whether it is confidential, click **Index**, then ask questions. For a demo, untick "confidential" so Cloud mode can use it.

## Evaluation

`eval.py` runs a set of questions with known answers (`eval_questions.json`) and reports retrieval hits, correct answers, citation presence, and correct refusals on questions the document doesn't answer.

First run (6 questions on a 12-chunk set of study notes; a very small test, being expanded):

| | Gemini | Ollama (llama3.1:8b) |
|---|---|---|
| Answerable questions correct | 3/3 | 3/3 |
| Answers with a citation | 3/3 | 3/3 |
| Unanswerable correctly refused | 3/3 | 3/3 |

Local answers took roughly 1 to 4 minutes each on a laptop with about 7 GB of usable RAM.

## Project layout

- `app.py`: Streamlit interface
- `pdf_reader.py`, `chunker.py`, `store.py`: reading, chunking, embedding and search
- `rag.py`: prompt, score cutoff, and the cloud/confidential rule
- `llm.py`: one `generate()` function that switches between Gemini and Ollama
- `eval.py`, `eval_questions.json`: evaluation
- `scripts/`: small experiments and checks used during development
- `samples/`: a sample PDF (the author's own study notes)

## Known limitations

- Scanned PDFs (images of text) aren't supported; there is no OCR.
- Confidentiality is per document, not per page, and protects what is sent to the cloud model, not the files on disk.
- The score cutoff (0.25) was set from a handful of questions and needs more testing.
- Small local models cite less reliably than Gemini and can still add uncited sentences.
- Local answers are slow on CPU-only hardware.

## License

To be added. Note that PyMuPDF is AGPL-licensed.