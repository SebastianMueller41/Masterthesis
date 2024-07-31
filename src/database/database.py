"""
This module provides functions for logging execution data to a MySQL database and
establishing a connection to the database, potentially through an SSH tunnel.
"""

import logging
import mysql.connector
import json
import socket
from mysql.connector import Error
from sshtunnel import SSHTunnelForwarder

def log_execution_data(connection, execution_time, resources_used, dataset_content, strategy_param, num_kernels, num_branches, tree_depth, pruned_branches, filename, optimal_hitting_set, shrink_div_conq, expand_sw_size, alpha, search_strat, optimal_value, expand_div_conq, shrink_sw_size, optimal_cardinality, pruner, lowerBound, upperBound, optimal_found):
    """
    Log execution data to the MySQL database.

    Args:
        connection (mysql.connector.connection.MySQLConnection): The MySQL database connection.
        execution_time (float): The execution time of the operation.
        resources_used (str): The resources used during execution.
        dataset_content (dict): The content of the dataset.
        strategy_param (str): Strategy parameters used.
        num_kernels (int): The number of kernels computed.
        num_branches (int): The number of branches processed.
        tree_depth (int): The depth of the tree.
        pruned_branches (int): The number of pruned branches.
        filename (str): The name of the file.
        optimal_hitting_set (list): The optimal hitting set found.
        shrink_div_conq (bool): Whether divide-and-conquer was used in the shrink phase.
        expand_sw_size (int): The sliding window size used in the expand phase.
        alpha (str): The alpha value used.
        search_strat (str): The search strategy used.
        optimal_value (float): The optimal value found.
        expand_div_conq (bool): Whether divide-and-conquer was used in the expand phase.
        shrink_sw_size (int): The sliding window size used in the shrink phase.
        optimal_cardinality (int): The optimal cardinality found.
        pruner (str): The pruner used.
        lowerBound (float): The lower bound value.
        upperBound (float): The upper bound value.
        optimal_found (bool): Whether the optimal solution was found.

    Returns:
        None
    """
    # Convert both optimal_solution and dataset_content to JSON strings
    optimal_solution = json.dumps(optimal_hitting_set)
    dataset_content_json = json.dumps(dataset_content)  # Convert dataset_content to a JSON string
    # upperBound might have the value 'inf'
    upperBound = None if upperBound == float('inf') else upperBound
    cursor = connection.cursor()
    try:
        cursor.execute('''
            INSERT INTO RESULTS (execution_time, resources_used, dataset_content, strategy_param, num_kernels, num_branches, tree_depth, pruned_branches, filename, optimal_solution, shrink_div_conq, expand_sw_size, alpha, search_strategy, optimal_value, expand_div_conq, shrink_sw_size, optimal_cardinality, pruner, lowerBound, upperBound, optimal_found)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (execution_time, resources_used, dataset_content_json, strategy_param, num_kernels, num_branches, tree_depth, pruned_branches, filename, optimal_solution, shrink_div_conq, expand_sw_size, alpha, search_strat, optimal_value, expand_div_conq, shrink_sw_size, optimal_cardinality, pruner, lowerBound, upperBound, optimal_found))
        connection.commit()
    except Error as e:
        print(f"Failed to insert data into MySQL database: {e}")
    finally:
        cursor.close()

def create_ssh_tunnel_and_connect():
    """
    Create an SSH tunnel and connect to the MySQL database.

    Returns:
        mysql.connector.connection.MySQLConnection: The MySQL database connection, or None if the connection failed.
    """
    # Get the local IP address
    local_host = socket.gethostname()

    # Define the server
    server_host = 'student5aig'

    if local_host == server_host:
        print("RUNNING ON SERVER!")
        # Program is running on the server, no SSH tunnel needed
        db_host = '127.0.0.1'
        db_name = 'EXE_RESULTS'
        db_user = '' # DB User
        db_password = ''# DB PW if set
    else:
        print("RUNNING LOCALLY!")
        ssh_host = '132.176.10.110'
        ssh_port = 22  # default SSH port
        ssh_username = '' # path to SSH-file
        ssh_password = '' # ssh PW or path to private file
        ssh_key = ''
        db_host = '127.0.0.1'
        db_name = 'EXE_RESULTS'
        db_user = '' # DB User
        db_password = '' # DB PW if set

        try:
            # Set up the SSH tunnel
            tunnel = SSHTunnelForwarder(
                (ssh_host, ssh_port),
                ssh_username=ssh_username,
                ssh_password=ssh_key,
                ssh_pkey=ssh_password,  
                remote_bind_address=(db_host, 3306),
                local_bind_address=('127.0.0.1', 3307) 
            )

            tunnel.start()

            # Connect to the MySQL database through the SSH tunnel
            connection = mysql.connector.connect(
                host='127.0.0.1',
                port=tunnel.local_bind_port,
                database=db_name,
                user=db_user,
                password=db_password,
                use_pure=True
            )

            if connection.is_connected():
                print("Connection to MySQL database successful")
                return connection
            else:
                print("Connection to MySQL database failed")
                return None

        except Error as e:
            print(f"Error: {e}")
            return None

        except Exception as e:
            print(f"SSH Tunnel Error: {e}")
            return None

    try:
        # Connect to the MySQL database
        connection = mysql.connector.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password
        )

        if connection.is_connected():
            print("Connection to MySQL database successful")
            return connection
        else:
            print("Connection to MySQL database failed")
            return None

    except Error as e:
        print(f"Error connecting to MySQL Database: {e}")
        return None
