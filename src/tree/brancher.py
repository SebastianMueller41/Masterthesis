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

    def expand_children(self, current_node):
        if current_node.get_kernel() is None or current_node.get_kernel() == "LEAF":
            return []

        children = []
        for element in current_node.get_kernel():
            self.computed_kernels.append(current_node)
            tree_logger.warning(f"Adding: {element} with parent_sub_value: {current_node.get_dataset().sum_values()}")
            reduced_dataset = current_node.get_dataset().clone()
            reduced_dataset.remove_element(element)
            child_path_value = self.calculate_child_path(current_node, element)
            sub_value = reduced_dataset.sum_values()
            tree_logger.info(f"Calculated child_path_value = {child_path_value}")
            child_node = HSTreeNode(kernel=None, dataset=reduced_dataset, edge=element, level=current_node.level + 1, path_value=child_path_value, sub_value=sub_value, parent=current_node)
            tree_logger.debug(f"Child Node created with: path value {child_path_value}, sub_value {sub_value}")
            current_node.add_child(child_node)
            children.append(child_node)
            tree_logger.debug(f"Child node {element} added to the list of children")
        return children