from rag import ask

r = ask("What does a Gaussian Mixture Model do?")
print(r["answer"], "\n")
for i, s in enumerate(r["sources"], start=1):
    print(f"[{i}] page {s['page']}, score {s['score']}")
    print("   ", s["text"][:200], "\n")