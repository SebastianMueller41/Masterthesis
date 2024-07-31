"""
This module sets up logging and defines the BestPruner class, which extends the BasePruner class.
The BestPruner class includes methods for pruning nodes in a search tree to optimize the search for solutions.
"""

import logging
from itertools import combinations
from src.kernels.shrinkexpand import ShrinkExpand
from src.pruner.basepruner import BasePruner
from src.structs.logger import setup_logging

# Set up logging for this module
setup_logging()

# Get the logger for this module
prune_logger = logging.getLogger(__name__)
prune_logger.info("Pruner called.")

class BestPruner(BasePruner):
    """
    A class for pruning nodes in a search tree using the best approach strategy.
    """

    def __init__(self, kernel_strategy, tree):
        """
        Initialize the BestPruner with a kernel strategy and a search tree.

        Args:
            kernel_strategy (KernelStrategy): The strategy used to find kernels.
            tree (SearchTree): The search tree to be pruned.
        """
        super().__init__(kernel_strategy, tree)
        self.card_check = self.has_potential_duplicate_sums()  # Initial check if dataset qualifies for this approach
        prune_logger.info(f"Cardinality check set to: {self.card_check}, because {self.tree.dataset.sum_values()} <= {len(self.tree.dataset.get_elements())}")
        self.max_reached = False  # Initialize max_reached
        if not self.card_check:
            return None  # If dataset does not qualify for approach, don’t execute

    def update_boundary_with_leaf(self, leaf_node):
        """
        Update the upper and lower boundaries of the search tree with a leaf node's value.

        Args:
            leaf_node (TreeNode): The leaf node to update the boundary with.

        Returns:
            None
        """
        prune_logger.info(f"Leaf path measure: {leaf_node.path_value}, Dataset sum: {self.dataset_max}")
        if not self.max_reached:
            if leaf_node.path_value == self.dataset_max:
                self.max_reached = True
                self.tree.lowerBound = leaf_node.path_value
                self.tree.upperBound = len(self.tree.get_hitting_set_for_leaf(leaf_node).get_elements())
            elif leaf_node.path_value > self.tree.lowerBound:
                self.tree.lowerBound = leaf_node.path_value
        else:
            upperBoundCard = len(self.tree.get_hitting_set_for_leaf(leaf_node).get_elements())
            prune_logger.debug(f"Highest value reached: {leaf_node.path_value}, checking for lower cardinality lower than {upperBoundCard}")
            if upperBoundCard < self.tree.upperBound:
                self.tree.upperBound = upperBoundCard
                prune_logger.debug(f"Lower found, updating upperBound to {upperBoundCard}")

    def should_prune(self, node):
        """
        Determine whether a node should be pruned.

        Args:
            node (TreeNode): The node to evaluate for pruning.

        Returns:
            bool: True if the node should be pruned, False otherwise.
        """
        prune_logger.debug(f"Node path_value: {node.path_value}, Current lowerBound: {self.tree.lowerBound}, Max reached: {self.max_reached}")
        
        if self.tree.lowerBound == 0:
            prune_logger.debug("Boundary is zero, not pruning.")
            return False
        
        if self.max_reached:
            prune_logger.debug("Max not reached, not pruning.")
            if self.card_check:  # Maybe unnecessary -> see initial check
                hs_cardinality = len(self.tree.get_hitting_set_for_leaf(node).get_elements())
                prune_logger.warning(f"Hitting set cardinality: {hs_cardinality}, Best leaf cardinality: {self.tree.upperBound}")
                return hs_cardinality >= self.tree.upperBound
        else:
            prune_logger.debug(f"Prune? {node.path_value < self.tree.lowerBound}, because path value {node.path_value} < lowerBound: {self.tree.lowerBound}, Max reached: {self.max_reached}")
            return False

    def has_potential_duplicate_sums(self):
        """
        Check if sum values of the dataset qualify for the best approach.
        True if two subsets of the list with the same score and different cardinalities are possible.

        Returns:
            bool: True if the dataset has potential duplicate sums with different cardinalities, False otherwise.
        """
        elements_with_values = self.tree.dataset.get_elements_with_values()
        n = len(elements_with_values)
        sum_cardinality_map = {}

        # Iterate over all possible subsets
        for r in range(1, n + 1):  # Start from 1 to n, excluding empty subset
            for subset in combinations(elements_with_values, r):
                subset_sum = sum(value for _, value in subset)
                cardinality = len(subset)

                # Check if there is already a subset with the same sum but different cardinality
                if subset_sum in sum_cardinality_map:
                    if sum_cardinality_map[subset_sum] != cardinality:
                        return True
                else:
                    sum_cardinality_map[subset_sum] = cardinality

        return False
