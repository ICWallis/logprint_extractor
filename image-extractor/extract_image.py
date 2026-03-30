"""Batch extraction of depth-labelled crop images from a PDF."""

import os
import fitz  # PyMuPDF

from ._render import render_crop


def extract_image(
    pdf_path: str,
    output_dir: str,
    wellname: str,
    top_depth: float,
    base_depth: float,
    pixel_coords_first: dict,
    pixel_coords_default: dict,
    pixel_coords_last: dict,
    exclude_pages: list[int] | None = None,
    render_zoom: float = 2.0,
) -> list[str]:
    """Extract a cropped region from every included page of a PDF and save as PNG.

    The depth range covered by each page is calculated proportionally from the
    pixel heights of all included pages.  The depth values are encoded in the
    output filename.

    Parameters
    ----------
    pdf_path:
        Path to the PDF file.
    output_dir:
        Directory where PNG files will be saved (created if absent).
    wellname:
        Well identifier used as the filename prefix, e.g. ``"FORGE_78B-32"``.
    top_depth:
        Depth value (any unit) at the very top of the first included page crop.
    base_depth:
        Depth value at the very bottom of the last included page crop.
    pixel_coords_first:
        Crop coordinates for the first included page — dict with keys
        ``x_start``, ``x_end``, ``y_start``, ``y_end``, ``zoom``.
    pixel_coords_default:
        Crop coordinates applied to every page that is neither first nor last.
    pixel_coords_last:
        Crop coordinates for the last included page.
    exclude_pages:
        List of 0-indexed page numbers to skip entirely.  Defaults to ``[]``.
    render_zoom:
        Magnification factor used when rasterising the crops.

    Returns
    -------
    list[str]
        Absolute paths of all saved PNG files, in page order.

    Example
    -------
    >>> from logprint_digitiser import extract_image
    >>> saved = extract_image(
    ...     pdf_path="my_log.pdf",
    ...     output_dir="output/",
    ...     wellname="FORGE_78B-32",
    ...     top_depth=2990.0,
    ...     base_depth=8507.0,
    ...     pixel_coords_first={'x_start': 768.0, 'x_end': 987.0,
    ...                         'y_start': 1199.5, 'y_end': 1223.5, 'zoom': 2.0},
    ...     pixel_coords_default={'x_start': 768.0, 'x_end': 987.0,
    ...                           'y_start': 0.0,   'y_end': 854.5,  'zoom': 2.0},
    ...     pixel_coords_last={'x_start': 768.0, 'x_end': 987.0,
    ...                        'y_start': 0.0,   'y_end': 855.0,  'zoom': 2.0},
    ...     exclude_pages=[196],
    ... )
    """
    if exclude_pages is None:
        exclude_pages = []

    os.makedirs(output_dir, exist_ok=True)

    doc = fitz.open(pdf_path)
    total_pages = doc.page_count
    print(f"PDF has {total_pages} pages.")

    # Build ordered list of included pages and identify first/last
    included_pages = [p for p in range(total_pages) if p not in exclude_pages]
    if not included_pages:
        doc.close()
        raise ValueError("No pages remain after applying exclude_pages.")

    first_page = included_pages[0]
    last_page  = included_pages[-1]
    print(f"First included page: {first_page}  |  Last included page: {last_page}")

    def _get_coords(page_num: int) -> dict:
        if page_num == first_page:
            return pixel_coords_first
        elif page_num == last_page:
            return pixel_coords_last
        return pixel_coords_default

    # Pass 1 — total pixel height for depth scaling
    total_pdf_height = sum(
        _get_coords(p)["y_end"] - _get_coords(p)["y_start"]
        for p in included_pages
    )

    depth_span     = base_depth - top_depth
    depth_per_unit = depth_span / total_pdf_height
    print(f"Included pages  : {len(included_pages)}")
    print(f"Total PDF height: {total_pdf_height:.2f} PDF units")
    print(f"Depth scale     : {depth_per_unit:.4f} depth-units / PDF unit\n")

    # Pass 2 — extract, save
    saved_paths: list[str] = []
    cumulative_height = 0.0

    for page_num in included_pages:
        coords      = _get_coords(page_num)
        page_height = coords["y_end"] - coords["y_start"]

        page_top_depth  = top_depth + cumulative_height * depth_per_unit
        page_base_depth = top_depth + (cumulative_height + page_height) * depth_per_unit

        img      = render_crop(doc[page_num], coords, render_zoom)
        filename = f"{wellname} {page_top_depth:.2f} - {page_base_depth:.2f}.png"
        out_path = os.path.join(output_dir, filename)
        img.save(out_path)
        saved_paths.append(os.path.abspath(out_path))

        print(
            f"  Page {page_num:>3d}  "
            f"{page_top_depth:9.2f} - {page_base_depth:9.2f}  ->  {filename}"
        )

        cumulative_height += page_height

    doc.close()
    print(f"\nDone. {len(saved_paths)} images saved to:\n  {output_dir}")
    return saved_paths
