from __future__ import annotations
import argparse
import getpass
from src.docuchat_medreview.config import settings
from src.docuchat_medreview.pubmed import pubmed_search, pubmed_fetch_xml
from src.docuchat_medreview.parse import parse_pubmed_xml
from src.docuchat_medreview.index import build_faiss_index

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--query", required=True)
    p.add_argument("--retmax", type=int, default=40)
    p.add_argument("--mindate", default="2020/01/01")
    p.add_argument("--maxdate", default="2025/12/31")
    args = p.parse_args()

    api_key = getpass.getpass("Paste OpenAI API key: ").strip()
    s = settings()
    s.index_dir.mkdir(parents=True, exist_ok=True)

    pmids, count = pubmed_search(args.query, retmax=args.retmax, mindate=args.mindate, maxdate=args.maxdate)
    print(f"Total PubMed hits: {count} | Fetching: {len(pmids)} PMIDs")

    xml = pubmed_fetch_xml(pmids)
    docs = parse_pubmed_xml(xml)
    print(f"Parsed abstracts with text: {len(docs)}")

    _, chunks = build_faiss_index(docs, api_key=api_key, out_dir=s.index_dir)
    print(f"Chunks indexed: {len(chunks)}")
    print(f"✅ Index saved to: {s.index_dir}")

if __name__ == "__main__":
    main()
