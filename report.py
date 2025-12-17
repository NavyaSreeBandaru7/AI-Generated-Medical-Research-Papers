from __future__ import annotations
import json, time
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

def write_markdown(text: str, out_path: Path):
    out_path.write_text(text, encoding="utf-8")

def write_audit_json(payload: dict, out_path: Path):
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

def build_pdf_report(title: str, topic: str, review_md: str, claims: list[dict], sources: list[str], out_path: Path):
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(str(out_path), pagesize=letter,
                            leftMargin=0.8*inch, rightMargin=0.8*inch,
                            topMargin=0.75*inch, bottomMargin=0.75*inch)

    story = []
    story.append(Paragraph(title, styles["Title"]))
    story.append(Paragraph(f"<b>Topic:</b> {topic}", styles["Normal"]))
    story.append(Paragraph(f"<b>Generated:</b> {time.strftime('%Y-%m-%d %H:%M')}", styles["Normal"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Mini-review (generated from retrieved abstracts)", styles["Heading2"]))
    # Keep it readable: convert simple markdown-ish lines into paragraphs
    for line in review_md.splitlines():
        line = line.strip()
        if not line:
            story.append(Spacer(1, 6))
            continue
        if line.startswith("#"):
            level = min(line.count("#"), 3)
            text = line.lstrip("#").strip()
            story.append(Paragraph(text, styles["Heading" + str(level)]))
        else:
            story.append(Paragraph(line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"), styles["Normal"]))

    story.append(Spacer(1, 12))
    story.append(Paragraph("Claim-Evidence Table (audit)", styles["Heading2"]))

    table_data = [["#", "Claim", "Evidence", "PMID"]]
    for i, c in enumerate(claims, 1):
        table_data.append([str(i), c.get("claim",""), c.get("evidence",""), c.get("pmid","")])

    tbl = Table(table_data, colWidths=[0.35*inch, 2.3*inch, 2.8*inch, 0.9*inch])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 8),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.whitesmoke, colors.white]),
    ]))
    story.append(tbl)

    story.append(Spacer(1, 12))
    story.append(Paragraph("Sources (PMIDs)", styles["Heading2"]))
    for s in sources:
        story.append(Paragraph(s, styles["Normal"]))

    story.append(Spacer(1, 12))
    story.append(Paragraph("<b>Not medical advice:</b> This report summarizes research abstracts and is not a substitute for professional medical consultation.", styles["Normal"]))

    doc.build(story)
