"""
This module sets up logging and defines the BaseBrancher abstract base class.
The BaseBrancher class is used to expand child nodes in a tree structure during a search process.
"""

from abc import ABC, abstractmethod
import logging
from src.kernels.expandshrink import ExpandShrink
from src.structs.logger import setup_logging

# Set up logging for this module
setup_logging()

tree_logger = logging.getLogger(__name__)

class BaseBrancher(ABC):
    """
    Abstract base class for branching in a tree structure during a search process.

    Attributes:
        dataset (DataSet): The dataset used in the search.
        tree (HittingSetTree): The tree structure used in the search.
        kernelStrategy (KernelStrategy): The strategy used to find kernels.
        computed_kernels (list): A list to store computed kernels.
    """

    def __init__(self, kernelStrategy, dataset, tree):
        """
        Initialize the BaseBrancher with a kernel strategy, dataset, and tree.

        Args:
            kernelStrategy (KernelStrategy): The strategy used to find kernels.
            dataset (DataSet): The dataset used in the search.
            tree (HittingSetTree): The tree structure used in the search.
        """
        self.dataset = dataset
        self.tree = tree
        self.kernelStrategy = kernelStrategy
        self.computed_kernels = []

    @abstractmethod
    def expand_children(self, current_node):
        """
        Abstract method to expand child nodes from the current node.

        Args:
            current_node (HSTreeNode): The current node to expand.

        Returns:
            list: A list of child nodes.
        """
        pass

    def calculate_child_path(self, current_node, element):
        """
        Calculate the path value for a child node.

        Args:
            current_node (HSTreeNode): The current node from which the child node is expanded.
            element (str): The element used to expand the child node.

        Returns:
            int: The calculated path value for the child node.
        """
        child_path_value = current_node.path_value
        element_value = self.dataset.get_element_value(element)
        tree_logger.info(f"Edge Value: {element_value}")
        child_path_value += element_value
        tree_logger.debug(f"Child_path_value = {child_path_value}")
        return child_path_value
