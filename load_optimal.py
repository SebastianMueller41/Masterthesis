from mysql.connector import Error
import csv
import mysql.connector

from src.database.database import create_ssh_tunnel_and_connect

def parse_csv(filename):
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
    max_random_sum = max(hs[2] for hs in hitting_set_values)
    max_inconsistency_sum = max(hs[3] for hs in hitting_set_values)

    # Insert execution results into OPTIMAL table
    try:
        cursor.execute("""
            INSERT INTO EXE_RESULTS.OPTIMAL (
                execution_time, filename, num_kernels, num_branches, tree_depth, alpha, optimal_cardinality, optimal_hs_random, optimal_hs_incon
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                execution_time = VALUES(execution_time),
                num_kernels = VALUES(num_kernels),
                num_branches = VALUES(num_branches),
                tree_depth = VALUES(tree_depth),
                alpha = VALUES(alpha),
                optimal_cardinality = VALUES(optimal_cardinality),
                optimal_hs_random = VALUES(optimal_hs_random),
                optimal_hs_incon = VALUES(optimal_hs_incon)
        """, (execution_time, filename, num_kernels, num_branches, tree_depth, alpha, max_cardinality, max_random_sum, max_inconsistency_sum))
        conn.commit()
    except Error as e:
        print(f"Failed to insert data into MySQL database: {e}")
    finally:
        cursor.close()

# Example usage
conn = create_ssh_tunnel_and_connect()

runs = parse_csv('Results/All_hitting_sets_sig3.csv')

for run in runs:
    try:
        insert_results(conn, run)
    except ValueError as e:
        print(f"Error processing run: {e}. Skipping this run.")
    except IndexError as e:
        print(f"Error processing run due to index issue: {e}. Skipping this run.")

conn.close()
