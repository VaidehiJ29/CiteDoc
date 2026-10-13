import sys
from pdf_reader import extract_pages
from chunker import chunk_pages

pages = extract_pages(sys.argv[1])
chunks = chunk_pages(pages)

lengths = [len(c["text"]) for c in chunks]
print("Pages:", len(pages), "| Chunks:", len(chunks))
print("Shortest / average / longest chunk:", min(lengths), sum(lengths) // len(lengths), max(lengths))
print("Duplicate IDs:", len(chunks) - len({c["id"] for c in chunks}))
for c in chunks[:2]:
    print("\n", c["id"], "\n", c["text"])