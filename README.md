# Image Extractor

Workflow developed to extract PNGs from PDF borehole image log prints.

Each page of the borehole image print is extracted as a single PNG with 
a top and bottom depth in the file name. This is the format required for
import into WellCAD software as a RGB image. 

Workflow:
(1) Use the pxl_range tool to determine the pixel range that will be extracted for the first page, last page, and the pages between. Note these. 
(2) Verify you have specified the correct pixel range using inspect_image. 
(2) Use extract_image to generate the png images based on provided ranges.

Example method uses the open access FORGE 78B-32 log print that can be found here ____. CITATION.
