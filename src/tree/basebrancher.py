from abc import ABC, abstractmethod
import logging
from src.kernels.expandshrink import ExpandShrink
from src.structs.logger import setup_logging

# Set up logging for this module
setup_logging()

tree_logger = logging.getLogger(__name__)

class BaseBrancher(ABC):
    tree_logger = logging.getLogger(__name__)
    def __init__(self, kernelStrategy, dataset, tree):
        self.dataset = dataset
        self.tree = tree
        self.kernelStrategy = kernelStrategy
        self.computed_kernels = []

    @abstractmethod
    def expand_children(self, current_node):
        pass

    def calculate_child_path(self, current_node, element):
        child_path_value = current_node.path_value
        element_value = self.dataset.get_element_value(element)
        tree_logger.info(f"Edge Value: {element_value}")
        child_path_value = current_node.path_value + element_value
        tree_logger.debug(f"Child_path_value = {child_path_value}")
        return child_path_value

"""
    def calculate_bbvalue(self, current_node, dataset):
        assigned_value = dataset.get_value
        return current_node.bbvalue + assigned_value
"""

