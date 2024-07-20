import heapq
from src.tree.basebrancher import BaseBrancher
from src.tree.hittingsettree import HSTreeNode
import logging
from src.structs.logger import setup_logging


# Set up logging for this module
setup_logging()

# Get the logger for this module
tree_logger = logging.getLogger(__name__)

class Brancher(BaseBrancher):
    def __init__(self, dataset):
        self.dataset = dataset

    def expand_children(self, current_node, priority_queue):
        children = []
        for element in current_node.get_kernel():
            reduced_dataset = current_node.get_dataset().clone()
            reduced_dataset.remove_element(element)

            bbvalue = self.calculate_bbvalue(current_node, element, reduced_dataset)
            child_node = HSTreeNode(kernel=None, dataset=reduced_dataset, edge=element, level=current_node.level + 1, bbvalue=bbvalue, parent=current_node)
            current_node.add_child(child_node)

            priority = self.dataset.element_values.get(element, 0)
            children.append((priority, child_node))

        children.sort(reverse=True, key=lambda x: x[0])
        for priority, child_node in children:
            self.add_to_priority_queue(priority_queue, child_node, priority)

    def add_to_priority_queue(self, queue, node, priority):
        heapq.heappush(queue, (-priority, node))

    def calculate_bbvalue(self, current_node, element, dataset):
        assigned_value = dataset.element_values.get(element, 0)
        return current_node.bbvalue + assigned_value
