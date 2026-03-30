"""Interactive pixel-range selector for a single PDF page."""

import fitz  # PyMuPDF
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.widgets import Button


def pxl_range(pdf_path: str, page_num: int, zoom: float = 2.0) -> dict | None:
    """Interactively select a crop region on one page of a PDF.

    Opens a matplotlib window showing the rendered page.  Use the two buttons
    at the bottom to:

    * **Selection ON / OFF** — toggle click-capture on and off so you can
      freely use the normal zoom / pan toolbar between placements.
    * **Accept Point** — confirm the currently pending point (shown in yellow)
      and advance to the next corner.

    Click as many times as you like to reposition a corner before accepting.
    Once both corners are accepted the window title updates and you can close
    the window.

    Parameters
    ----------
    pdf_path:
        Path to the PDF file.
    page_num:
        0-indexed page number to display.
    zoom:
        Magnification used when rendering the page for display.  The returned
        coordinates are always in unzoomed PDF space.

    Returns
    -------
    dict or None
        ``{'x_start', 'x_end', 'y_start', 'y_end', 'zoom'}`` in PDF (unzoomed)
        coordinate space, or ``None`` if the window was closed before both
        corners were accepted.
    """
    doc = fitz.open(pdf_path)
    page = doc[page_num]
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    doc.close()

    print(f"Page {page_num} dimensions: {pix.width} x {pix.height}")
    print("1. Toggle 'Selection Mode' to enable/disable clicking")
    print("2. Click to place a point (yellow) — click again to adjust it")
    print("3. Press 'Accept Point' to confirm and move to the next corner")

    fig, ax = plt.subplots(figsize=(12, 16))
    plt.subplots_adjust(bottom=0.15)
    ax.imshow(img)
    ax.set_title(f"Page {page_num} - Toggle 'Selection Mode' then click top-left corner")

    coords = []
    pending = [None]
    pending_marker = [None]
    confirmed_markers = []
    rect_patch = [None]
    selection_enabled = [False]
    cid = [None]
    phase = [0]  # 0 = top-left, 1 = bottom-right, 2 = done

    def onclick(event):
        if not selection_enabled[0] or phase[0] >= 2:
            return
        if event.inaxes != ax:
            return

        x, y = int(event.xdata), int(event.ydata)
        pending[0] = (x, y)

        if pending_marker[0] is not None:
            pending_marker[0].remove()
        pending_marker[0], = ax.plot(x, y, "yo", markersize=10)

        if phase[0] == 1 and coords:
            x1, y1 = coords[0]
            if rect_patch[0] is not None:
                rect_patch[0].remove()
            rect_patch[0] = patches.Rectangle(
                (x1, y1), x - x1, y - y1,
                linewidth=2, edgecolor="yellow", facecolor="none", linestyle="--",
            )
            ax.add_patch(rect_patch[0])

        corner = "top-left" if phase[0] == 0 else "bottom-right"
        ax.set_title(f"Pending {corner}: ({x}, {y})  —  click to adjust, then Accept")
        btn_accept.label.set_text(f"Accept {corner.title()} ({x}, {y})")
        btn_accept.color = "lightgreen"
        fig.canvas.draw()

    def accept_point(event):
        if pending[0] is None or phase[0] >= 2:
            return

        x, y = pending[0]

        if pending_marker[0] is not None:
            pending_marker[0].remove()
            pending_marker[0] = None
        marker, = ax.plot(x, y, "ro", markersize=10)
        confirmed_markers.append(marker)

        coords.append((x, y))
        phase[0] += 1
        pending[0] = None

        if phase[0] == 1:
            pdf_x, pdf_y = x / zoom, y / zoom
            print(f"Top-left confirmed: pixel ({x}, {y})  ->  PDF ({pdf_x:.1f}, {pdf_y:.1f})")
            ax.set_title("Top-left confirmed! Now select bottom-right corner")
            btn_accept.label.set_text("Accept (click to set point first)")
            btn_accept.color = "lightyellow"

        elif phase[0] == 2:
            x1, y1 = coords[0]
            x2, y2 = coords[1]

            if rect_patch[0] is not None:
                rect_patch[0].remove()
            rect_patch[0] = patches.Rectangle(
                (x1, y1), x2 - x1, y2 - y1,
                linewidth=2, edgecolor="red", facecolor="none",
            )
            ax.add_patch(rect_patch[0])

            pdf_x1, pdf_y1 = x1 / zoom, y1 / zoom
            pdf_x2, pdf_y2 = x2 / zoom, y2 / zoom
            print(f"Bottom-right confirmed: pixel ({x2}, {y2})  ->  PDF ({pdf_x2:.1f}, {pdf_y2:.1f})")
            print(f"\nCrop coordinates (PDF space):")
            print(f"  x_start = {min(pdf_x1, pdf_x2):.2f}")
            print(f"  x_end   = {max(pdf_x1, pdf_x2):.2f}")
            print(f"  y_start = {min(pdf_y1, pdf_y2):.2f}")
            print(f"  y_end   = {max(pdf_y1, pdf_y2):.2f}")
            print(f"  zoom    = {zoom}")

            ax.set_title("Selection complete! Close window to continue.")
            btn_accept.label.set_text("Selection Complete")
            btn_accept.color = "lightblue"
            btn_toggle.label.set_text("Selection OFF")
            btn_toggle.color = "lightcoral"

            selection_enabled[0] = False
            if cid[0] is not None:
                fig.canvas.mpl_disconnect(cid[0])
                cid[0] = None

        fig.canvas.draw()

    def toggle_selection(event):
        if phase[0] >= 2:
            return

        selection_enabled[0] = not selection_enabled[0]

        if selection_enabled[0]:
            if cid[0] is None:
                cid[0] = fig.canvas.mpl_connect("button_press_event", onclick)
            btn_toggle.label.set_text("Selection ON")
            btn_toggle.color = "lightgreen"
            corner = "top-left" if phase[0] == 0 else "bottom-right"
            ax.set_title(f"Click to set {corner} corner (click again to adjust)")
            print(f"Selection mode ENABLED — phase {phase[0] + 1}/2")
        else:
            if cid[0] is not None:
                fig.canvas.mpl_disconnect(cid[0])
                cid[0] = None
            btn_toggle.label.set_text("Selection OFF")
            btn_toggle.color = "lightcoral"
            ax.set_title("Use zoom/pan tools (toggle on to continue selecting)")
            print("Selection mode DISABLED — use zoom/pan")

        fig.canvas.draw()

    ax_btn_toggle = plt.axes([0.15, 0.05, 0.28, 0.05])
    btn_toggle = Button(ax_btn_toggle, "Selection OFF")
    btn_toggle.color = "lightcoral"
    btn_toggle.on_clicked(toggle_selection)

    ax_btn_accept = plt.axes([0.55, 0.05, 0.30, 0.05])
    btn_accept = Button(ax_btn_accept, "Accept Point")
    btn_accept.color = "lightyellow"
    btn_accept.on_clicked(accept_point)

    plt.show()

    if len(coords) == 2:
        x1, y1 = coords[0]
        x2, y2 = coords[1]
        return {
            "x_start": min(x1, x2) / zoom,
            "x_end":   max(x1, x2) / zoom,
            "y_start": min(y1, y2) / zoom,
            "y_end":   max(y1, y2) / zoom,
            "zoom":    zoom,
        }
    return None
