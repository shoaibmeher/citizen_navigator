# utils/pdf_filler.py
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from pathlib import Path

def generate_application_pdf(service_key: str, form_data: dict, eligibility: bool, reasons: list,
                             explanation_en: str, required_docs: list, file_path: Path):
    c = canvas.Canvas(str(file_path), pagesize=A4)
    width, height = A4
    x = 20 * mm
    y = height - 20 * mm

    # Header
    c.setFont("Helvetica-Bold", 14)
    c.drawString(x, y, "Citizen Service Navigator — Application Summary")
    y -= 8 * mm
    c.setFont("Helvetica", 11)
    c.drawString(x, y, f"Service: {service_key}")
    y -= 6 * mm
    c.drawString(x, y, f"Decision: {'Eligible' if eligibility else 'Not eligible'}")
    y -= 10 * mm

    # Applicant info
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x, y, "Applicant Information")
    y -= 7 * mm
    c.setFont("Helvetica", 10)
    for k, v in form_data.items():
        c.drawString(x, y, f"- {k}: {v}"[:120])
        y -= 5 * mm
        if y < 30 * mm:
            c.showPage()
            y = height - 20 * mm
            c.setFont("Helvetica", 10)

    # Reasons
    y -= 4 * mm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x, y, "Reasons")
    y -= 7 * mm
    c.setFont("Helvetica", 10)
    if reasons:
        for r in reasons:
            c.drawString(x, y, f"- {r}"[:120])
            y -= 5 * mm
            if y < 30 * mm:
                c.showPage()
                y = height - 20 * mm
                c.setFont("Helvetica", 10)
    else:
        c.drawString(x, y, "- N/A")
        y -= 5 * mm

    # Explanation
    y -= 4 * mm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x, y, "Plain-language Explanation (English)")
    y -= 7 * mm
    c.setFont("Helvetica", 10)
    for line in wrap_text(explanation_en, 110):
        c.drawString(x, y, line)
        y -= 5 * mm
        if y < 30 * mm:
            c.showPage()
            y = height - 20 * mm
            c.setFont("Helvetica", 10)

    # Required Documents
    y -= 4 * mm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x, y, "Required Documents")
    y -= 7 * mm
    c.setFont("Helvetica", 10)
    if required_docs:
        for d in required_docs:
            c.drawString(x, y, f"- {d}"[:120])
            y -= 5 * mm
            if y < 30 * mm:
                c.showPage()
                y = height - 20 * mm
                c.setFont("Helvetica", 10)
    else:
        c.drawString(x, y, "- None")
        y -= 5 * mm

    c.showPage()
    c.save()
    return str(file_path)

def wrap_text(text: str, max_chars: int):
    words = str(text).split()
    lines, cur = [], []
    count = 0
    for w in words:
        if count + len(w) + (1 if cur else 0) <= max_chars:
            cur.append(w)
            count += len(w) + (1 if cur else 0)
        else:
            lines.append(" ".join(cur))
            cur, count = [w], len(w)
    if cur:
        lines.append(" ".join(cur))
    return lines
