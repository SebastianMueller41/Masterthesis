"""
This module provides the DataSet class for managing a collection of elements and various functions 
for initializing and manipulating datasets, including loading from files or databases and applying 
value assignment strategies.
"""

import sys
from mysql.connector import Error
import logging
from src.database.load import call_sat_solver
from src.structs.logger import setup_logging

# Set up logging for this module
setup_logging()

# Get the logger for this module
data_logger = logging.getLogger(__name__)

# Global variables
ini_strategy_param = 0
ini_elements = []
ini_element_values = {}
ini_random_values = {}
ini_incon_values = {}
ini_max_incon_value = 0
ini_filename = ''

class DataSet:
    """
    A class to manage a collection of elements.

    Provides methods to manipulate and persist the dataset.

    Attributes:
        elements (list): A list of elements representing the dataset.
    """
    
    def __init__(self, elements=None):
        """
        Initialize a new DataSet instance.

        Args:
            elements (list, optional): An initial list of elements to populate the dataset.
        """
        self.elements = elements if elements is not None else []
        self.strategy_param = ini_strategy_param

    def get_elements(self):
        """
        Retrieve the elements of the dataset.

        Returns:
            list: The elements contained in the dataset.
        """
        return self.elements if self.elements is not None else []

    def get_elements_with_values(self):
        """
        Retrieve the elements of the dataset along with their assigned values.

        Returns:
            list of tuples: Each tuple contains an element and its corresponding value.
        """
        return [(element, ini_element_values[element]) for element in self.elements]
    
    def get_element_value(self, element):
        """
        Retrieve the value assigned to the specified element.

        Args:
            element (str): The element for which to retrieve the value.

        Returns:
            The value assigned to the element, or 0 if the element is not found.
        """
        return ini_element_values.get(element, 0)

    def get_values(self):
        """
        Retrieve the values assigned to the elements of the dataset.

        Returns:
            list: A list of values assigned to the elements.
        """
        return list(ini_element_values.values())
    
    def sum_values(self):
        """
        Calculate the sum of the values of all elements in the dataset.

        Returns:
            int: The sum of the values of the elements.
        """
        return sum(ini_element_values[element] for element in self.elements)

    def add_element(self, element):
        """
        Add an element to the dataset if it is not already present.

        Args:
            element (str): The element to add to the dataset.
        """
        if element not in self.elements:
            self.elements.append(element)
    
    def add_element_at_start(self, element):
        """
        Add an element to the start of the dataset if it is not already present.

        Args:
            element (str): The element to add to the dataset.
        """
        if element not in self.elements:
            self.elements.insert(0, element)

    def remove_element(self, element):
        """
        Remove the specified element from the dataset if it exists.

        Args:
            element (str): The element to remove from the dataset.
        """
        try:
            self.elements.remove(element)
        except ValueError:
            data_logger.warning(f"Element {element} not found in the dataset.")

    def clone(self):
        """
        Create a copy of the current DataSet instance.

        Returns:
            DataSet: A new DataSet instance containing the same elements.
        """
        return DataSet(elements=list(self.elements))

    def split(self):
        """
        Split the dataset into two halves.

        Returns:
            tuple of DataSet: Two DataSet instances representing the split dataset.
        """
        mid_index = len(self.elements) // 2
        first_half = DataSet(elements=self.elements[:mid_index])
        second_half = DataSet(elements=self.elements[mid_index:])
        return first_half, second_half
    
    def combine(self, other):
        """
        Combine two datasets into one, ensuring each element is unique.

        Args:
            other (DataSet): The other dataset to combine with this one.

        Returns:
            DataSet: A new dataset containing unique elements from both datasets.
        """
        if other is None:
            return DataSet(elements=list(set(self.get_elements())))
        
        combined_elements_set = set(self.get_elements()) | set(other.get_elements())
        return DataSet(elements=list(combined_elements_set))

    def size(self):
        """
        Returns the number of elements in the dataset.

        Returns:
            int: The size of the dataset.
        """
        return len(self.elements)

    def to_file(self, output_file_path):
        """
        Write the elements of the dataset to a file, one element per line.

        Args:
            output_file_path (str): The file path where the dataset will be written.
        """
        with open(output_file_path, 'w') as file:
            for element in self.elements:
                file.write(element + '\n')

# --------------------------------------------------------------------------------------- #
# --------------------------------------------------------------------------------------- #

