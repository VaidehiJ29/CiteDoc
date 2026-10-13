from rag import ask

r = ask("What does a Gaussian Mixture Model do?")
print("END of source [1]:\n", r["sources"][0]["text"][-220:])