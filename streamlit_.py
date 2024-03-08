import mysql.connector
import pandas as pd
import streamlit as st

# MySQL database connection parameters
db_config = {
    'host': 'localhost',
    'database': 'attendance_database',
    'user': 'RAHUL',
    'password': '7square'
}

# Connect to MySQL database
try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    st.write("Connected to MySQL database")
except mysql.connector.Error as err:
    st.error(f"Error: Unable to connect to MySQL database: {err}")
    st.stop()

# Streamlit app title
st.title('Attendance Data')

# Query to fetch data from the table
query = "SELECT * FROM another_table"

# Execute the query
cursor.execute(query)
data = cursor.fetchall()

# Convert the data to a DataFrame
df = pd.DataFrame(data, columns=[desc[0] for desc in cursor.description])

# Execute the query to fetch names corresponding to IDs from id_names table
cursor.execute("SELECT id, name FROM id_names")
id_name_rows = cursor.fetchall()

# Create a dictionary to map each ID to its corresponding name
id_name_mapping = {row[0]: row[1] for row in id_name_rows}

# Display the DataFrame
if not df.empty:
    # Replace 'id' with 'name' using id_names table
    df['id'] = df['id'].map(id_name_mapping)
    
    # Calculate the time difference
    df['time_in'] = pd.to_datetime(df['time_in'])
    df['time_out'] = pd.to_datetime(df['time_out'])
    df['time_difference'] = df['time_out'] - df['time_in']
    df['time_difference'] = df['time_difference'].apply(lambda x: str(x).split()[-1])
    
    st.write("Attendance Data:")
    st.table(df.rename(columns={'id': 'name'}).drop(columns=['serial_number']))  # Rename 'id' column to 'name' and remove index column
else:
    st.warning("No data available.")

# Close connections
cursor.close()
conn.close()
