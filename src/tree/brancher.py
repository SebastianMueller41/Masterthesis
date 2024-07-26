import logging

from sortedcontainers import SortedList
from src.structs.logger import setup_logging
from src.tree.basebrancher import BaseBrancher
from src.tree.hittingsettree import HSTreeNode

# Set up logging for this module
setup_logging()

tree_logger = logging.getLogger(__name__)

class Brancher(BaseBrancher):
    def __init__(self, kernelStrategy, dataset, tree):
        super().__init__(kernelStrategy, dataset, tree)

    def initialize_queue(self, pruner):
        if pruner == 'UPPER':
            tree_logger.warning(f"Upper Pruner, Initializing SortedList with sub_value DESC and cardinality DESC")
            self.queue = SortedList(key=lambda x: (-x[0], x[2]))  # Sort desc by sub_value and asc by cardinality
        elif pruner == 'LOWER':
            tree_logger.warning(f"LOWER PRUNER, QUEUE ASC!")
            self.queue = SortedList(key=lambda x: (x[0], -x[2]))  # Sort asc by sub_value and asc by cardinality
        else:
            self.queue = SortedList()

    def expand_children(self, current_node):
        for element in current_node.get_kernel():
            self.computed_kernels.append(current_node)
            reduced_dataset = current_node.get_dataset().clone()
            reduced_dataset.remove_element(element)
            child_path_value = self.calculate_child_path(current_node, element)
            sub_value = reduced_dataset.sum_values()
            self.tree_logger.info(f"Calculated child_path_value = {child_path_value}")
            child_node = HSTreeNode(kernel=None, dataset=reduced_dataset, edge=element, level=current_node.level + 1, path_value=child_path_value, sub_value=sub_value, parent=current_node)
            tree_logger.debug(f"Child Node created with: path value {child_path_value}, sub_value {sub_value}")
            current_node.add_child(child_node)
            self.add_to_priority_queue(child_node)
            self.tree_logger.debug(f"Adding node element {element} to queue with value: {sub_value}")

    def add_to_priority_queue(self, node):
        cardinality = len(self.tree.get_hitting_set_for_leaf(node).get_elements())
        self.queue.add((node.sub_value, node, cardinality))
        tree_logger.debug(f"Priority Queue: {self.queue}")