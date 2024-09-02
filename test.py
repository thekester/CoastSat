import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from coastsat import SDS_download, SDS_preprocess, SDS_shoreline, SDS_tools, SDS_transects
import pickle
import tempfile
import shutil

# Test 1: Verify that NumPy is working correctly
def test_numpy():
    array = np.array([1, 2, 3])
    assert np.sum(array) == 6, "NumPy sum test failed!"
    print("Test NumPy: OK")

# Test 2: Verify that Pandas is working correctly
def test_pandas():
    df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
    assert df.shape == (3, 2), "Pandas DataFrame test failed!"
    print("Test Pandas: OK")

# Test 3: Verify that basic CoastSat functions are working
def test_coastsat():
    polygon = [[[151.301454, -33.700754],
                [151.311453, -33.702075],
                [151.307237, -33.739761],
                [151.294220, -33.736329],
                [151.301454, -33.700754]]]
    
    # Test the smallest_rectangle function
    rectangle = SDS_tools.smallest_rectangle(polygon)
    
    # Check that the output is a list of exactly 4 vertices
    assert len(rectangle[0]) == 5, "CoastSat smallest_rectangle test failed! The rectangle should have 5 points (4 vertices plus the closing point)."
    assert rectangle[0][0] == rectangle[0][-1], "The first and last point should be the same to close the polygon."
    
    print("Test CoastSat smallest_rectangle: OK")

# Test 4: Run the full example pipeline without GUI
def test_full_pipeline():
    # Use a temporary directory for file outputs
    temp_dir = tempfile.mkdtemp()

    try:
        # Define the region of interest (polygon)
        polygon = [[[151.301454, -33.700754],
                    [151.311453, -33.702075],
                    [151.307237, -33.739761],
                    [151.294220, -33.736329],
                    [151.301454, -33.700754]]]
        polygon = SDS_tools.smallest_rectangle(polygon)

        # Date range
        dates = ['1984-01-01', '2022-01-01']

        # Satellite missions
        sat_list = ['L5', 'L7', 'L8']
        sitename = 'NARRA'

        # Inputs dictionary
        inputs = {
            'polygon': polygon,
            'dates': dates,
            'sat_list': sat_list,
            'sitename': sitename,
            'filepath': temp_dir,  # Use temp directory
        }

        # Check available images
        available_images = SDS_download.check_images_available(inputs)
        assert available_images is not None, "Image availability check failed!"
        print(f"Available images: {available_images}")

        # Retrieve satellite images from GEE (this may take time)
        metadata = SDS_download.retrieve_images(inputs)
        assert metadata is not None, "Image retrieval failed!"
        print("Image retrieval: OK")

        # Shoreline extraction settings
        settings = {
            'cloud_thresh': 0.1,
            'dist_clouds': 300,
            'output_epsg': 28356,
            'check_detection': False,
            'adjust_detection': False,
            'save_figure': False,  # Disable figure saving
            'min_beach_area': 1000,
            'min_length_sl': 500,
            'cloud_mask_issue': False,
            'sand_color': 'default',
            'pan_off': False,
            's2cloudless_prob': 40,
            'inputs': inputs,
        }

        # Extract shorelines
        output = SDS_shoreline.extract_shorelines(metadata, settings)
        assert output is not None, "Shoreline extraction failed!"
        print("Shoreline extraction: OK")

        # Remove duplicates and inaccuracies
        output = SDS_tools.remove_duplicates(output)
        output = SDS_tools.remove_inaccurate_georef(output, 10)
        assert output is not None, "Removing duplicates or inaccurate georeferencing failed!"
        print("Duplicates and inaccuracies removal: OK")

        # Save output to GeoJSON (no GUI)
        geomtype = 'points'
        gdf = SDS_tools.output_to_gdf(output, geomtype)
        assert gdf is not None, "GeoDataFrame creation failed!"
        gdf.crs = {'init': 'epsg:' + str(settings['output_epsg'])}
        gdf.to_file(os.path.join(inputs['filepath'], inputs['sitename'], '%s_output_%s.geojson' % (sitename, geomtype)),
                    driver='GeoJSON', encoding='utf-8')
        print("GeoJSON saving: OK")

        # Load shoreline data (simulate post-processing)
        filepath = os.path.join(inputs['filepath'], sitename)
        with open(os.path.join(filepath, sitename + '_output' + '.pkl'), 'rb') as f:
            output = pickle.load(f)
        assert output is not None, "Loading shoreline data failed!"
        print("Shoreline data loaded: OK")

        print("Full pipeline test: OK")
    finally:
        # Clean up the temporary directory
        shutil.rmtree(temp_dir)
        print(f"Temporary directory {temp_dir} cleaned up.")

if __name__ == "__main__":
    test_numpy()
    test_pandas()
    test_coastsat()
    test_full_pipeline()

    print("All tests were successfully executed.")
