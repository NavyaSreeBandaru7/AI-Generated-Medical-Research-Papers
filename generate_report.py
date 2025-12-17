from __future__ import annotations
import argparse
import getpass
import json
import time
from src.docuchat_medreview.config import settings
from src.docuchat_medreview.rag import load_index, format_context, format_sources
from src.docuchat_medreview.report import write_markdown, write_audit_json, build_pdf_report
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--topic", required=True)
    args = p.parse_args()

    api_key = getpass.getpass("Paste OpenAI API key: ").strip()
    s = settings()
    s.exports_dir.mkdir(parents=True, exist_ok=True)

    _, retriever = load_index(api_key)
    llm = ChatOpenAI(model=s.chat_model, temperature=s.temperature, api_key=api_key)

    # Retrieve context
    docs = retriever.invoke(args.topic)
    ctx = format_context(docs)
    sources = format_sources(docs)

    # Mini-review
    review_prompt = ChatPromptTemplate.from_messages([
        ("system",
         "Write a concise mini-review based ONLY on the provided abstracts.\n"
         "Requirements:\n"
         "- Use markdown headings.\n"
         "- Every key claim must include PMID citations.\n"
         "- Do not invent numbers not present.\n"
         "- End with a 'Not medical advice' note."),
        ("human", "Topic: {topic}\n\nAbstract context:\n{ctx}\n\nMini-review:")
    ])
    review_chain = review_prompt | llm | StrOutputParser()
    review_md = review_chain.invoke({"topic": args.topic, "ctx": ctx})

    # Claim-evidence table (escaped braces)
    claims_prompt = ChatPromptTemplate.from_messages([
        ("system",
         "Extract 6–10 verifiable claims supported by the provided abstracts.\n"
         "Return STRICT JSON ONLY in this exact schema:\n"
         "{{\"claims\": [{{\"claim\": \"...\", \"evidence\": \"short quote/paraphrase\", \"pmid\": \"12345678\"}}]}}\n"
         "Rules: only use PMIDs present in context; if unsure, omit the claim."),
        ("human", "Context:\n{ctx}")
    ])
    claims_chain = claims_prompt | llm | StrOutputParser()

    raw = claims_chain.invoke({"ctx": ctx})
    data = json.loads(raw)
    claims = data.get("claims", [])

    ts = time.strftime("%Y%m%d-%H%M%S")
    md_path = s.exports_dir / f"mini_review_{ts}.md"
    json_path = s.exports_dir / f"audit_{ts}.json"
    pdf_path = s.exports_dir / f"report_{ts}.pdf"

    write_markdown(review_md, md_path)
    write_audit_json({"topic": args.topic, "sources": sources, "claims": claims}, json_path)
    build_pdf_report("DocuChat MedReview Report", args.topic, review_md, claims, sources, pdf_path)

    print("✅ Saved:")
    print("-", md_path)
    print("-", json_path)
    print("-", pdf_path)

if __name__ == "__main__":
    main()
