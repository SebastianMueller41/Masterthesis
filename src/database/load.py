"""
This module provides functions for interacting with a MySQL database, checking file existence, 
calling a SAT solver, calculating inconsistency values, and processing files in a directory.
"""

import os
import sys
import random
from src.database.database import create_ssh_tunnel_and_connect, log_execution_data
import subprocess
import tempfile


def log_execution_data(sql):
    """
    Execute an SQL statement to log execution data in the database.

    Args:
        sql (str): The SQL statement to execute.

    Returns:
        None
    """
    conn = create_ssh_tunnel_and_connect()
    if conn is not None:
        cursor = conn.cursor()
        try:
            cursor.execute(sql)
            conn.commit()
        finally:
            cursor.close()
            conn.close()
    else:
        print("Connection to MySQL database failed")


def check_filename_exists(filename):
    """
    Check if a filename already exists in the DATA_SETS table.

    Args:
        filename (str): The filename to check.

    Returns:
        bool: True if the filename exists in the database, False otherwise.
    """
    conn = create_ssh_tunnel_and_connect()
    if conn is not None:
        cursor = conn.cursor()
        try:
            query = "SELECT COUNT(*) FROM DATA_SETS WHERE filename = %s"
            cursor.execute(query, (filename,))
            result = cursor.fetchone()
            return result[0] > 0
        finally:
            cursor.close()
            conn.close()
    else:
        print("Connection to MySQL database failed")
        return False


def call_sat_solver(script_path, temp_filepath, option='c'):
    """
    Call the SAT solver script and return the output using a subset.

    Args:
        script_path (str): The path to the SAT solver script.
        temp_filepath (str): The path to the temporary file.
        option (str): The option to pass to the SAT solver script. Default is 'c'.

    Returns:
        int: The inconsistency measure obtained from the SAT solver.

    Raises:
        RuntimeError: If there is an error calling the SAT solver.
        ValueError: If the inconsistency measure could not be obtained.
    """
    try:
        result = subprocess.run(
            [sys.executable, script_path, temp_filepath, option], 
            capture_output=True, 
            text=True,
            check=True  # Ensures any subprocess errors are caught
        )
    except subprocess.CalledProcessError as e:
        print(f"Error calling SAT solver: {e}")
        print(f"Command: {e.cmd}")
        print(f"Return code: {e.returncode}")
        print(f"Output: {e.output}")
        print(f"Error output: {e.stderr}")
        raise RuntimeError(f"Error calling SAT solver: {e.stderr}") from e

    output_lines = result.stdout.splitlines()
    for line in output_lines:
        if line.startswith("o "):
            return int(line.split()[1])
    raise ValueError("Failed to obtain inconsistency measure from SAT solver.")


def calculate_values(filepath, script_path='sat4im/src/sat4im.py'):
    """
    Calculate inconsistency values for the dataset in the specified file.

    Args:
        filepath (str): The path to the dataset file.
        script_path (str): The path to the SAT solver script. Default is 'sat4im/src/sat4im.py'.

    Returns:
        None
    """
    initial_inconsistency_measure = call_sat_solver(script_path, filepath)

    with open(filepath, 'r') as file:
        lines = file.readlines()
    
    print(f"Initial inconsistency measure: {initial_inconsistency_measure}")

    range_of_values = list(range(1, len(lines) + 1))
    random.shuffle(range_of_values)

    inconsistency_differences = []
    for i in range(len(lines)):
        if lines[i].strip() == "":
            continue
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
            temp_file.writelines(lines[:i] + lines[i+1:])
            temp_filepath = temp_file.name

        try:
            inconsistency_measure = call_sat_solver(script_path, temp_filepath)
            inconsistency_difference = initial_inconsistency_measure - inconsistency_measure
            inconsistency_differences.append(inconsistency_difference)
            random_value = range_of_values[i]
            sql = f"INSERT INTO DATA_ENTRY (randomValue, inconsistencyValue, filename, line) VALUES ({random_value}, {inconsistency_difference}, '{filepath}', '{lines[i].strip()}')"
            print(sql)
            log_execution_data(sql)
        finally:
            os.remove(temp_filepath)


def list_files_excluding_db(root_folder):
    """
    List files in a directory and process them, excluding certain directories.

    Args:
        root_folder (str): The root directory to start listing files from.

    Returns:
        None
    """
    for dirpath, _, filenames in os.walk(root_folder):
        if dirpath in ["data/SRS", "data/Test_Datasets"]:
            continue
        print(dirpath)
        for filename in filenames:
            if filename == '.DS_Store':
                continue
            full_path = os.path.join(dirpath, filename)
            if check_filename_exists(full_path):
                print(f"Skipping {full_path} as it already exists in the database.")
                continue
            sql = f"INSERT INTO DATA_SETS (filename) VALUES ('{full_path}');"
            print(full_path)
            log_execution_data(sql)
            calculate_values(full_path, filename)


if __name__ == "__main__":
    root_folder = 'data'
    list_files_excluding_db(root_folder)
