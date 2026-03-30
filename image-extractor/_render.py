"""Shared low-level rendering helper."""

import fitz  # PyMuPDF
from PIL import Image


def render_crop(page, coords: dict, render_zoom: float) -> Image.Image:
    """Render a clipped region of an open PDF page and return a PIL Image.

    Parameters
    ----------
    page:
        An open ``fitz.Page`` object.
    coords:
        Dict with keys ``x_start``, ``x_end``, ``y_start``, ``y_end``
        in PDF (unzoomed) coordinate space.
    render_zoom:
        Magnification factor applied when rasterising.
    """
    rect = fitz.Rect(
        coords["x_start"], coords["y_start"],
        coords["x_end"],   coords["y_end"],
    )
    mat = fitz.Matrix(render_zoom, render_zoom)
    pix = page.get_pixmap(matrix=mat, clip=rect)
    return Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
