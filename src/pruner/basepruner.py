# Set up logging for this module
import logging
from src.structs.logger import setup_logging

setup_logging()

# Get the logger for this module
prune_logger = logging.getLogger(__name__)

prune_logger.info("BasePruner called.")

class BasePruner:
    def __init__(self, tree):
        self.tree = tree
        self.best_solution = None
        self.boundary = None

    def calculate_subproblem(self, node):
        subproblem_value = node.dataset.sum_values()
        node.sub_value = subproblem_value
        return subproblem_value

    def calculate_potential_bound(self, node):
        subproblem_value = self.calculate_subproblem(node)
        prune_logger.info(f"Node path value: {node.bbvalue}")
        return node.bbvalue+subproblem_value

    def should_prune(self, node):
        return False
    
    def update_boundary_with_leaf(self, leaf_node):
        pass
    
    # This approach is not used but maybe interesting for future work
    def calculate_bbvalue(self, element, dataset):
        assigned_value = dataset.get_element_value(element)
        transformed_value = 1 / (assigned_value) if assigned_value != 0 else 0
        return transformed_value