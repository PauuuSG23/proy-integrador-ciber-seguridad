from pathlib import Path
from fpdf import FPDF
import re
import unicodedata

BASE_DIR = Path(__file__).resolve().parent
REPORT_DIR = BASE_DIR / "reports"
INPUT_HTML = REPORT_DIR / "combined_report_20260523_1430.html"
OUTPUT_PDF = REPORT_DIR / "combined_report_20260523_1430.pdf"

if not INPUT_HTML.exists():
    raise FileNotFoundError(f"Input HTML report not found: {INPUT_HTML}")

html = INPUT_HTML.read_text(encoding="utf-8")
# Replace tags with newlines/spaces
text = re.sub(r"<(/?br|/?p|/?div|/?h[1-6]|/?li|/?ul|/?ol|/?table|/?thead|/?tbody|/?tr|/?th|/?td)[^>]*>", "\n", html, flags=re.IGNORECASE)
text = re.sub(r"<[^>]+>", "", text)
text = re.sub(r"\n{2,}", "\n\n", text)
text = text.strip()
text = unicodedata.normalize('NFKD', text)
text = text.encode('ascii', 'ignore').decode('ascii')

pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()
pdf.set_font("Arial", size=11)
line_height = pdf.font_size * 2.5
max_width = 190

for paragraph in text.split("\n\n"):
    pdf.multi_cell(max_width, line_height, paragraph, align="L")
    pdf.ln(1)

pdf.output(OUTPUT_PDF)
print(f"PDF saved: {OUTPUT_PDF}")
