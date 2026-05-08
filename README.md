# image_extractor

A Python package for extracting depth-labelled PNG strips from PDF borehole image log prints.

Each page of the PDF is cropped to the log track and saved as a PNG whose filename encodes the top and bottom depth of that strip — the format required for import into **WellCAD** as an RGB image.

Contact irene@cubicearth.nz for more information on extracting and using historic borehole image data.

---

## Installation

```bash
pip install logprint_extractor
```

Requires Python ≥ 3.11.  Dependencies (`pymupdf`, `Pillow`, `matplotlib`) are installed automatically.

---

## Workflow

The extraction is a three-step process, each covered by a script in the `tutorial/` folder.

### Step 1 — Find pixel coordinates (`tutorial/step1_find_pixel_range.py`)

Use `pxl_range()` to interactively select the crop region on a rendered PDF page.
Run this once for each distinct page layout (typically: first page, a representative middle page, and the last page).

1. A matplotlib window opens showing the rendered page.
2. Use the built-in zoom/pan tools to navigate to the area of interest.
3. Toggle **Selection Mode** on, then click the top-left corner of the log strip.
4. Press **Accept Point** to lock it in.
5. Navigate to the bottom-right corner, click, then press **Accept Point** again.
6. Close the window — the coordinate dict is printed to the terminal.
7. Copy the coordinates into steps 2 and 3.

### Step 2 — Verify the crop (`tutorial/step2_inspect_image.py`)

Use `inspect_image()` to display the cropped region for the first, a middle, and the last page.
Confirm the crop looks correct before running the full extraction.

### Step 3 — Extract images (`tutorial/step3_extract_image.py`)

Use `extract_image()` to batch-process all included pages.
Each page is saved as a PNG named with its depth range, for example:

```
FORGE_78B-32 224.70 - 228.65.png
```

---

## API reference

| Function | Description |
|---|---|
| `pxl_range(pdf_path, page_num)` | Interactively define a crop rectangle and return pixel coordinates. |
| `inspect_image(pdf_path, page_num, pixel_coords)` | Display a single cropped page region for verification. |
| `extract_image(pdf_path, output_dir, wellname, top_depth, base_depth, ...)` | Batch-extract depth-labelled PNG strips from all included pages. |

---

## Tutorial data

The tutorial scripts use an open-access FMI log print from the Utah FORGE project:

> McLennan, J. (2021). *Utah FORGE: Well 78B-32 Daily Drilling Reports and Logs.*
> \[Data set\]. Geothermal Data Repository. Energy and Geoscience Institute at the University of Utah.
> <https://doi.org/10.15121/1814488>

The PDF (`University_Utah_FORGE_78B-32_FMI_Interpretation_20.pdf`) can be downloaded from
<https://gdr.openei.org/submissions/1330>.




