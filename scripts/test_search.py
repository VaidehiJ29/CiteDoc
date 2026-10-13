import sys
from store import index_pdf, search, count

pdf = sys.argv[1]
question = sys.argv[2]

print("Chunks indexed:", index_pdf(pdf))
print("Total in database:", count())

for h in search(question):
    print(f"\n[{h['file']} p.{h['page']}  score {h['score']}]")
    print(h["text"][:250])