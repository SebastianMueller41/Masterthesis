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

    def calculate_bbvalue(self, current_node, dataset):
        assigned_value = dataset.get_value
        return current_node.bbvalue + assigned_value
