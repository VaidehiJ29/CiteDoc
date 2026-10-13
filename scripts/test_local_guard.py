import time
from rag import ask

t = time.time()
r = ask("What is an LSTM?", provider="ollama")
print(r["answer"])
print("Sources:", [(s["page"], s["score"]) for s in r["sources"]])
print("Seconds:", round(time.time() - t))