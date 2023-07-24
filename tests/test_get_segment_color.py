import random
import sys
sys.path.append('/home/syrmia/Desktop/GPS_tracking_improved')
from func import get_segment_color


def generate_gps_coordinates(num_coords):
    coordinates = [(random.uniform(-180, 180),
                    random.uniform(-90, 90)) for i in range(num_coords)]
    return coordinates


z_data_segment_1 = [-10.777353102214956, -10.616294109919242,
                    -9.332074951653105, -10.73787706789625,
                    -9.642770502069054, -10.892680872820524,
                    -10.496781605618118, -10.769162179136199,
                    -9.92715678269657, -10.005161701636538,
                    -10.82846943205352, -9.969206125182886,
                    -9.527816132245249, -10.48201040990367,
                    -10.5956168927883, -9.523724090001746,
                    -9.712634445808366, -10.947046761405938,
                    -10.894737451982145, -10.779131645541797]

z_data_segment_2 = [-9.475618407794174, -9.227686497967147,
                    -9.338674719662693, -9.845903732016605,
                    -9.879984206373353, -9.772366497917721,
                    -9.606832509923633, -9.305592032334625,
                    -9.021902139988397, -9.378685233785445,
                    -9.020269496328758, -9.747354171308025,
                    -9.158860600753952, -9.461868929412445,
                    -9.521997006599422, -9.210101452509262,
                    -9.146551879675876, -9.272951472892554,
                    -9.283569100610546, -9.275920893577474]


# Test for no bumps and good smoothness of the road

def test_get_segment_color():

    segment = generate_gps_coordinates(20)
    bump_coords = []
    assert get_segment_color(segment, z_data_segment_1, bump_coords) == "green"

# Test for no bumps and bad smoothness of the road

    bump_coords = []
    assert get_segment_color(segment, z_data_segment_2, bump_coords) == "blue"

    # Test for a few bumps

    bump_coords = [segment[2], segment[6], segment[12], segment[14]]
    assert get_segment_color(segment, z_data_segment_1,
                             bump_coords) == "orange"

# Test for a few bumps

    bump_coords = [segment[2]]
    assert get_segment_color(segment, z_data_segment_1,
                             bump_coords) == "yellow"

    # Test for many bumps

    bump_coords = [segment[0], segment[1], segment[2], segment[3],
                   segment[4], segment[5], segment[6],
                   segment[7], segment[8], segment[9], segment[10]]
    assert get_segment_color(segment, z_data_segment_1, bump_coords) == "red"
