import csv
import serial
import pynmea2
import time
from time import sleep
from datetime import datetime
from mpu6050 import mpu6050
from haversine import haversine, Unit
from func import process_data


MPU6050_REGISTER = 0x68
SERIAL_PORT = '/dev/ttyAMA0'
BAUD_RATE = 9600
GPS_TIMEOUT = 1  # in seconds
ACCEL_RANGE = 16
DATA_FOLDER = "./data"
DATA_RESULTS = "./results"
THRESHOLD_DISTANCE = 0


class VehicleNotMovingException(Exception):
    "Raised when vehicle has stopped moving for more than 5 minutes"
    pass


def initialize_gps():
    """Initialize the GPS sensor"""
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=GPS_TIMEOUT)
    return ser


def initialize_accelerometer():
    """Initialize the MPU6050 accelerometer"""
    sensor = mpu6050(MPU6050_REGISTER)
    sensor.set_accel_range(ACCEL_RANGE)
    return sensor


def create_csv_file(file_name, headers):
    """Create and open a CSV file with the given name and write the headers"""
    file = open(file_name, "w", newline="")
    writer = csv.writer(file)
    writer.writerow(headers)
    return file, writer


def read_gps_data(ser):
    """Read GPS data from the serial port and parse the NMEA message"""
    data = ser.readline().decode('unicode_escape')
    if not data:
        raise ValueError("No data received from NEO 6M sensor,"
                         "please check connection and run the app again!")
    if data.startswith('$GPRMC'):
        msg = pynmea2.parse(data)
        return msg.latitude, msg.longitude, msg.spd_over_grnd
    return None, None, None


def read_accelerometer_data(sensor):
    """Read accelerometer data"""
    accel_data = sensor.get_accel_data()
    return accel_data.get("x"), accel_data.get("y"), accel_data.get("z")


def main():
    """Main function to read GPS and accelerometer data"""

    prev_lat, prev_lon = 0, 0
    signal_lost = False
    INACTIVE_TIMEOUT = (time.time() + 60 * 5)  # in seconds

    # Creates and opens CSV files for data storage

    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    accel_file_name = f'accel_data_{timestamp}.csv'
    gps_file_name = f'gps_data_{timestamp}.csv'

    accel_file, accel_writer = create_csv_file(accel_file_name,
                                               ['x', 'y', 'z', 'time'])
    gps_file, gps_writer = create_csv_file(gps_file_name,
                                           ['latitude', 'longitude', 'time'])
    print("---Reading data will start after detecting movement of vehicle---")

    try:
        ser = initialize_gps()
        sensor = initialize_accelerometer()

        while True:
            lat, lon, speed = read_gps_data(ser)

            if speed is not None:
                if prev_lat == 0 and prev_lon == 0:
                    prev_lat = lat
                    prev_lon = lon
                else:
                    distance = haversine((prev_lat, prev_lon), (lat, lon),
                                         unit=Unit.METERS)
                    if distance >= THRESHOLD_DISTANCE:
                        time_ = datetime.now().strftime("%H:%M:%S")
                        print('Timestamp:', time_)
                        print('Latitude:', lat)
                        print('Longitude:', lon)
                        gps_writer.writerow([lat, lon, time_])

                        ax, ay, az = read_accelerometer_data(sensor)
                        print(f'\tax={ax:.2f} g\tay={ay:.2f} g\taz={az:.2f} g')
                        accel_writer.writerow([ax, ay, az, time_])
                        sleep(1)
                    elif (distance < THRESHOLD_DISTANCE and
                          time.time() > INACTIVE_TIMEOUT):
                        raise VehicleNotMovingException
                    ("Vehicle didn't move for more than 5 minutes.")

                    prev_lat = lat
                    prev_lon = lon
                    INACTIVE_TIMEOUT = time.time() + 60 * 5  # Reset

            elif speed is None:
                if not signal_lost:
                    print("Lost signal, searching for satellites,"
                          "wait until LED starts blinking!")
                    signal_lost = True
                    INACTIVE_TIMEOUT = time.time() + 60 * 5  # Reset

            if signal_lost:
                if speed is not None:
                    print("Signal found, resuming GPS tracking.")
                    signal_lost = False

    except (KeyboardInterrupt, VehicleNotMovingException, ValueError):
        accel_file.close()
        gps_file.close()
        print("GPS tracking stopped!")
        print("Saving road statistics...")
        process_data(gps_file_name, accel_file_name,
                     DATA_FOLDER, DATA_RESULTS)


main()
