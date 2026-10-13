import time
from llm import generate
from rag import ask

t = time.time()
print(generate("Reply with exactly: local works.", provider="ollama"))
print("Seconds:", round(time.time() - t), "\n")

t = time.time()
r = ask("What is a Hidden Markov Model?", provider="ollama")
print(r["answer"])
print("Sources:", [(s["page"], s["score"]) for s in r["sources"]])
print("Seconds:", round(time.time() - t))