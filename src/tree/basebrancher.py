import heapq
from abc import ABC, abstractmethod
from src.tree.hittingsettree import HSTreeNode

class BaseBrancher(ABC):
    def __init__(self, dataset, tree):
        self.dataset = dataset
        self.tree = tree

    @abstractmethod
    def expand_children(self, current_node, priority_queue, kernel_strategy, alpha):
        pass

    def add_to_priority_queue(self, queue, node, priority):
        heapq.heappush(queue, (-priority, node))

    def calculate_bbvalue(self, current_node):
        #assigned_value = self.dataset.get_element_value(element)
        path_from_leaf = self.tree.get_hitting_set_for_leaf(current_node)
        assigned_value = path_from_leaf.sum_values() if path_from_leaf is not None else 0
        self.tree_logger.debug(f"assigned_value = {assigned_value}")
        return assigned_value

"""
    def calculate_bbvalue(self, current_node, dataset):
        assigned_value = dataset.get_value
        return current_node.bbvalue + assigned_value
"""

