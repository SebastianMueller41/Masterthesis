from abc import ABC, abstractmethod
import logging
from sortedcontainers import SortedList
from src.structs.logger import setup_logging

# Set up logging for this module
setup_logging()

class BaseBrancher(ABC):
    tree_logger = logging.getLogger(__name__)
    def __init__(self, dataset, tree, pruner):
        self.dataset = dataset
        self.tree = tree
        self.pruner = pruner
        self.queue = SortedList(key=lambda x: (x[0], x[2]))

    @abstractmethod
    def expand_children(self, current_node, priority_queue, kernel_strategy, alpha):
        pass

    @abstractmethod
    def add_to_priority_queue(self, node):
        pass

    def calculate_bbvalue(self, current_node):
        #assigned_value = self.dataset.get_element_value(element)
        path_from_leaf = self.tree.get_hitting_set_for_leaf(current_node)
        assigned_value = path_from_leaf.sum_values() if path_from_leaf is not None else 0
        self.tree_logger.debug(f"Calculated bbvlalue: {assigned_value}")
        return assigned_value

"""
    def calculate_bbvalue(self, current_node, dataset):
        assigned_value = dataset.get_value
        return current_node.bbvalue + assigned_value
"""

