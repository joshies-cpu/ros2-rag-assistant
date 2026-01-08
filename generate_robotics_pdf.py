from fpdf import FPDF
import os

try:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', size=12)
    pdf.cell(200, 10, txt='Title: Advances in Robotics', ln=1, align='C')
    pdf.cell(200, 10, txt='Abstract: This paper discusses the latest in robotics.', ln=1, align='L')
    pdf.cell(200, 10, txt='1. Introduction: Robots are likely to take over common ETL tasks.', ln=1, align='L')
    parsed_file = 'data/robotics_paper.pdf'
    pdf.output(parsed_file)
    print(f"Created {parsed_file}")
except Exception as e:
    print(f"Failed to create PDF: {e}")
