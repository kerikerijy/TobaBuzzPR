import sys
import pypdf
from pypdf import PdfReader

if len(sys.argv) < 3:
    print("Usage: python extract_pdf_argv.py <input.pdf> <output.txt>")
    sys.exit(1)

pdf_file = sys.argv[1]
out_file = sys.argv[2]

reader = PdfReader(pdf_file)
text = ""
for page in reader.pages:
    text += page.extract_text() + "\n\n"
    
with open(out_file, "w", encoding="utf-8") as f:
    f.write(text)
print(f"Extraction successful. Saved to {out_file}")
