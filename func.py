import shutil
import os
import folium
import traceback
import openpyxl
from openpyxl.drawing.image import Image
import pandas as pd
import numpy as np
from haversine import haversine, Unit
from datetime import datetime
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

MIN_BUMPS_POOR = 5
MIN_BUMPS_FAIR = 2
MAX_BUMPS_GOOD = 0
SEGMENT_DISTANCE_THRESHOLD = 100        # meters
TIMESTAMP_FORMAT = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")


def read_data_file(file_path):
    """Reads a data file and returns a Pandas DataFrame"""
    try:
        with open(file_path, 'r') as f:
            f.readline().strip()
            second_line = f.readline().strip()
            if second_line == '':
                print(f"{file_path} is empty.")
                return None
        data = pd.read_csv(file_path, delimiter=',')
        return data
    except FileNotFoundError:
        print(f"{file_path} not found.")
        return None
    except pd.errors.EmptyDataError:
        print(f"{file_path} is empty.")
        return None


def merge_dataframes(accel_data, gps_data):
    """Merges the accelerometer and GPS data"""
    try:
        data = pd.merge(gps_data, accel_data, on='time')
        return data
    except KeyError:
        print("Both data files must have a 'time' column to merge.")
        return None


def find_bump_coords(data):
    """
    Finds the coordinates of bumps in the accelerometer data.

    Args:
        data (DataFrame): Data collected from sensors.

    Returns:
        list: List of GPS coordinates where bumps are detected.
    """
    z_data = data['z']
    threshold = np.percentile(np.abs(z_data), 70)
    bump_indices = np.where(np.abs((np.abs(z_data) - threshold)) >= 1)[0]

    bump_coords = []
    for i in bump_indices:
        bump_coords.append((data.loc[i, 'latitude'],
                            data.loc[i, 'longitude']))
    return bump_coords


def divide_into_segments(coordinates, z_data):
    """
    Divides the coordinates and accelerometer data
      into segments based on distance thresholds.

    Args:
        coordinates (list): List of GPS coordinates.
        accel_data (list): List of accelerometer data.

    Returns:
        tuple: A tuple containing lists of
        segments and accelerometer data segments.
    """
    z_data_segments = []
    z_data_segment = [z_data[0]]
    segments = []
    total_distance = 0
    segment = [coordinates[0]]
    for i in range(1, len(coordinates)):
        distance = haversine((coordinates[i-1][0], coordinates[i-1][1]),
                             (coordinates[i][0], coordinates[i][1]),
                             unit=Unit.METERS)
        total_distance += distance
        if total_distance >= SEGMENT_DISTANCE_THRESHOLD:
            segment.append(coordinates[i])
            segments.append(segment)
            segment = [coordinates[i]]
            z_data_segment.append(z_data[i])
            z_data_segments.append(z_data_segment)
            z_data_segment = [z_data[i]]
            total_distance = 0
        else:
            segment.append(coordinates[i])
            z_data_segment.append(z_data[i])
    segments.append(segment)
    z_data_segments.append(z_data_segment)
    return segments, z_data_segments


def get_segment_color(segment, z_data_segment, bump_coords):
    """Returns the color to use for a segment based on
       the number of bumps it contains
       and the smoothness of the road.

    Args:
        segment (list): List of GPS coordinates.
        accel_data_segment (list): List of respective z_data values.
        bump_coords (list): List of GPS coordinates of detected bumps.

    Returns:
        string: Color used for drawing a map and qualifying road quality.
    """
    z_data_segment = np.array(z_data_segment)
    count = 0
    for item in segment:
        if item in bump_coords:
            count += 1
    if count >= MIN_BUMPS_POOR:
        color = 'red'
    elif (MIN_BUMPS_FAIR <= count
          and count < MIN_BUMPS_POOR):
        color = 'orange'
    elif MAX_BUMPS_GOOD < count < MIN_BUMPS_FAIR:
        color = 'yellow'
    elif count <= MAX_BUMPS_GOOD:
        if np.std(z_data_segment) >= 0.5:
            color = 'green'
        else:
            color = "blue"
    return color


def plot_segment(segment, z_data_segment, bump_coords, my_map):
    """Plots a segment on a map with a color based
       on the number of bumps it contains.

    Args:
        segment (list): GPS coordinates of one of road segments.
        accel_data_segment(list): Accel_data values for one road segment.
        bump_coords (list): List of GPS coordinates where bumps are detected.
        my_map: Map object.
    """

    color = get_segment_color(segment, z_data_segment, bump_coords)
    folium.PolyLine(segment, color=color, weight=6).add_to(my_map)


