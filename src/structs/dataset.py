import copy
import sys
from mysql.connector import Error

import logging
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

class DataSet:
    """
    A class to manage a collection of elements.

    Provides methods to manipulate and persist the dataset.

    Attributes:
        elements (list): A list of elements representing the dataset.
    """
    
    def __init__(self, elements=None):
        """
        Initialize a new DataSet instance, optionally loading elements from a file and applying a value assignment strategy.

        Args:
            input_file_path (str, optional): The path to a file from which to load elements.
            elements (list, optional): An initial list of elements to populate the dataset.
            strategy (str, optional): The strategy identifier (e.g., "A1").
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
            The value assigned to the element, or None if the element is not found.
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
        summe = 0
        for element in self.elements:
            summe += ini_element_values[element]
        return summe


    def add_element(self, element):
            """
            Add an element to the dataset if it is not already present.
            Optionally, add a value for the element.

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
            self.elements.insert(0, element)  # Inserts element at the start of the list

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
            DataSet: A new DataSet instance containing the same elements and their values.
        """
        return DataSet(elements=list(self.elements))

    def split(self):
        """
        Splits the dataset into two halves.

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
            # Return a copy of the current dataset
            return DataSet(elements=list(set(self.get_elements())))
        
        # Use a set to ensure uniqueness
        combined_elements_set = set(self.get_elements()) | set(other.get_elements())
        # Return a new DataSet with the combined unique elements
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
    global ini_strategy_param

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

            # Process the rows as needed, skipping empty lines
            for row in rows:
                # Example processing: log non-empty rows
                if row['randomvalue'] == "" or row['inconsistencyvalue'] == "" or row['filename'] == "" or row['line'] == "":
                    continue
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

def apply_value_assignment_strategy():
    """
    Apply a value assignment strategy to each element in the dataset based on the specified parameter.

    Args:
        strategy_param (int): The parameter defining the value assignment strategy.
    """
    global ini_element_values

    if ini_strategy_param == 0:
        for element in ini_elements:
            ini_element_values[element] = 0
    elif ini_strategy_param == 1:
        for element in ini_elements:
            ini_element_values[element] = 1
            data_logger.warning(f"Value: {ini_element_values[element]}")

    if ini_strategy_param == 2:
        ini_element_values = ini_random_values
    if ini_strategy_param == 3:
        ini_element_values = ini_incon_values
    # Ensure all elements have values assigned
    for element in ini_elements:
        if element not in ini_element_values:
            ini_element_values[element] = 0

def get_incon_values():
    return ini_incon_values

def get_random_values():
    return ini_random_values

def get_strategy_param():
    return ini_strategy_param
