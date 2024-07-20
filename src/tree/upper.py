from src.tree.basepruner import BasePruner
import logging
from src.structs.logger import setup_logging


# Set up logging for this module
setup_logging()

# Get the logger for this module
tree_logger = logging.getLogger(__name__)

class UpperPruner(BasePruner):
    def __init__(self, tree, brancher):
        self.tree = tree
        self.brancher = brancher

    def calculate_bbvalue(self, current_node, element, dataset):
        assigned_value = dataset.element_values.get(element, 0)
        return current_node.bbvalue + assigned_value
    
    def calculate_potential_bound(self, node):
        # A simple heuristic: sum the values of all remaining elements in the dataset
        potential_bound = self.tree.get_hitting_set_for_leaf(node).sum_values()
        potential_bound += node.get_dataset().sum_values() # Add sum value of remaining elements
        return potential_bound 

    def update_boundary_with_leaf(self, leaf_node):
        #leaf_path_measure = self.tree.calculate_path_bbvalue_up_to_root(leaf_node)
        leaf_path_measure = self.tree.get_hitting_set_for_leaf(leaf_node).sum_values()
        if leaf_path_measure > self.pruner.boundary:
            self.pruner.boundary = leaf_path_measure
            tree_logger.DEBUG(f"Updated boundary: {self.pruner.boundary}")
            print(f"Updated boundary: {self.pruner.boundary}")

    def should_prune(self, node):
        if self.pruner.boundary == 0:
            return False
        return self.calculate_potential_bound(node) <= self.pruner.boundary