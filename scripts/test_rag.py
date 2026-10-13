from rag import ask

questions = [
    "What is HMM?",                          # answerable, acronym
    "What does a Gaussian Mixture Model do?",# answerable
    "What is the capital of France?",        # off-topic
    "What is an LSTM?",                      # on-topic, probably NOT in the PDF
    "What is a transformer?",                # on-topic, probably NOT in the PDF
]

for q in questions:
    r = ask(q)
    print("\nQ:", q)
    print("A:", r["answer"])
    print("Sources:", [(s["page"], s["score"]) for s in r["sources"]])