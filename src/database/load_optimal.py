"""
This module provides functions for parsing CSV files, computing hitting set values,
and inserting execution results into a MySQL database.
"""

import mysql.connector
import csv
from mysql.connector import Error
from src.database.database import create_ssh_tunnel_and_connect

def parse_csv(filename):
    """
    Parse a CSV file and extract execution runs and hitting sets.

    Args:
        filename (str): The path to the CSV file.

    Returns:
        list: A list of dictionaries, each containing execution parameters and hitting sets.
    """
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)

    all_runs = []
    current_run = {'params': None, 'hitting_sets': []}

    for row in rows:
        if row and row[0].replace('.', '', 1).isdigit() and len(row) > 7:
            if current_run['params']:
                all_runs.append(current_run)
                current_run = {'params': None, 'hitting_sets': []}
            current_run['params'] = row
        elif len(row) == 3:
            current_run['hitting_sets'].append(row)

    if current_run['params']:
        all_runs.append(current_run)

    return all_runs

def compute_hitting_set_values(conn, hitting_sets, filename):
    """
    Compute the values of hitting sets based on data entries in the MySQL database.

    Args:
        conn (mysql.connector.connection.MySQLConnection): The MySQL database connection.
        hitting_sets (list): The list of hitting sets to compute values for.
        filename (str): The filename associated with the data entries.

    Returns:
        list: A list of tuples containing hitting set values.
    """
    cursor = conn.cursor()

    hitting_set_values = []
    for hs in hitting_sets:
        hs_value, cardinality, elements_str = hs
        elements = elements_str.split(', ')
        
        # Compute sums
        random_sum = 0
        inconsistency_sum = 0
        for element in elements:
            cursor.execute("""
                SELECT randomValue, inconsistencyValue
                FROM EXE_RESULTS.DATA_ENTRY
                WHERE line = %s and filename = %s
            """, (element, filename,))
            row = cursor.fetchone()
            if row:
                random_sum += row[0]
                inconsistency_sum += row[1]
        
        hitting_set_values.append((filename, int(cardinality), random_sum, inconsistency_sum, elements_str))
    
    cursor.close()
    return hitting_set_values

def insert_results(conn, run):
    """
    Insert execution results and hitting set values into the MySQL database.

    Args:
        conn (mysql.connector.connection.MySQLConnection): The MySQL database connection.
        run (dict): A dictionary containing execution parameters and hitting sets.

    Returns:
        None
    """
    cursor = conn.cursor()

    # Extract execution parameters
    execution_params = run['params']
    hitting_sets = run['hitting_sets']

    # Debug: Print execution parameters to understand their structure
    print("Execution Parameters:", execution_params)

    # Ensure we have the expected number of parameters
    if len(execution_params) < 8:
        print("Skipping run due to insufficient execution parameters:", execution_params)
        return

    execution_time = float(execution_params[0])
    filename = execution_params[1]
    num_kernels = int(execution_params[3])
    num_branches = int(execution_params[4])
    tree_depth = int(execution_params[5])
    alpha = execution_params[6]

    # Compute hitting set values and insert into HITTING_SETS table
    hitting_set_values = compute_hitting_set_values(conn, hitting_sets, filename)
    try:
        for hs_value in hitting_set_values:
            cursor.execute("""
                INSERT INTO EXE_RESULTS.HITTING_SETS (
                    filename, cardinality, random_sum, inconsistency_sum, hitting_set
                ) VALUES (%s, %s, %s, %s, %s)
            """, hs_value)
        conn.commit()
    except Error as e:
        print(f"Failed to insert hitting set data into MySQL database: {e}")

    # Calculate the maximum values for the optimal hitting set
    max_cardinality = max(hs[1] for hs in hitting_set_values)
    max_random_value = max(hs[2] for hs in hitting_set_values)
    max_incon_value = max(hs[3] for hs in hitting_set_values)
    min_cardinality = min(hs[1] for hs in hitting_set_values)
    min_random_value = min(hs[2] for hs in hitting_set_values)
    min_incon_value = min(hs[3] for hs in hitting_set_values)
    num_leafs = len(hitting_set_values)

    # Insert execution results into OPTIMAL table
    try:
        cursor.execute("""
            INSERT INTO EXE_RESULTS.OPTIMAL (
                execution_time, filename, num_kernels, num_branches, tree_depth, alpha, max_cardinality, max_random_value, max_incon_value, min_random_value, min_incon_value, min_cardinality, num_leafs
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                execution_time = VALUES(execution_time),
                num_kernels = VALUES(num_kernels),
                num_branches = VALUES(num_branches),
                tree_depth = VALUES(tree_depth),
                alpha = VALUES(alpha),
                max_cardinality = VALUES(max_cardinality),
                max_random_value = VALUES(max_random_value),
                max_incon_value = VALUES(max_incon_value),
                min_random_value = VALUES(min_random_value),
                min_incon_value = VALUES(min_incon_value),
                min_cardinality = VALUES(min_cardinality),
                num_leafs = VALUES(num_leafs)
        """, (
            execution_time, filename, num_kernels, num_branches, tree_depth, alpha,
            max_cardinality, max_random_value, max_incon_value, min_random_value, min_incon_value, min_cardinality, num_leafs
        ))
        conn.commit()
    except Error as e:
        print(f"Failed to insert data into MySQL database: {e}")
    finally:
        cursor.close()

# Example usage
if __name__ == "__main__":
    conn = create_ssh_tunnel_and_connect()

    runs = parse_csv('Results/All_hitting_sets.csv')

    for run in runs:
        try:
            insert_results(conn, run)
        except ValueError as e:
            print(f"Error processing run: {e}. Skipping this run.")
        except IndexError as e:
            print(f"Error processing run due to index issue: {e}. Skipping this run.")

    conn.close()
