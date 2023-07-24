import sys
import pandas as pd
import os
sys.path.append('/home/syrmia/Desktop/GPS_tracking_improved')
from func import read_data_file


def test_read_data_file():
    # create a test file
    test_file = 'test_file.csv'
    with open(test_file, 'w') as f:
        f.write('header1,header2\n')
        f.write('value1,value2\n')

    # test reading a valid file
    data = read_data_file(test_file)
    assert isinstance(data, pd.DataFrame)
    assert len(data) == 1
    assert list(data.columns) == ['header1', 'header2']
    assert list(data.iloc[0]) == ['value1', 'value2']

    # test reading an empty file
    with open(test_file, 'w') as f:
        f.write('header1,header2\n')
    assert read_data_file(test_file) is None

    # test reading a file that does not exist
    assert read_data_file('nonexistent_file.csv') is None

    # clean up the test file
    os.remove(test_file)
