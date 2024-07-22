from src.pruner.basepruner import BasePruner
import logging
from src.structs.logger import setup_logging
from src.kernels.shrinkexpand import ShrinkExpand

# Set up logging for this module
setup_logging()

# Get the logger for this module
prune_logger = logging.getLogger(__name__)

prune_logger.info("Pruner called.")

class UpperPruner(BasePruner):
    def __init__(self, tree, strategy_param, alpha, window_size, divide_and_conquer):
        self.tree = tree
        self.best_solution = None
        self.boundary = 0
        self.strategy_param = strategy_param
        self.alpha = alpha
        prune_logger.debug("UpperPruner initialized.")
        self.shrink_expand = ShrinkExpand(window_size, divide_and_conquer)
    
    def find_remainder_in_dataaset(self, dataset, alpha):
        return self.shrink_expand.find_remainder(dataset, alpha)
    
    def calculate_potential_bound(self, node):
        remainder = self.shrink_expand.find_remainder(node.dataset, self.alpha)
        if remainder is None:
            subproblem_value = node.dataset.sum_values()
            prune_logger.debug(f"Remainder = empty. Subproblem value {subproblem_value}")
        else:
            subproblem_value = node.dataset.sum_values() - remainder.sum_values()
            prune_logger.debug(f"Computed Remainder: {node.dataset.get_elements()}, with value {remainder.sum_values()}, subproblem value {subproblem_value} = node_dataset value {node.dataset.sum_values()} - remainder value {- remainder.sum_values()}")

        path_value = self.tree.get_hitting_set_for_leaf(node).sum_values()
        potential_bound = path_value + subproblem_value # Add sum value of remaining elements
        prune_logger.debug(f"Path value: {path_value} with subproblem value: {subproblem_value} and remainder: {node.get_dataset().get_elements()}")
        return potential_bound 

    def update_boundary_with_leaf(self, leaf_node):
        leaf_path_measure = self.tree.calculate_path_bbvalue_up_to_root(leaf_node)
        if leaf_path_measure > self.boundary:
            prune_logger.debug(f"leaf_path_measure {leaf_path_measure} > {self.boundary} boundary")
            self.boundary = leaf_path_measure
            prune_logger.debug(f"Updated boundary: {self.boundary}")
            print(f"Updated boundary: {self.boundary}")
        else:
            prune_logger.debug(f"Path value {leaf_path_measure} <= {self.boundary} Boundary")

    def should_prune(self, node):
        potential_value = self.calculate_potential_bound(node)
        prune_logger.debug(f"Prune: {potential_value < self.boundary}, because {potential_value} < {self.boundary}")
        return potential_value < self.boundary
