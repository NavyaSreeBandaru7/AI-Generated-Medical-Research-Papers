from __future__ import annotations
import xml.etree.ElementTree as ET
from langchain_core.documents import Document

def _t(elem, path: str) -> str:
    x = elem.find(path)
    return (x.text or "").strip() if x is not None and x.text else ""

def parse_pubmed_xml(xml_text: str) -> list[Document]:
    """Parse PubMed EFetch XML into Documents. Skips entries without abstracts."""
    root = ET.fromstring(xml_text)
    docs: list[Document] = []

    for art in root.findall(".//PubmedArticle"):
        pmid = _t(art, ".//MedlineCitation/PMID")
        title = _t(art, ".//Article/ArticleTitle")
        journal = _t(art, ".//Article/Journal/Title")
        year = _t(art, ".//Article/Journal/JournalIssue/PubDate/Year")

        abs_texts = [("".join(a.itertext())).strip() for a in art.findall(".//Abstract/AbstractText")]
        abstract = "\n".join([t for t in abs_texts if t])

        if not abstract:
            continue

        page = f"PMID:{pmid}\nTitle: {title}\nJournal: {journal} ({year})\n\nAbstract:\n{abstract}".strip()
        docs.append(Document(
            page_content=page,
            metadata={
                "pmid": pmid,
                "title": title,
                "journal": journal,
                "year": year,
                "source": f"PMID:{pmid}",
            }
        ))
    return docs
