import serial
import mysql.connector
from mysql.connector import Error
import re
from datetime import datetime
import pytz

# MySQL database configuration
db_config = {
    'host': 'localhost',
    'user': 'RAHUL',
    'password': '7square',
    'database': 'attendance_database'
}

# Function to handle MySQL connection errors
def handle_connection_error(err):
    print('MySQL connection error:', err)
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Error: Invalid database credentials")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Error: Database does not exist")
    else:
        print("Error:", err)

# Connect to MySQL database
try:
    conn = mysql.connector.connect(**db_config)
    print("Connected to MySQL database")
except mysql.connector.Error as err:
    handle_connection_error(err)
    exit(1)

# Set the timezone to the desired timezone (e.g., 'Asia/Kolkata' for Indian Standard Time)
timezone = pytz.timezone('Asia/Kolkata')

# Map to store the last inserted timestamp for each ID
last_timestamps = {}

# Function to parse the serial monitor output and process the data
def parse_serial_output(data):
    lines = data.strip().split('\n')
    for line in lines:
        match = re.match(r'Found ID #(\d+) with confidence of \d+', line)
        if match:
            id = int(match.group(1))
            current_time = datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S')
            if id in last_timestamps:
                last_timestamp = last_timestamps[id]
                update_query = """
                    UPDATE another_table
                    SET time_out = %s
                    WHERE id = %s AND time_in = %s
                """
                try:
                    cursor = conn.cursor()
                    cursor.execute(update_query, (current_time, id, last_timestamp))
                    conn.commit()
                    cursor.close()
                    print(f'ID {id}: time_out updated to {current_time}')
                except Error as e:
                    handle_connection_error(e)
            else:
                insert_query = """
                    INSERT INTO another_table (id, time_in) VALUES (%s, %s)
                """
                try:
                    cursor = conn.cursor()
                    cursor.execute(insert_query, (id, current_time))
                    conn.commit()
                    cursor.close()
                    print(f'ID {id}: time_in inserted at {current_time}')
                    last_timestamps[id] = current_time
                except Error as e:
                    handle_connection_error(e)

# Open the serial port
try:
    port = serial.Serial('COM5', baudrate=9600)
    print("Serial port opened")
except serial.SerialException as e:
    print("Error: Unable to open serial port:", e)
    exit(1)

# Read data from the serial port and pass it to the parse_serial_output function
try:
    while True:
        data = port.readline().decode().strip()
        if data:
            parse_serial_output(data)
except KeyboardInterrupt:
    print("Exiting...")
    port.close()
    conn.close()
    exit(0)
