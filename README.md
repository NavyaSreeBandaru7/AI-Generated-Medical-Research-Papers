# DocuChat MedReview — Evidence-Backed Medical Mini-Review (PubMed + RAG)

This project builds an **evidence-backed** literature assistant using:
- PubMed E-utilities (ESearch + EFetch) to pull real abstracts
- Chunking + embeddings + FAISS for semantic retrieval
- A grounded LLM prompt that cites **PMIDs**
- Optional audit outputs: claim→evidence→PMID + basic QC

> Note: This tool is for research support only. It is **not medical advice**.

## 1) Setup (local or Colab)
```bash
pip install -r requirements.txt
```

## 2) Add your OpenAI key (manual paste; not stored)
This repo avoids storing keys in code or git.
You paste the key at runtime when prompted.

## 3) Ingest PubMed abstracts (build FAISS index)
Example:
```bash
python ingest_pubmed.py --query "SGLT2 inhibitors heart failure outcomes" --retmax 40 --mindate 2020/01/01 --maxdate 2025/12/31
```

This creates:
- `indexes/faiss_index/` (FAISS index + store)

## 4) Ask questions (interactive CLI)
```bash
python app_cli.py
```

## 5) Generate a mini-review + audit files (+ PDF)
```bash
python generate_report.py --topic "SGLT2 inhibitors and heart failure outcomes"
```

Outputs in `exports/`:
- `mini_review_*.md`
- `audit_*.json`
- `report_*.pdf`

## Colab note
If you run in Colab, use the same scripts, or copy the code blocks into cells.
Never commit `.env` or keys.
