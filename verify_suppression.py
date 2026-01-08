import logging
import sys
from pdfminer.high_level import extract_text

# Suppress pdfminer logging
logging.getLogger("pdfminer").setLevel(logging.ERROR)

print("Starting extraction with suppression...")
try:
    text = extract_text("./data/ROBOTICS AND AUTOMATION.pdf")
    print(f"Extraction complete. Length: {len(text)}")
except Exception as e:
    print(f"Error: {e}")
