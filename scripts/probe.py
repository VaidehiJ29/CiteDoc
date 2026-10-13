from store import search

questions = [
    # answerable (edit these to match your PDF)
    "What is HMM?",
    "What is a Hidden Markov Model?",
    "What does a Gaussian Mixture Model do?",
    "How do autoencoders compress data?",
    # NOT in the PDF
    "What is the capital of France?",
    "How do I bake sourdough bread?",
]

for q in questions:
    hits = search(q, k=3)
    scores = [h["score"] for h in hits]
    print(f"\nQ: {q}")
    print("  top-3 scores:", scores, "| top page:", hits[0]["page"])
    print("  top chunk:", hits[0]["text"][:400].replace("\n", " "))