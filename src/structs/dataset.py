"""
This module defines the DataSet class, which is used to manage a collection of elements
typically representing data items or clauses in computational logic. The DataSet class
provides functionality to load data from a file, access elements, add or remove elements,
clone itself, and write its contents to a file.
"""

import logging
from src.database.database import create_connection, create_ssh_tunnel_and_connect
import sys
from mysql.connector import Error

# Configure logging
logging.basicConfig(filename='dataset.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(message)s')

class DataSet:
    """
    A class to manage a collection of elements.

    Provides methods to manipulate and persist the dataset.

    Attributes:
        elements (list): A list of elements representing the dataset.
    """
    
    def __init__(self, input_file_path=None, strategy_param=None, elements=None, strategy=None):
        """
        Initialize a new DataSet instance, optionally loading elements from a file and applying a value assignment strategy.

        Args:
            input_file_path (str, optional): The path to a file from which to load elements.
            elements (list, optional): An initial list of elements to populate the dataset.
            strategy (str, optional): The strategy identifier (e.g., "A1").
            strategy_param (int, optional): The parameter that defines how values are assigned to the elements.
        """
        self.elements = elements if elements is not None else []
        self.element_values = {}  # Initialize the mapping of elements to values
        self.strategy_param = strategy_param
        if input_file_path:
            self.load_elements_from_db(input_file_path)
        if strategy_param:
            self.apply_value_assignment_strategy(strategy_param)

    def load_elements_from_file(self, file_path):
        """
        Load elements from the specified file path into the dataset.
        Each line in the file is treated as a separate element.
        """
        try:
            with open(file_path, 'r') as file:
                self.elements = [line.strip() for line in file.readlines()]
        except FileNotFoundError:
            sys.exit(f"File {file_path} not found.\nPlease check file path: {file_path}.")
    
    def load_elements_from_db(self, file_path):
        conn = create_ssh_tunnel_and_connect()

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
                    logging.debug(f"Random Value: {row['randomvalue']}, Inconsistency Value: {row['inconsistencyvalue']}, Filename: {row['filename']}, Value: {row['line']}")
                    self.elements.append(row['line'])
                    element_value = None
                    if self.strategy_param == 2:
                        element_value = row['randomvalue']
                    elif self.strategy_param == 3:
                        element_value = row['inconsistencyvalue']
                    self.element_values[row['line']] = element_value

            except Error as e:
                logging.error(f"Failed to load data from MySQL database: {e}")
            finally:
                cursor.close()
                conn.close()
        else:
            logging.error("Connection to MySQL database failed")

    def get_elements(self):
        """
        Retrieve the elements of the dataset.

        Returns:
            list: The elements contained in the dataset.
        """
        return self.elements

    def get_elements_with_values(self):
        """
        Retrieve the elements of the dataset along with their assigned values.

        Returns:
            list of tuples: Each tuple contains an element and its corresponding value.
        """
        return [(element, self.element_values[element]) for element in self.elements]

    def get_values(self):
        """
        Retrieve the values assigned to the elements of the dataset.

        Returns:
            list: A list of values assigned to the elements.
        """
        return list(self.element_values.values())

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
            logging.warning(f"Element {element} not found in the dataset.")

    def clone(self):
        """
        Create a copy of the current DataSet instance.

        Returns:
            DataSet: A new DataSet instance containing the same elements.
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

    def apply_value_assignment_strategy(self, strategy_param):
        """
        Apply a value assignment strategy to each element in the dataset based on the specified parameter.

        Args:
            strategy_param (int): The parameter defining the value assignment strategy.
        """        
        if strategy_param == 1:
            for element in self.elements:
                self.element_values[element] = 1
        elif strategy_param == 2 or strategy_param == 3:
            # Values already assigned during load_elements_from_db
            for element in self.elements:
                if element not in self.element_values:
                    self.element_values[element] = None
