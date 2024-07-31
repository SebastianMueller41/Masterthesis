"""
This module sets up logging and defines the BasePruner class for pruning in search trees.
"""

import logging
from src.kernels.shrinkexpand import ShrinkExpand
from src.structs import dataset
from src.structs.logger import setup_logging

# Set up logging for this module
setup_logging()

# Get the logger for this module
prune_logger = logging.getLogger(__name__)
prune_logger.info("BasePruner called.")

class BasePruner:
    """
    A class for pruning nodes in a search tree to optimize the search for solutions.
    """

    def __init__(self, kernel_strategy, tree):
        """
        Initialize the BasePruner with a kernel strategy and a search tree.

        Args:
            kernel_strategy (KernelStrategy): The strategy used to find kernels.
            tree (SearchTree): The search tree to be pruned.
        """
        self.tree = tree
        self.best_solution = None
        self.optimal_reached = False
        self.kernel_strategy = kernel_strategy
        self.remainder_flag = False  # Set flag to True to calculate remainder value of node
        self.initial_remainder_flag = False
        self.remainder = ShrinkExpand(window_size=1, divide_and_conquer=True, alpha=self.kernel_strategy.alpha)
        self.remainder_value = float('inf')
        self.dataset_max = self.tree.dataset.sum_values()

    def calculate_subproblem(self, node):
        """
        Calculate the value of the subproblem for a given node.

        Args:
            node (TreeNode): The node to calculate the subproblem value for.

        Returns:
            float: The value of the subproblem.
        """
        subproblem_value = node.dataset.get_elements().sum_values()
        node.sub_value = subproblem_value
        return subproblem_value
    
    def find_remainder_in_dataset(self, dataset):
        """
        Find the remainder of a dataset using the kernel strategy.

        Args:
            dataset (DataSet): The dataset to find the remainder in.

        Returns:
            DataSet: The remainder dataset.
        """
        return self.remainder.find_remainder(dataset)
    
    def calculate_potential_bound(self, node):
        """
        Calculate the potential bound of a node in the search tree.

        Args:
            node (TreeNode): The node to calculate the potential bound for.

        Returns:
            float: The potential bound value.
        """
        if self.remainder_flag:
            remainder = self.find_remainder_in_dataset(node.dataset)
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
        """
        Determine whether a node should be pruned.

        Args:
            node (TreeNode): The node to evaluate for pruning.

        Returns:
            bool: True if the node should be pruned, False otherwise.
        """
        return False
    
    def update_boundary_with_leaf(self, leaf_node):
        """
        Update the upper boundary of the search tree with a leaf node's value.

        Args:
            leaf_node (TreeNode): The leaf node to update the boundary with.

        Returns:
            None
        """
        prune_logger.info(f"LEAF FOUND with path value: {leaf_node.path_value} and sub_value: {leaf_node.sub_value} path: {self.tree.get_hitting_set_for_leaf(leaf_node).get_elements()}")
        if leaf_node.sub_value < self.tree.upperBound:
            prune_logger.debug(f"Update {leaf_node.sub_value > self.tree.upperBound} because subproblem: {leaf_node.sub_value} > {self.tree.upperBound} upper boundary")
            self.tree.upperBound = leaf_node.sub_value 
            prune_logger.debug(f"Updated upper boundary: {self.tree.upperBound}")
            print(f"Updated upperBound: {self.tree.upperBound}")
