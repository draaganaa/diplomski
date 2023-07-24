import os
import sys
sys.path.append('/home/syrmia/Desktop/GPS_tracking_improved')
from func import remove_files


def test_remove_files():
    # create some temporary files for testing
    file1 = 'temp_file1.txt'
    file2 = 'temp_file2.txt'
    with open(file1, 'w') as f1, open(file2, 'w') as f2:
        f1.write('This is a test.')
        f2.write('This is another test.')

    # call the remove_files function
    remove_files(file1, file2)

    # assert that the files no longer exist
    assert not os.path.isfile(file1)
    assert not os.path.isfile(file2)
