import sys
from datetime import timedelta
sys.path.append('/home/syrmia/Desktop/GPS_tracking_improved')
from func import road_duration


def test_road_duration():
    # Create test data
    data = {
        'time': ['10:00:00', '10:30:00', '11:00:00']
    }

    # Call the function
    duration = road_duration(data)

    # Assert the duration
    expected_duration = timedelta(hours=1)
    assert duration == expected_duration
