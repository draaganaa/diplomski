import sys
import pandas as pd
sys.path.append('/home/syrmia/Desktop/GPS_tracking_improved')
from func import merge_dataframes


def test_merge_dataframes():
    # create example dataframes
    accel_data = pd.DataFrame({'x': [1.1, 2.2, 3.3], 'y': [5.5, 6.7, 3.4],
                               'z': [4.5, 7.8, 3.3], 'time': [1, 2, 3]})
    gps_data = pd.DataFrame({'latitude': [40, 41, 42],
                             'longitude': [-74, -73, -72], 'time': [1, 2, 3]})

    # call the function
    merged_data = merge_dataframes(accel_data, gps_data)

    # assert the result is as expected
    assert len(merged_data) == 3
    assert list(merged_data.columns) == ['latitude',
                                         'longitude', 'time', 'x', 'y', 'z']
