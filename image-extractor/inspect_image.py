"""Display a cropped page region given pixel coordinates."""

import fitz  # PyMuPDF
import matplotlib.pyplot as plt

from ._render import render_crop


def inspect_image(pdf_path: str, page_num: int, pixel_coords: dict) -> None:
    """Display a cropped region of a PDF page in a matplotlib window.

    Useful for verifying that pixel coordinates produced by :func:`pxl_range`
    capture the correct area before running a full extraction.

    Parameters
    ----------
    pdf_path:
        Path to the PDF file.
    page_num:
        0-indexed page number to inspect.
    pixel_coords:
        Dict with keys ``x_start``, ``x_end``, ``y_start``, ``y_end``, and
        ``zoom`` in PDF (unzoomed) coordinate space — the format returned by
        :func:`pxl_range`.

    Example
    -------
    >>> from logprint_digitiser import inspect_image
    >>> coords = {'x_start': 768.0, 'x_end': 987.0,
    ...           'y_start': 0.0,   'y_end': 854.5, 'zoom': 2.0}
    >>> inspect_image("my_log.pdf", page_num=11, pixel_coords=coords)
    """
    doc  = fitz.open(pdf_path)
    img  = render_crop(doc[page_num], pixel_coords, pixel_coords["zoom"])
    doc.close()

    print(f"Extracted image size: {img.width} x {img.height} px")

    plt.figure(figsize=(8, 10))
    plt.imshow(img)
    plt.title(
        f"Page {page_num}  |  "
        f"x: {pixel_coords['x_start']} – {pixel_coords['x_end']}  "
        f"y: {pixel_coords['y_start']} – {pixel_coords['y_end']}"
    )
    plt.axis("off")
    plt.tight_layout()
    plt.show()
