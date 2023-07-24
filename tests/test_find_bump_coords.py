import sys
import pandas as pd
sys.path.append('/home/syrmia/Desktop/GPS_tracking_improved')
from func import find_bump_coords


def test_find_bump_coords():
    # create a test DataFrame with known bumps
    data = pd.DataFrame({
        'latitude': [42.3601, 42.3602, 42.3603, 42.3604, 42.3605,
                     42.3606, 42.3607, 42.3608, 42.3609, 42.3610],
        'longitude': [-71.0589, -71.0588, -71.0587, -71.0586, -71.0585,
                      -71.0584, -71.0583, -71.0582, -71.0581, -71.0580],
        'time': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        'x': [5.1, 5.22, 5.23, 5.3, 5.54, 5.9, 6.1, 6.3, 7.3, 8],
        'y': [5.1, 5.22, 5.23, 5.3, 5.54, 5.9, 6.1, 6.3, 7.3, 8],
        'z': [5.1, 5.22, 5.23, 5.3, 6.64, 6.9, 7.1, 7.3, 8.3, 8]
        })

    # call the function on the test DataFrame
    result = find_bump_coords(data)

    # check that the correct number of bumps were detected
    assert len(result) == 6

    # check that the expected bump coordinates were detected
    expected_bumps = [(42.3601, -71.0589), (42.3602, -71.0588),
                      (42.3603, -71.0587), (42.3604, -71.0586),
                      (42.3609, -71.0581), (42.3610, -71.0580)]
    assert set(result) == set(expected_bumps)
