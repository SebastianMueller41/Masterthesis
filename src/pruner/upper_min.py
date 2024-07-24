from src.pruner.basepruner import BasePruner
import logging
from src.structs.logger import setup_logging

# Set up logging for this module
setup_logging()

# Get the logger for this module
prune_logger = logging.getLogger(__name__)

prune_logger.info("Pruner called.")

class UpperPruner(BasePruner):
    def __init__(self, kernel_strategy, tree, alpha):
        super().__init__(kernel_strategy, tree, alpha)
        self.lower_bound = float('-inf')  # Initialize with a very low value

    def update_boundary_with_leaf(self, leaf_node):
        leaf_path_measure = self.tree.calculate_path_bbvalue_up_to_root(leaf_node)
        if leaf_path_measure > self.lower_bound:
            prune_logger.debug(f"leaf_path_measure {leaf_path_measure} > {self.lower_bound} lower boundary")
            self.lower_bound = leaf_path_measure
            prune_logger.debug(f"Updated lower boundary: {self.lower_bound}")
            print(f"Updated lower boundary: {self.lower_bound}")
        else:
            prune_logger.debug(f"Path value {leaf_path_measure} <= {self.lower_bound} lower boundary")

    def calculate_potential_bound(self, node):
        # This method should be implemented to calculate the potential bound of the node
        # For now, let's assume it returns some computed value
        return node.bbvalue  # Placeholder implementation

    def should_prune(self, node):
        potential_value = self.calculate_potential_bound(node)
        prune_logger.debug(f"Node BBValue: {node.bbvalue}")
        prune_logger.debug(f"Prune: {potential_value < self.lower_bound}, because {potential_value} < {self.lower_bound}")
        return potential_value < self.lower_bound
