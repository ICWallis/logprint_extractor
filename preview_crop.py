import fitz  # PyMuPDF
from PIL import Image
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# INPUTS — edit these as needed
# ---------------------------------------------------------------------------

pdf_file = r"c:\Users\irene\Dropbox (Personal)\Cubic-Earth\Marketing\ALT_colab\DigitisingLogPrints\Repo\University_Utah_FORGE_78B-32_FMI_Interpretation_20.pdf"

page_number = 195

pixel_coords = {'x_start': 768.0, 'x_end': 987.5, 'y_start': 0.0, 'y_end': 855.0, 'zoom': 2.0}

# ---------------------------------------------------------------------------

doc  = fitz.open(pdf_file)
page = doc[page_number]

rect = fitz.Rect(pixel_coords['x_start'], pixel_coords['y_start'],
                 pixel_coords['x_end'],   pixel_coords['y_end'])
mat  = fitz.Matrix(pixel_coords['zoom'], pixel_coords['zoom'])
pix  = page.get_pixmap(matrix=mat, clip=rect)
img  = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
doc.close()

print(f"Extracted image size: {pix.width} x {pix.height} px")

plt.figure(figsize=(8, 10))
plt.imshow(img)
plt.title(f"Page {page_number}  |  x: {pixel_coords['x_start']} – {pixel_coords['x_end']}  "
          f"y: {pixel_coords['y_start']} – {pixel_coords['y_end']}")
plt.axis('off')
plt.tight_layout()
plt.show()
