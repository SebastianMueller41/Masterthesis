# Set up logging for this module
import logging
from src.structs.logger import setup_logging

setup_logging()

# Get the logger for this module
prune_logger = logging.getLogger(__name__)

prune_logger.info("BasePruner called.")

class BasePruner:
    def __init__(self, tree, strategy_param):
        self.tree = tree
        self.best_solution = None
        self.boundary = 0

    def calculate_potential_bound(self, node):
        return float('inf')

    def update_boundary_with_leaf(self, leaf_node):
        pass

    def should_prune(self, node):
        return False
