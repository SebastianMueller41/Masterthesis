from src.pruner.basepruner import BasePruner
import logging
from src.structs.logger import setup_logging

# Set up logging for this module
setup_logging()

# Get the logger for this module
prune_logger = logging.getLogger(__name__)

class LowerPruner(BasePruner):
    def __init__(self, tree):
        self.tree = tree
        self.boundary = float('inf')

    def update_boundary_with_leaf(self, leaf_node):
        prune_logger.info(f"LEAF FOUND with path value: {leaf_node.bbvalue}")
        subproblem_value = self.calculate_subproblem(leaf_node)
        if subproblem_value < self.boundary:
            prune_logger.debug(f"Update because subproblem: {subproblem_value} < {self.boundary} upper boundary")
            self.boundary = subproblem_value
            prune_logger.debug(f"Updated upper boundary: {self.boundary}")
            print(f"Updated upper boundary: {self.boundary}")

    def should_prune(self, node):
        potential_bound = self.calculate_potential_bound(node)
        return potential_bound >= self.boundary

"""
if self.strategy_param == 1:
            subproblem_value = leaf_path_value
        #leaf_path_measure = self.tree.get_hitting_set_for_leaf(leaf_node).sum_values()

if self.strategy_param == 1:
    prune_logger.info(f"Should prune? {path_value <= self.boundary} because path_value {path_value} <= {self.boundary} upper boundary")
    return path_value <= self.boundary
else:
    subproblem_value = self.tree.dataset.sum_values() - path_value
    prune_logger.info(f"Should prune? {path_value <= self.boundary} because path_value {path_value} <= {self.boundary} upper boundary")
    return path_value >= self.boundary 
"""