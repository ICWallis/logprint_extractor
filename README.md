# Image Extractor

Workflow developed to extract PNGs from PDF borehole image log prints.

Each page of the borehole image print is extracted as a single PNG with 
a top and bottom depth in the file name. This is the format required for
import into WellCAD software as a RGB image. 

Workflow:
(1) determine pixel range that will be extracted for the first page, last page,
and the pages between. 
(2) extract the images based on those ranges.
