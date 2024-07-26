from src.pruner.basepruner import BasePruner
import logging
from src.structs.logger import setup_logging

# Set up logging for this module
setup_logging()

# Get the logger for this module
prune_logger = logging.getLogger(__name__)

prune_logger.info("Pruner called.")

class UpperPruner(BasePruner):
    def __init__(self, kernel_strategy, tree):
        super().__init__(kernel_strategy, tree)

    def update_boundary_with_leaf(self, leaf_node):
        prune_logger.warning(f"UPDATE CHECK: {leaf_node.sub_value} > {self.tree.lowerBound}")
        if leaf_node.sub_value > self.tree.lowerBound:
            prune_logger.warning(f"Lower Bound Update to: {leaf_node.sub_value}, because > {self.tree.lowerBound}")
            self.tree.lowerBound = leaf_node.sub_value

        else:
            prune_logger.debug(f"Path value {leaf_node.sub_value} >= {self.tree.lowerBound} lower boundary")

    def should_prune(self, node):
        prune_logger.debug(f"Prune CHECK: {node.sub_value <= self.tree.lowerBound}, because {node.sub_value} <= {self.tree.lowerBound}")
        if self.tree.lowerBound == 0:
            prune_logger.info(f"Not pruning, lowerBound = 0, {self.tree.lowerBound}")
            return False
        prune_logger.debug(f"Prune: {node.sub_value <= self.tree.lowerBound}, because {node.sub_value} <= {self.tree.lowerBound}")
        return node.sub_value <= self.tree.lowerBound