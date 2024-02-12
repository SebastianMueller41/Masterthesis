"""
This module defines the DataSet class, which is used to manage a collection of elements
typically representing data items or clauses in computational logic. The DataSet class
provides functionality to load data from a file, access elements, add or remove elements,
clone itself, and write its contents to a file.
"""

class DataSet:
    """
    A class to manage a collection of elements.

    Provides methods to manipulate and persist the dataset.

    Attributes:
        elements (list): A list of elements representing the dataset.
    """
    
    def __init__(self, input_file_path=None, elements=None):
        """
        Initialize a new DataSet instance, optionally loading elements from a file.

        Args:
            input_file_path (str, optional): The path to a file from which to load elements.
            elements (list, optional): An initial list of elements to populate the dataset.
        """
        self.elements = elements if elements is not None else []
        if input_file_path:
            self.load_elements_from_file(input_file_path)

    def load_elements_from_file(self, file_path):
        """
        Load elements from the specified file path into the dataset.

        Each line in the file is treated as a separate element.

        Args:
            file_path (str): The path to the file from which to load elements.
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
