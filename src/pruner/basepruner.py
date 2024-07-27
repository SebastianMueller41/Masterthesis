# Set up logging for this module
import logging
from src.kernels.shrinkexpand import ShrinkExpand
from src.structs.logger import setup_logging

setup_logging()

# Get the logger for this module
prune_logger = logging.getLogger(__name__)

prune_logger.info("BasePruner called.")

class BasePruner:
    def __init__(self, kernel_strategy, tree):
        self.tree = tree
        self.best_solution = None
        self.optimal_reached = False
        self.kernel_strategy = kernel_strategy
        self.remainder_flag = True # Set Flag to True to calculate remainder value of node
        self.initial_remainder_flag = False
        self.remainder = ShrinkExpand(window_size=1, divide_and_conquer=True,alpha=self.kernel_strategy.alpha)
        self.remainder_value = 0
        if self.initial_remainder_flag:
            possible_HS_value = self.tree.dataset.sum_values() - self.remainder_value
            self.tree.lowerBound = possible_HS_value
            self.tree.upperBound = possible_HS_value

    def calculate_subproblem(self, node):
        subproblem_value = node.dataset.get_elements().sum_values()
        node.sub_value = subproblem_value
        return subproblem_value
    
    def find_remainder_in_dataaset(self, dataset):
        return self.remainder.find_remainder(dataset)
    
    def calculate_potential_bound(self, node):
        if self.remainder_flag:
            remainder = self.find_remainder_in_dataaset(node.dataset)
            if remainder is not None:
                self.remainder_value = remainder.sum_values()
                subproblem_value = node.sub_value - self.remainder_value
                prune_logger.debug(f"Computed Remainder: {remainder.get_elements()}, with value {self.remainder_value}, potential subproblem value {subproblem_value} = node_dataset value {node.sub_value} - remainder value {self.remainder_value}")
            else:
                subproblem_value = node.sub_value
        else:
            subproblem_value = node.sub_value

        prune_logger.debug(f"Path value: {node.path_value} with subproblem value: {subproblem_value} and remaining dataset: {node.get_dataset().get_elements()}")
        return subproblem_value

    def should_prune(self, node):
        return False
    
    def update_boundary_with_leaf(self, leaf_node):
        prune_logger.info(f"LEAF FOUND with path value: {leaf_node.path_value} and sub_value: {leaf_node.sub_value} path: {self.tree.get_hitting_set_for_leaf(leaf_node).get_elements()}")
        if leaf_node.sub_value < self.tree.upperBound:
            prune_logger.debug(f"Update {leaf_node.sub_value > self.tree.upperBound} because subproblem: {leaf_node.sub_value } > {self.tree.upperBound} upper boundary")
            self.tree.upperBound = leaf_node.sub_value 
            prune_logger.debug(f"Updated upper boundary: {self.tree.upperBound}")
            print(f"Updated upperBound: {self.tree.upperBound}")

    def should_prune(self, node):
        prune_logger.debug(f"Prune CHECK: {node.sub_value <= self.tree.upperBound}, because {node.sub_value} <= {self.tree.upperBound}")
        if self.tree.upperBound > self.tree.dataset.sum_values():
            prune_logger.info(f"Not pruning, upperBound <= {self.tree.dataset.sum_values()}")
        prune_logger.warning(f"Pruning {node.sub_value <= self.tree.upperBound}, because Subvale {node.sub_value} <= {self.tree.upperBound} upperBound")
        pass
    """
    
        def calculate_potential_bound(self, node):
        subproblem_value = self.calculate_subproblem(node)
        prune_logger.info(f"Node path value: {node.path_value}")
        return node.path_value+subproblem_value
        """