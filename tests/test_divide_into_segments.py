import sys
sys.path.append('/home/syrmia/Desktop/GPS_tracking_improved')
from func import divide_into_segments


def test_divide_into_segments():
    coordinates = [
       (37.7763, -122.4021), (37.7771, -122.4022),
       (37.7774, -122.4022), (37.7776, -122.4026)]

    accel_data = [0.1, 0.2, 0.3, 0.4]
    # Define the expected output
    expected_segments = [[(37.7763, -122.4021), (37.7771, -122.4022),
                         (37.7774, -122.4022)], [(37.7774, -122.4022),
                         (37.7776, -122.4026)]]
    expected_accel_data_segments = [[0.1, 0.2, 0.3],
                                    [0.3, 0.4]]
    # Call the divide_into_segments function
    segments, accel_data_segments = divide_into_segments(coordinates,
                                                         accel_data)

    # Assert the expected output
    assert segments == expected_segments
    assert accel_data_segments == expected_accel_data_segments
