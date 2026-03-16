"""Extract text from EPA OBR PDF for definition alignment."""
import os

try:
    import fitz  # PyMuPDF
except ImportError:
    print("PyMuPDF not installed, trying pdfplumber...")
    fitz = None

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

BASE = os.path.dirname(__file__)
pdf_path = os.path.join(BASE, "Phase II CSVs", "Week 10- HR Operations OBR.pdf")

if fitz:
    doc = fitz.open(pdf_path)
    for i, page in enumerate(doc):
        print(f"\n=== PAGE {i+1} ===")
        print(page.get_text())
elif pdfplumber:
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            print(f"\n=== PAGE {i+1} ===")
            text = page.extract_text()
            if text:
                print(text)
            # Also try tables
            tables = page.extract_tables()
            for j, table in enumerate(tables):
                print(f"\n--- Table {j+1} ---")
                for row in table:
                    print("\t".join(str(c) for c in row))
else:
    print("No PDF library available. Install with: pip install pdfplumber")