def plot_map(segments, z_data_segments,
             bump_coords, folder_results):
    """
    Plot the segments and associated accelerometer data on a folium map.

    Args:
        segments (list): List of segments, where each segment
          is a list of coordinates.
        accel_data_segments (list): List of accelerometer data segments,
          where each segment is a list of accelerometer data.
        bump_coords (list): List of bump coordinates.
        flag_show (int): Flag indicating whether to open the map
                         in a web browser.
                        Set to 1 to open, 2 to not open.
        folder_results (str): Path to the folder where the map HTML file
          will be saved.

    Returns:
        None
    """
    start_position = segments[0][0]
    i = 0
    my_map = folium.Map(location=start_position, zoom_start=15)
    for segment in segments:
        plot_segment(segment, z_data_segments[i], bump_coords, my_map)
        i += 1

    legend_html = '''
    <div style="position: fixed;
                top: 30px; right: 30px; width: 120px; height: 150px;
                border:4px solid black; z-index:9999; font-size:15px;
                background-color:lightblue;
                ">&nbsp; Road quality: <br>
                &nbsp; &#x1F535 - excellent <br>
                &nbsp; &#x1F7E2 - good <br>
                &nbsp; &#x1F7E1 - fair <br>
                &nbsp; &#x1F7E0 - poor <br>
                &nbsp; &#x1F534 - very poor <br>
    </div>
'''
    my_map.get_root().html.add_child(folium.Element(legend_html))

    map_name = f'map_{TIMESTAMP_FORMAT}.html'
    map_path = os.path.join(folder_results, map_name)
    my_map.save(map_path)
    return os.path.abspath(map_path)


def remove_files(file_1, file_2):
    """Removing files if they are empty or wrong format.

    Args:
        file_1 (<class 'str'>)): File path of first file to be deleted.
        file_2 (<class 'str'>)): File path of second file to be deleted.
    """
    os.remove(file_1)
    os.remove(file_2)


def road_duration(data):
    """
    Calculates the duration of a road based on the time data.

    Args:
        data (dict): Data from sensors.

    Returns:
        datetime.timedelta: The duration of the road segment.
    """
    times = data['time']
    start_time = datetime.strptime(times[0], "%H:%M:%S")
    end_time = datetime.strptime(times[len(times)-1], "%H:%M:%S")
    duration = end_time - start_time
    return duration


def road_distance(coords):
    """
    Calculates the distance of a road based on the given coordinates.

    Args:
        coords (list): List of GPS coordinates.

    Returns:
        float: The distance of the road in kilometers,
          rounded to 2 decimal places.
    """
    distance = 0
    for i in range(1, len(coords)):
        distance += haversine(coords[i-1], coords[i],
                              unit=Unit.KILOMETERS)
    distance = format(distance, ".2f")
    return distance


def bumps_statistics(z_data):
    """
    Calculates statistics of bumps based on the provided accelerometer data.

    Args:
        z_data (list): List of accelerometer data along the z-axis.

    Returns:
        tuple: A tuple containing the following statistics:
            - all_bumps (int): The total number of detected bumps.
            - big_bumps (int): The number of bumps categorized as big.
            - medium_bumps (int): The number of bumps categorized as medium.
            - small_bumps (int): The number of bumps categorized as small.
    """
    all_bumps = 0
    big_bumps = 0
    medium_bumps = 0
    small_bumps = 0
    threshold = np.percentile(np.abs(z_data), 70)
    for i in z_data:
        if 1 < np.abs((np.abs(i) - threshold)) < 1.5:
            all_bumps += 1
            small_bumps += 1
        elif 1.5 <= np.abs((np.abs(i) - threshold)) < 2:
            all_bumps += 1
            medium_bumps += 1
        elif (np.abs(np.abs(i) - threshold)) >= 2:
            all_bumps += 1
            big_bumps += 1
    return all_bumps, big_bumps, medium_bumps, small_bumps


