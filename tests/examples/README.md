# Snow mask example

[`snow-mask-alaska-west-nome.png`](snow-mask-alaska-west-nome.png) shows a real Sentinel-2 scene from the natural Arctic coast west of Nome, Alaska, acquired on 1 June 2024. Red highlights Sentinel-2 Scene Classification Layer class 11, snow and ice. The class covers 26.6% of the displayed raster.

**Location:** the scene covers approximately 64.49 to 64.53 degrees north and 165.60 to 165.50 degrees west, on the Seward Peninsula shoreline of Norton Sound. It is about 5 to 10 km west of Nome, Alaska. In the Sentinel-2 image, north is at the top and the coastline runs diagonally across the frame.

The scene is an illustration for the snow mask covered by [`snow-mask-test.py`](../snow-mask-test.py). It is not a test fixture, and the shoreline extraction is not validated by this image. Sea ice lies between the land and open water.

Source imagery: Sentinel-2 Level-2A, accessed through Google Earth Engine from `COPERNICUS/S2_SR_HARMONIZED`.
