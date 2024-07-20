from src.pruner.basepruner import BasePruner
import logging
from src.structs.logger import setup_logging

# Set up logging for this module
setup_logging()

# Get the logger for this module
prune_logger = logging.getLogger(__name__)

class UpperPruner(BasePruner):
    def __init__(self, tree):
        self.tree = tree
        self.best_solution = None
        self.boundary = 0

    def calculate_potential_bound(self, node):
        # A simple heuristic: sum the values of all remaining elements in the dataset
        potential_bound = self.tree.get_hitting_set_for_leaf(node).sum_values()
        potential_bound += node.get_dataset().sum_values() # Add sum value of remaining elements
        return potential_bound 

    def update_boundary_with_leaf(self, leaf_node):
        #leaf_path_measure = self.tree.calculate_path_bbvalue_up_to_root(leaf_node)
        leaf_path_measure = self.tree.get_hitting_set_for_leaf(leaf_node).sum_values()
        if leaf_path_measure > self.boundary:
            self.boundary = leaf_path_measure
            print(f"Updated boundary: {self.boundary}")

    def should_prune(self, node):
        if self.boundary == 0:
            return False
        return self.calculate_potential_bound(node) <= self.boundary
