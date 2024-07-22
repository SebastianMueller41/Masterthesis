from src.pruner.basepruner import BasePruner
import logging
from src.structs.logger import setup_logging

# Set up logging for this module
setup_logging()

# Get the logger for this module
prune_logger = logging.getLogger(__name__)

prune_logger.info("Pruner called.")

class UpperPruner(BasePruner):
    def __init__(self, tree, strategy_param):
        self.tree = tree
        self.best_solution = None
        self.boundary = 0
        self.strategy_param = strategy_param
        prune_logger.debug("UpperPruner initialized.")

    def calculate_potential_bound(self, node):
        # A simple heuristic: sum the values of all remaining elements in the dataset
        path_value = self.tree.get_hitting_set_for_leaf(node).sum_values()
        remaining_value = node.get_dataset().sum_values()
        potential_bound = path_value + remaining_value # Add sum value of remaining elements
        prune_logger.debug(f"Path value: {path_value} with remaining value: {remaining_value} and remainder: {node.get_dataset().get_elements()}")
        return potential_bound 

    def update_boundary_with_leaf(self, leaf_node):
        leaf_path_measure = self.tree.calculate_path_bbvalue_up_to_root(leaf_node)
        #leaf_path_measure = self.tree.get_hitting_set_for_leaf(leaf_node).sum_values()
        if leaf_path_measure > self.boundary:
            self.boundary = leaf_path_measure
            prune_logger.debug(f"Updated boundary: {self.boundary}")
            print(f"Updated boundary: {self.boundary}")

    def should_prune(self, node):
        if self.boundary == 0:
            return False
        potential_value = self.calculate_potential_bound(node)
        prune_logger.debug(f"Prune: {potential_value >= self.boundary}, because {potential_value} >= {self.boundary}")
        return potential_value >= self.boundary
