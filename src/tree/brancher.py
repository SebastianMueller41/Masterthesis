import heapq
import logging
from src.pruner.lower_max import LowerPruner
from src.pruner.upper_min import UpperPruner
from src.structs.logger import setup_logging
from src.tree.basebrancher import BaseBrancher
from src.tree.hittingsettree import HSTreeNode

# Set up logging for this module
setup_logging()

tree_logger = logging.getLogger(__name__)

class Brancher(BaseBrancher):
    def __init__(self, dataset, tree, pruner):
        super().__init__(dataset, tree, pruner)
        self.tree_logger.debug("TEST")

    def expand_children(self, current_node):
        for element in current_node.get_kernel():
            reduced_dataset = current_node.get_dataset().clone()
            reduced_dataset.remove_element(element)
            bbvalue = self.tree.calculate_path_bbvalue_up_to_root(current_node)
            sub_value = reduced_dataset.sum_values()
            self.tree_logger.info(f"Calculated bbvalue = {bbvalue}")
            child_node = HSTreeNode(kernel=None, dataset=reduced_dataset, edge=element, level=current_node.level + 1, bbvalue=bbvalue, sub_value=sub_value, parent=current_node)
            current_node.add_child(child_node)
            self.add_to_priority_queue(child_node)
            self.tree_logger.debug(f"Adding node element {element} to queue with value: {bbvalue}")            

    def add_to_priority_queue(self, node):
        self.queue.add((node.bbvalue, node, node.sub_value))

    def pop_min_element(self):
        if self.queue:
            element = self.queue.pop(0)  # Remove and return the smallest element
            self.tree_logger.debug(f"Popped min element {element[1].edge} from queue: {element}")
            return element
        return None

    def pop_max_element(self):
        if self.queue:
            element = self.queue.pop(-1)  # Remove and return the largest element
            self.tree_logger.debug(f"Popped max element {element[1].edge} from queue: {element}")
            return element
        return None

    def pop_element(self, pruner):
        if isinstance(pruner, UpperPruner):
            return self.pop_min_element()
        elif isinstance(pruner, LowerPruner):
            return self.pop_max_element()
        else:
            if pruner.optimal_reached:
                return self.pop_min_element()
            else:
                return self.pop_max_element()
