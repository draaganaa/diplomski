import sys
sys.path.append('/home/syrmia/Desktop/GPS_tracking_improved')
from func import road_distance


def test_road_distance():
    # Create test data
    coords = [
        (42.123, -71.456),
        (42.345, -71.678),
        (42.567, -71.890)
    ]

    # Call the function
    distance = road_distance(coords)

    # Assert the distance
    expected_distance = '60.91'
    assert distance == expected_distance
