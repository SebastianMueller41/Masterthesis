from src.pruner.basepruner import BasePruner
import logging
from src.structs.logger import setup_logging

# Set up logging for this module
setup_logging()

# Get the logger for this module
prune_logger = logging.getLogger(__name__)

class LowerPruner(BasePruner):
    def __init__(self, tree, strategy_param):
        self.tree = tree
        self.boundary = float('inf')
        self.strategy_param = strategy_param

    # This approach is not used but maybe interesting for future work
    def calculate_bbvalue(self, element, dataset):
        assigned_value = dataset.get_element_value(element)
        transformed_value = 1 / (assigned_value) if assigned_value != 0 else 0
        return transformed_value

    def update_boundary_with_leaf(self, leaf_node):
        leaf_path_value = self.tree.calculate_path_bbvalue_up_to_root(leaf_node)
        prune_logger.info(f"LEAF FOUND with path value: {leaf_path_value}")
    
        subproblem_value = leaf_node.dataset.sum_values() - leaf_path_value

        leaf_node.sub_value = subproblem_value
        prune_logger.debug(f"Subproblem: {subproblem_value}, leaf_path_value: {leaf_path_value} upper boundary: {self.boundary}")
        if subproblem_value < self.boundary:
            prune_logger.debug(f"Update because subproblem: {subproblem_value} < {self.boundary} upper boundary")
            self.boundary = subproblem_value
            prune_logger.debug(f"Updated upper boundary: {self.boundary}")
            print(f"Updated upper boundary: {self.boundary}")

    def should_prune(self, node):
        path_value = self.tree.calculate_path_bbvalue_up_to_root(node)
        prune_logger.info(f"Node path value: {path_value}")
        subproblem_value = node.dataset.sum_values()
        node.sub_value = subproblem_value
        return path_value+subproblem_value >= self.boundary


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