import folium
import sys
sys.path.append('/home/syrmia/Desktop/GPS_tracking_improved')
from func import plot_segment


def test_plot_segment():
    # Create test data
    segment = [(42.123, -71.456), (42.345, -71.678), (42.567, -71.890)]
    z_data_segment = [0.1, 0.2, 0.3]
    bump_coords = [(42.234, -71.567), (42.456, -71.789)]
    my_map = folium.Map()

    # Call the function
    plot_segment(segment, z_data_segment, bump_coords, my_map)

    # Assert that the PolyLine was added to the map
    assert len(my_map._children) == 2
    