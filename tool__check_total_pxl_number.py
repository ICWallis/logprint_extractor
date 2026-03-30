# %%

import fitz  # PyMuPDF
from PIL import Image
import io
import os

# %%

def inspect_page(pdf_path, page_num):
    """Helper to inspect page dimensions and manually determine crop coordinates"""
    doc = fitz.open(pdf_path)
    page = doc[page_num]
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    print(f"Page {page_num} dimensions: {pix.width} x {pix.height}")
    img.show()  # Opens image for manual inspection
    doc.close()


pdf_file = r"c:\Users\irene\Dropbox (Personal)\Cubic-Earth\Marketing\ALT_colab\DigitisingLogPrints\Repo\University_Utah_FORGE_78B-32_FMI_Interpretation_20.pdf"
page_number = 0  # Example page number to inspect

inspect_page(pdf_file, page_number)


# %%