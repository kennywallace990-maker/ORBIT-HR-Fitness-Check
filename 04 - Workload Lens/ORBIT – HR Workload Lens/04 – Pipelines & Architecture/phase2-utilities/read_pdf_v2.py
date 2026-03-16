"""Extract text from EPA OBR PDF — page by page to file."""
import os
import pdfplumber

BASE = os.path.dirname(__file__)
pdf_path = os.path.join(BASE, "Phase II CSVs", "Week 10- HR Operations OBR.pdf")
out_path = os.path.join(BASE, "epa_obr_wk10_text.txt")

with pdfplumber.open(pdf_path) as pdf:
    with open(out_path, 'w', encoding='utf-8') as out:
        out.write(f"Total pages: {len(pdf.pages)}\n\n")
        for i, page in enumerate(pdf.pages):
            out.write(f"=== PAGE {i+1} ===\n")
            text = page.extract_text()
            if text:
                out.write(text + "\n")
            out.write("\n")

print(f"Extracted {len(pdf.pages)} pages to {out_path}")
