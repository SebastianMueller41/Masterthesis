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
    def __init__(self, kernel_strategy, tree):
        super().__init__(kernel_strategy, tree)
        self.boundary = 0
    
    def update_boundary_with_leaf(self, leaf_node):
        leaf_path_measure = self.tree.calculate_path_bbvalue_up_to_root(leaf_node)
        if leaf_path_measure > self.boundary:
            prune_logger.debug(f"leaf_path_measure {leaf_path_measure} > {self.boundary} lower boundary")
            self.boundary = leaf_path_measure
            prune_logger.debug(f"Updated lower boundary: {self.boundary}")
            print(f"Updated lower boundary: {self.boundary}")
        else:
            prune_logger.debug(f"Path value {leaf_path_measure} <= {self.boundary} lower boundary")

    def should_prune(self, node):
        potential_value = self.calculate_potential_bound(node)
        prune_logger.debug(f"Prune: {potential_value < self.boundary}, because {potential_value} < {self.boundary}")
        return potential_value < self.boundary