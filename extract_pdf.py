import subprocess
import os

pdf_file = "鳥羽高校 広報戦略策定レポート (最新版).pdf"
out_file = "latest_report_extracted.md"

try:
    import pypdf
    from pypdf import PdfReader
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n\n"
        
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Extraction successful using pypdf. Saved to {out_file}")
except ImportError:
    print("pypdf not found. Trying another method...")
    # fallback to pdfplumber or fitz or pdftotext
    try:
        import fitz
        doc = fitz.open(pdf_file)
        text = ""
        for page in doc:
            text += page.get_text() + "\n\n"
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Extraction successful using PyMuPDF. Saved to {out_file}")
    except ImportError:
        print("PyMuPDF not found either. Trying pdftotext command...")
        result = subprocess.run(["pdftotext", pdf_file, out_file], capture_output=True)
        if result.returncode == 0:
            print(f"Extraction successful using pdftotext. Saved to {out_file}")
        else:
            print("Failed to extract text. Please install pypdf: pip install pypdf")
