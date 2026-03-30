"""logprint-digitiser — extract depth-labelled images from PDF well log prints.

Public API
----------
pxl_range(pdf_path, page_num, zoom=2.0)
    Interactively select a crop region and return pixel coordinates.

inspect_image(pdf_path, page_num, pixel_coords)
    Display a single cropped page region for verification.

extract_image(pdf_path, output_dir, wellname, top_depth, base_depth,
              pixel_coords_first, pixel_coords_default, pixel_coords_last,
              exclude_pages=None, render_zoom=2.0)
    Batch-extract depth-labelled PNG images from all included pages.
"""

from .pxl_range import pxl_range
from .inspect_image import inspect_image
from .extract_image import extract_image

__all__ = ["pxl_range", "inspect_image", "extract_image"]
__version__ = "0.1.0"
