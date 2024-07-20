# src/tree/base_expander.py

from abc import ABC, abstractmethod
from src.tree.hittingsettree import HSTreeNode
import heapq

class BaseExpander(ABC):
    def __init__(self, dataset):
        self.dataset = dataset

    @abstractmethod
    def expand_children(self, current_node, priority_queue, kernel_strategy, alpha):
        pass

    def add_to_priority_queue(self, queue, node, priority):
        heapq.heappush(queue, (-priority, node))

    def calculate_bbvalue(self, current_node, element, dataset):
        assigned_value = dataset.element_values.get(element, 0)
        return current_node.bbvalue + assigned_value
