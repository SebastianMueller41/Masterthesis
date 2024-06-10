import subprocess
import mysql.connector
from mysql.connector import Error

from src.database.database import create_ssh_tunnel_and_connect


def batch_run(filename):
    # Construct the command to run main.py with the dataset filename
    command = ["python", "main.py", filename, "0", "-k", "--alpha", "A0&&!A0"]
    
    # Execute the command
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running main.py for dataset {filename}: {e}")


def fetch_dataset_filenames_from_sql(conn):
    if conn is None:
        print("Failed to establish SSH tunnel and connect to the database")
        return []

    if conn.is_connected():
        cursor = conn.cursor(dictionary=True)
        try:
            query = f"SELECT * FROM EXE_RESULTS.DATA_SETS where filename like 'data/SRS/Dataset_A/sig3_5_15/srs_0%';"
            cursor.execute(query)
            rows = cursor.fetchall()

            # Print out the rows to inspect their structure
            print(rows)

            # Extract dataset filenames from the result set
            dataset_filenames = [row['filename'] for row in rows]

            return dataset_filenames
        
        except Error as e:
            print(f"Error fetching dataset filenames from SQL: {e}")
        finally:
            if conn.is_connected():
                cursor.close()

    else:
        print("Failed to connect to the database")
        return []

if __name__ == "__main__":

    conn = create_ssh_tunnel_and_connect()
    # List of dataset filenames obtained from SQL table
    dataset_filenames = fetch_dataset_filenames_from_sql(conn)

    # Close the SSH tunnel after fetching data
    if dataset_filenames:
        print(dataset_filenames)
        print("Closing SSH tunnel...")
        conn.close()

    for filename in dataset_filenames:
        batch_run(filename)
