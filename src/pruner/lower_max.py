from src.pruner.basepruner import BasePruner
import logging
from src.structs.logger import setup_logging

# Set up logging for this module
setup_logging()

# Get the logger for this module
prune_logger = logging.getLogger(__name__)
prune_logger.info("Pruner called.")

class LowerPruner(BasePruner):
    def __init__(self, kernel_strategy, tree):
        super().__init__(kernel_strategy, tree)

    def update_boundary_with_leaf(self, leaf_node):
        prune_logger.info(f"LEAF FOUND with path value: {leaf_node.path_value} and sub_value: {leaf_node.sub_value} path: {self.tree.get_hitting_set_for_leaf(leaf_node).get_elements()}")
        if leaf_node.sub_value < self.tree.upperBound:
            prune_logger.debug(f"Update {leaf_node.sub_value < self.tree.upperBound} because subproblem: {leaf_node.sub_value } < {self.tree.upperBound} upper boundary")
            self.tree.upperBound = leaf_node.sub_value 
            prune_logger.debug(f"Updated upper boundary: {self.tree.upperBound}")
            print(f"Updated upperBound: {self.tree.upperBound}")

    def should_prune(self, node):
        if self.tree.upperBound > self.tree.dataset.sum_values():
            prune_logger.info(f"Not pruning, because leafs: {self.tree.leaf_nodes}")
            return False
        prune_logger.warning(f"Pruning {node.sub_value >= self.tree.upperBound}, because Subvale {node.sub_value} >= {self.tree.upperBound} upperBound")
        prune_logger.warning(f"Node path value: {node.path_value}")
        return node.sub_value <= self.tree.upperBound