def initialize_dataset(conn, input_file_path, strategy_param, db):
    """
    Initialize the dataset by loading elements from a file or database and applying a value assignment strategy.

    Args:
        conn (mysql.connector.connection.MySQLConnection): The MySQL database connection.
        input_file_path (str): The path to the input file.
        strategy_param (int): The strategy parameter for value assignment.
        db (bool): Flag to indicate if loading from a database.

    Returns:
        DataSet: The initialized dataset.
    """
    global ini_strategy_param
    global ini_filename

    ini_filename = input_file_path
    ini_strategy_param = strategy_param

    if input_file_path:
        if db:
            load_elements_from_db(conn, input_file_path)
        else:
            load_elements_from_file(input_file_path)
    
    if ini_strategy_param is not None:
        apply_value_assignment_strategy()
    
    return DataSet(ini_elements)

def load_elements_from_file(file_path):
    """
    Load elements from the specified file path into the dataset.
    Each line in the file is treated as a separate element.

    Args:
        file_path (str): The path to the input file.

    Returns:
        None
    """
    global ini_elements
    global ini_element_values
    try:
        with open(file_path, 'r') as file:
            ini_elements = [line.strip() for line in file.readlines()]
            data_logger.debug(f"Dataset loaded: {ini_elements}")
    except FileNotFoundError:
        sys.exit(f"File {file_path} not found.\nPlease check file path: {file_path}.")

def load_elements_from_db(conn, file_path):
    """
    Load elements from the database into the dataset.

    Args:
        conn (mysql.connector.connection.MySQLConnection): The MySQL database connection.
        file_path (str): The filename used to query the database.

    Returns:
        None
    """
    global ini_elements
    global ini_element_values
    global ini_random_values
    global ini_incon_values
    
    if conn is not None:
        cursor = conn.cursor(dictionary=True)
        try:
            query = f"SELECT randomvalue, inconsistencyvalue, filename, line FROM DATA_ENTRY where filename='{file_path}'"
            cursor.execute(query)
            rows = cursor.fetchall()

            for row in rows:
                if all(row.values()):
                    data_logger.debug(f"Random Value: {row['randomvalue']}, Inconsistency Value: {row['inconsistencyvalue']}, Filename: {row['filename']}, Formula: {row['line']}")
                    ini_elements.append(row['line'])
                    ini_random_values[row['line']] = row['randomvalue']
                    ini_incon_values[row['line']] = row['inconsistencyvalue']

        except Error as e:
            data_logger.error(f"Failed to load data from MySQL database: {e}")
        finally:
            cursor.close()
    else:
        data_logger.error("Connection to MySQL database failed")

    calculate_initial_inconsistency_bound(file_path)

def apply_value_assignment_strategy():
    """
    Apply a value assignment strategy to each element in the dataset based on the specified parameter.

    Returns:
        None
    """
    global ini_element_values

    if ini_strategy_param == 0:
        for element in ini_elements:
            ini_element_values[element] = 0
    elif ini_strategy_param == 1:
        for element in ini_elements:
            ini_element_values[element] = 1
            data_logger.warning(f"Value: {ini_element_values[element]}")
    elif ini_strategy_param == 2:
        ini_element_values = ini_random_values
    elif ini_strategy_param == 3:
        ini_element_values = ini_incon_values
    
    for element in ini_elements:
        if element not in ini_element_values:
            ini_element_values[element] = 0

def calculate_initial_inconsistency_bound(file_path):
    """
    Calculate the initial inconsistency bound for the dataset using a SAT solver.

    Args:
        file_path (str): The path to the input file.

    Returns:
        None
    """
    global ini_max_incon_value
    ini_max_incon_value = call_sat_solver('sat4im/src/sat4im.py', file_path, option='c')

def get_max_incon_value():
    """
    Get the maximum inconsistency value for the dataset.

    Returns:
        int: The maximum inconsistency value.
    """
    return ini_max_incon_value

def get_incon_values():
    """
    Get the inconsistency values for the dataset elements.

    Returns:
        dict: A dictionary of elements and their inconsistency values.
    """
    return ini_incon_values

def get_random_values():
    """
    Get the random values for the dataset elements.

    Returns:
        dict: A dictionary of elements and their random values.
    """
    return ini_random_values

def get_strategy_param():
    """
    Get the strategy parameter used for value assignment.

    Returns:
        int: The strategy parameter.
    """
    return ini_strategy_param

def get_filename():
    """
    Get the filename of the dataset.

    Returns:
        str: The filename.
    """
    return ini_filename
