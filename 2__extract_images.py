import fitz  # PyMuPDF
from PIL import Image
import os

# ---------------------------------------------------------------------------
# INPUTS
# ---------------------------------------------------------------------------

#pdf_file = r"c:\Users\irene\Dropbox (Personal)\Cubic-Earth\Marketing\ALT_colab\DigitisingLogPrints\Repo\University_Utah_FORGE_78B-32_FMI_Interpretation_20.pdf"
pdf_file = r"C:\Users\irene\Dropbox (Personal)\Cubic-Earth\Marketing\ALT_colab\DigitisingLogPrints\ExampleData\Ramsay_FMI_report_open_file__log_print.pdf"

output_dir = r"c:\Users\irene\Dropbox (Personal)\Cubic-Earth\Marketing\ALT_colab\DigitisingLogPrints\Repo\extracted_images"

# wellname = "FORGE_78B-32"

# top_depth  = 2990.0   # depth at the very top of page 0 crop
# base_depth = 8507.0   # depth at the very bottom of the last page crop

# Pixel coordinates from 2__define_pxl_ranges.py (PDF space, before zoom)
# pixel_coords_first_page             = {'x_start': 768.0, 'x_end': 987.0, 'y_start': 1199.5, 'y_end': 1223.5, 'zoom': 2.0}
# pixel_coords_all_other_pages    = {'x_start': 768.5, 'x_end': 987.0, 'y_start': 0.0, 'y_end': 1223.5, 'zoom': 2.0}
# pixel_coords_last_page           = {'x_start': 768.0, 'x_end': 987.5, 'y_start': 0.0, 'y_end': 855.0, 'zoom': 2.0}

# exclude_pages = [196]   # 0-indexed page numbers to skip entirely

wellname = "RAMSAY-1"

top_depth  = 223.4  # depth at the very top of page 0 crop
base_depth = 999.5  # depth at the very bottom of the last page crop

pixel_coords_first_page = {'x_start': 423.0, 'x_end': 541.0, 'y_start': 178.0, 'y_end': 594.5, 'zoom': 2.0}
pixel_coords_all_other_pages = {'x_start': 423.0, 'x_end': 541.0, 'y_start': 0.0, 'y_end': 594.5, 'zoom': 2.0}
pixel_coords_last_page = {'x_start': 423.0, 'x_end': 541.0, 'y_start': 0.0, 'y_end': 594.5, 'zoom': 2.0}

exclude_pages = [259]   # 0-indexed page numbers to skip entirely

# Zoom used when rendering the final PNG (independent of the selection zoom)
RENDER_ZOOM = 2.0

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def get_coords(page_num, first_page, last_page):
    """Return the pixel_coords dict for a given 0-indexed page number."""
    if page_num == first_page:
        return pixel_coords_first_page
    elif page_num == last_page:
        return pixel_coords_last_page
    else:
        return pixel_coords_all_other_pages


def render_crop(page, coords, render_zoom):
    """Render a cropped region of a PDF page and return a PIL Image."""
    rect = fitz.Rect(coords['x_start'], coords['y_start'],
                     coords['x_end'],   coords['y_end'])
    mat  = fitz.Matrix(render_zoom, render_zoom)
    pix  = page.get_pixmap(matrix=mat, clip=rect)
    return Image.frombytes("RGB", [pix.width, pix.height], pix.samples)



# ---------------------------------------------------------------------------
# MAIN EXTRACTION LOOP
# ---------------------------------------------------------------------------

os.makedirs(output_dir, exist_ok=True)

doc = fitz.open(pdf_file)
total_pages = doc.page_count
print(f"PDF has {total_pages} pages.")

# Determine the first and last included page numbers (excluding skipped pages)
included_pages = [p for p in range(total_pages) if p not in exclude_pages]
first_page = included_pages[0]
last_page  = included_pages[-1]
print(f"First included page: {first_page}  |  Last included page: {last_page}")

# --- Pass 1: sum pixel heights across all included pages -------------------
total_pdf_height = 0.0

for page_num in included_pages:
    coords = get_coords(page_num, first_page, last_page)
    total_pdf_height += coords['y_end'] - coords['y_start']

depth_span     = base_depth - top_depth
depth_per_unit = depth_span / total_pdf_height
print(f"Included pages  : {len(included_pages)}")
print(f"Total PDF height: {total_pdf_height:.2f} PDF units")
print(f"Depth scale     : {depth_per_unit:.4f} m / PDF unit\n")

# --- Pass 2: extract, label, and save each page ----------------------------
cumulative_height = 0.0

for page_num in included_pages:
    coords      = get_coords(page_num, first_page, last_page)
    page_height = coords['y_end'] - coords['y_start']

    page_top_depth  = top_depth + cumulative_height * depth_per_unit
    page_base_depth = top_depth + (cumulative_height + page_height) * depth_per_unit

    img = render_crop(doc[page_num], coords, RENDER_ZOOM)

    # e.g. "FORGE_78B-32 3047.17 - 3075.50.png"
    filename = f"{wellname} {page_top_depth:.2f} - {page_base_depth:.2f}.png"
    img.save(os.path.join(output_dir, filename))

    print(f"  Page {page_num:>3d}  {page_top_depth:9.2f} - {page_base_depth:9.2f} m  ->  {filename}")

    cumulative_height += page_height

doc.close()
print(f"\nDone. {len(included_pages)} images saved to:\n  {output_dir}")
