from __future__ import annotations
import requests

def pubmed_search(query: str, retmax: int = 30,
                  mindate: str = "2020/01/01", maxdate: str = "2025/12/31",
                  datetype: str = "pdat", sort: str = "pub+date") -> tuple[list[str], str]:
    """Return (pmids, total_count_str)."""
    r = requests.get(
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
        params={
            "db": "pubmed",
            "term": query,
            "retmode": "json",
            "retmax": retmax,
            "mindate": mindate,
            "maxdate": maxdate,
            "datetype": datetype,
            "sort": sort,
        },
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    ids = data["esearchresult"].get("idlist", [])
    count = data["esearchresult"].get("count", "0")
    return ids, count

def pubmed_fetch_xml(pmids: list[str]) -> str:
    if not pmids:
        raise ValueError("No PMIDs provided to fetch.")
    r = requests.get(
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
        params={"db": "pubmed", "id": ",".join(pmids), "retmode": "xml"},
        timeout=30,
    )
    r.raise_for_status()
    return r.text
