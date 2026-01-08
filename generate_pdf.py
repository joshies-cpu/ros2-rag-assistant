from fpdf import FPDF
import os

try:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', size=12)
    pdf.cell(200, 10, txt='Hello World! This is a test PDF. Visit https://example.com for more.', ln=1, align='C')
    parsed_file = 'data/sample.pdf'
    pdf.output(parsed_file)
    print(f"Created {parsed_file}")
except Exception as e:
    print(f"Failed to create PDF: {e}")
