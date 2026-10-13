import sys
from pdf_reader import extract_pages

pages = extract_pages(sys.argv[1])
empty = [p["page"] for p in pages if len(p["text"]) < 20]

print("Pages:", len(pages))
print("Pages with (almost) no text:", empty)
print("--- Page 1 preview ---")
print(pages[0]["text"][:300])