from store import search

hits = search("What is a Hidden Markov Model?", k=5)
for i, h in enumerate(hits, start=1):
    t = h["text"].lower()
    print(f"[{i}] page {h['page']}: mentions 'speech': {'speech' in t}, "
          f"'natural language': {'natural language' in t}")