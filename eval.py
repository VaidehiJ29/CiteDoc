import json
import re
import sys
import time

from llm import LLMError
from rag import ask, NOT_FOUND, MIN_SCORE
from store import search

with open("eval_questions.json", encoding="utf-8") as f:
    QUESTIONS = json.load(f)


def has_keyword(text, keywords):
    text = text.lower()
    return any(k.lower() in text for k in keywords)


def run_retrieval():
    found = total = blocked = unans = 0
    for item in QUESTIONS:
        hits = search(item["q"], k=5)
        top = hits[0]["score"] if hits else 0.0
        if item["type"] == "answer":
            total += 1
            ok = has_keyword(" ".join(h["text"] for h in hits), item["keywords"])
            found += ok
            print(f"{'OK  ' if ok else 'MISS'}  top score {top:.2f}  {item['q']}")
        else:
            unans += 1
            ok = top < MIN_SCORE
            blocked += ok
            print(f"{'BLOCKED' if ok else 'PASSES CUTOFF'}  top score {top:.2f}  {item['q']}")
    print(f"\nRight passage retrieved: {found}/{total}")
    print(f"Unanswerable blocked by the score cutoff: {blocked}/{unans}")


def run_answers(provider, limit):
    items = QUESTIONS[:limit] if limit else QUESTIONS
    rows = []
    for item in items:
        start = time.time()
        try:
            answer = ask(item["q"], provider=provider)["answer"]
        except LLMError as e:
            answer = f"ERROR: {e}"
        secs = round(time.time() - start)
        refused = answer.strip().startswith(NOT_FOUND)
        cited = bool(re.search(r"\[\d+", answer))
        if item["type"] == "answer":
            good = (not refused) and has_keyword(answer, item["keywords"])
        else:
            good = refused
        rows.append({"q": item["q"], "type": item["type"], "good": good,
                     "cited": cited, "secs": secs, "answer": answer})
        print(f"{'PASS' if good else 'FAIL'}  {secs}s  {item['q']}")
        print("      ", answer[:160].replace("\n", " "))
        if provider == "gemini":
            time.sleep(4)  # stay friendly to the free-tier rate limit

    ans = [r for r in rows if r["type"] == "answer"]
    una = [r for r in rows if r["type"] != "answer"]
    print(f"\n=== {provider} ===")
    print(f"Answerable correct: {sum(r['good'] for r in ans)}/{len(ans)}")
    print(f"Answerable with a citation: {sum(r['cited'] for r in ans)}/{len(ans)}")
    print(f"Unanswerable correctly refused: {sum(r['good'] for r in una)}/{len(una)}")
    print(f"Average seconds per question: {sum(r['secs'] for r in rows) // max(len(rows), 1)}")
    with open(f"results_{provider}.json", "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)


mode = sys.argv[1]
if mode == "retrieval":
    run_retrieval()
else:
    run_answers(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 0)