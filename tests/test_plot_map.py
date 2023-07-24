import os
import sys
from datetime import datetime
sys.path.append('/home/syrmia/Desktop/GPS_tracking_improved')
from func import plot_map


TIMESTAMP_FORMAT = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")


def test_plot_map(tmpdir):
    # Create test data
    segments = [[(42.123, -71.456), (42.345, -71.678), (42.567, -71.890)]]
    z_data_segments = [[0.1, 0.2, 0.3]]
    bump_coords = [(42.234, -71.567), (42.456, -71.789)]
    flag_show = 2
    folder_results = str(tmpdir)

    # Call the function
    plot_map(segments, z_data_segments, bump_coords, flag_show, folder_results)

    # Assert that the map HTML file was created
    map_name = f'map_{TIMESTAMP_FORMAT}.html'
    map_path = os.path.join(folder_results, map_name)
    assert os.path.isfile(map_path)