def create_road_statistics(map, duration, distance, bumps,
                           folder_results):
    workbook = openpyxl.Workbook()
    road_statistics_name = f'road_statistics_{TIMESTAMP_FORMAT}.xlsx'
    road_statistics_path = os.path.join(folder_results, road_statistics_name)
    rating = calculate_road_rating(duration, distance, bumps[0])
    sheet = workbook.active
    sheet.column_dimensions["A"].width = 20
    sheet.column_dimensions["B"].width = 20
    sheet["A1"] = "Duration:"
    sheet["B1"] = duration
    sheet["A2"] = "Length (Km)"
    sheet["B2"] = distance
    sheet["A4"] = "Number of bumps:"
    sheet["B4"] = bumps[0]
    sheet["B5"] = "Big bumps"
    sheet["C5"] = bumps[1]
    sheet["B6"] = "Medium bumps:"
    sheet["C6"] = bumps[2]
    sheet["B7"] = "Small bumps:"
    sheet["C7"] = bumps[3]
    sheet["A8"] = "Road rating:"
    sheet["B8"] = rating
    img = Image(map)
    sheet.add_image(img, "A10")
    img.width = img.width * 1.5
    img.height = img.height * 1.5
    workbook.save(road_statistics_path)


def calculate_road_rating(duration, distance, num_bumps):
    """
    Calculate the rating of a road based on the duration,
      distance, and number of bumps encountered.

    Args:
        duration (datetime.timedelta): The duration of travel.
        distance (float): The distance traveled in kilometers.
        num_bumps (int): The number of bumps encountered during the travel.

    Returns:
        str: The road rating, which can be one of the following:
          "Excellent", "Good", "Fair", or "Poor".
    """

    duration = (duration.total_seconds()) / 60
    distance = float(distance)
    if duration <= 0 or num_bumps < 0 or distance <= 0:
        return "Invalid input. Please provide positive values."
    average_bumps_per_km = num_bumps / distance
    bumps_per_minute = num_bumps / duration

    if bumps_per_minute < 0.1:
        return "Excellent"
    elif bumps_per_minute < 0.3:
        if average_bumps_per_km < 0.5:
            return "Good"
        else:
            return "Fair"
    elif bumps_per_minute < 0.6:
        if average_bumps_per_km < 1.5:
            return "Fair"
        else:
            return "Poor"
    else:
        return "Poor"


def html_to_png(html_file, png_file):
    # Set up Chrome WebDriver and configure it to run in headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)

    # Load the HTML file in the WebDriver
    driver.get(f'file://{html_file}')
    sleep(3)

    # Capture the full page by scrolling to the end
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Save the screenshot
    driver.save_screenshot(png_file)

    # Close the WebDriver
    driver.quit()


def process_data(file_path_accel, file_path_gps,
                 folder_data, folder_results, flag_show):
    """The function processes data from two files
    (one containing accelerometer data and the other containing GPS data),
    merges the data, finds bump coordinates,
    plots the data on a OpenStreet Map.
    If an error occurs during the processing,
    the function prints an error message to the console.

    Args:
        file_path_accel (<class 'str'>)): Path of file containig
        accelerometer data.
        file_path_gps (<class 'str'>)): Path of file containig GPS data.
        folder_data (<class 'str'>): Path of folder where we store files.
        folder_results (<class 'str'>): Path of folder where we store result.
        flag_show (integer): Flag used to decide if we want
        to see resulting map.
    """
    try:
        accel_data = read_data_file(file_path_accel)
        gps_data = read_data_file(file_path_gps)

        if accel_data is None or gps_data is None:
            remove_files(file_path_accel, file_path_gps)
            print("No data to process!")
            return

        data = merge_dataframes(gps_data, accel_data)
        bump_coords = find_bump_coords(data)
        z_data = data['z']
        latitudes = data['latitude']
        longitudes = data['longitude']

        coords = list(zip(latitudes, longitudes))
        segments = divide_into_segments(coords, z_data)[0]
        accel_data_segments = divide_into_segments(coords, z_data)[1]
        map_path = plot_map(segments, accel_data_segments, bump_coords,
                            folder_results)

        duration = road_duration(data)
        distance = road_distance(coords)
        bumps = bumps_statistics(z_data)
        image_name = f'image_{TIMESTAMP_FORMAT}.png'
        image_path = os.path.join(folder_results, image_name)
        html_to_png(map_path, image_path)
        create_road_statistics(image_path, duration, distance, bumps,
                               folder_results)

        shutil.move(file_path_accel, folder_data)
        shutil.move(file_path_gps, folder_data)

    except FileNotFoundError as e:
        print(f'File not found: {e.filename}.'
              f'Please check the file path and try again.')
    except Exception as e:
        print(f'An error occurred: {e}')
        print(traceback.format_exc())

        # If an error occurs during processing, delete the files to avoid
        # leaving incomplete or corrupted data in the system
        remove_files(file_path_accel, file_path_gps)
