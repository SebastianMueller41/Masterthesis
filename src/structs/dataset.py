"""
This module defines the DataSet class, which is used to manage a collection of elements
typically representing data items or clauses in computational logic. The DataSet class
provides functionality to load data from a file, access elements, add or remove elements,
clone itself, and write its contents to a file.
"""

from src.values.values import assign_fixed_value, assign_unique_random_values, assign_inconsistency_value

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
        if input_file_path:
            self.load_elements_from_file(input_file_path)
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
            print(f"File {file_path} not found. Starting with an empty dataset.")

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


    def add_element(self, element):
        """
        Add an element to the dataset if it is not already present.

        Args:
            element (str): The element to add to the dataset.
        """
        if element not in self.elements:
            self.elements.append(element)

    def remove_element(self, element):
        """
        Remove the specified element from the dataset if it exists.

        Args:
            element (str): The element to remove from the dataset.
        """
        try:
            self.elements.remove(element)
        except ValueError:
            print(f"Element {element} not found in the dataset.")

    def clone(self):
        """
        Create a copy of the current DataSet instance.

        Returns:
            DataSet: A new DataSet instance containing the same elements.
        """
        return DataSet(elements=list(self.elements))

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
            assign_fixed_value(self, 1)
        elif strategy_param == 2:
            assign_unique_random_values(self)
        elif strategy_param == 3:
            assign_inconsistency_value(self)  # Placeholder for future implementation

