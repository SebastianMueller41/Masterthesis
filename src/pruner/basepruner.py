# Set up logging for this module
import logging
from src.structs.logger import setup_logging

setup_logging()

# Get the logger for this module
prune_logger = logging.getLogger(__name__)

prune_logger.info("BasePruner called.")

class BasePruner:
    def __init__(self, kernel_strategy, tree, alpha):
        self.tree = tree
        self.best_solution = None
        self.optimal_reached = False
        self.lower_bound = 0
        self.upper_bound = float('inf')
        self.alpha = alpha
        self.kernel_strategy = kernel_strategy
        self.remainder_flag = False # Set Flag to True to calculate remainder value of node

    def calculate_subproblem(self, node):
        subproblem_value = node.dataset.sum_values()
        node.sub_value = subproblem_value
        return subproblem_value
    
    def find_remainder_in_dataaset(self, dataset):
        return self.kernel_strategy.find_remainder(dataset)
    
    def calculate_potential_bound(self, node):
        if self.remainder_flag:
            remainder = self.shrink_expand.find_remainder(node.dataset, self.alpha)
            if remainder is not None:
                subproblem_value = node.dataset.sum_values() - remainder.sum_values()
                prune_logger.debug(f"Computed Remainder: {node.dataset.get_elements()}, with value {remainder.sum_values()}, subproblem value {subproblem_value} = node_dataset value {node.dataset.sum_values()} - remainder value {- remainder.sum_values()}")
        else:
            subproblem_value = self.calculate_subproblem(node)
            prune_logger.debug(f"Calculating subproblem from node dataset: subproblem value {subproblem_value}")

        node.sub_value = subproblem_value
        path_value = self.tree.get_hitting_set_for_leaf(node).sum_values()
        potential_bound = path_value + subproblem_value # Add sum value of remaining elements
        prune_logger.debug(f"Path value: {path_value} with subproblem value: {subproblem_value} and remaining dataset: {node.get_dataset().get_elements()}")
        return potential_bound 

    def should_prune(self, node):
        return False
    
    def update_boundary_with_leaf(self, leaf_node):
        pass


    """
    
        def calculate_potential_bound(self, node):
        subproblem_value = self.calculate_subproblem(node)
        prune_logger.info(f"Node path value: {node.bbvalue}")
        return node.bbvalue+subproblem_value
        """