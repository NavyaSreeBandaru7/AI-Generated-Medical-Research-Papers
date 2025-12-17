from __future__ import annotations
import getpass
from src.docuchat_medreview.rag import build_chat

def main():
    api_key = getpass.getpass("Paste OpenAI API key: ").strip()
    ask = build_chat(api_key)

    print("\n✅ DocuChat MedReview ready. Type /exit to quit.\n")
    while True:
        q = input("You: ").strip()
        if not q:
            continue
        if q.lower() in ["/exit", "exit", "quit"]:
            break
        answer, sources = ask(q)
        print("\nAI:", answer)
        print("\nSources:")
        for s in sources:
            print("-", s)
        print()

if __name__ == "__main__":
    main()
