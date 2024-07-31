"""
This module sets up logging and defines the LowerPruner class, which extends the BasePruner class.
The LowerPruner class includes methods for pruning nodes in a search tree to optimize the search for solutions.
"""

import logging
from src.pruner.basepruner import BasePruner
from src.structs.logger import setup_logging

# Set up logging for this module
setup_logging()

# Get the logger for this module
prune_logger = logging.getLogger(__name__)
prune_logger.info("Pruner called.")

class LowerPruner(BasePruner):
    """
    A class for pruning nodes in a search tree using the lower bound strategy.
    """

    def __init__(self, kernel_strategy, tree):
        """
        Initialize the LowerPruner with a kernel strategy and a search tree.

        Args:
            kernel_strategy (KernelStrategy): The strategy used to find kernels.
            tree (SearchTree): The search tree to be pruned.
        """
        super().__init__(kernel_strategy, tree)

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
            prune_logger.debug(f"Update {leaf_node.sub_value < self.tree.upperBound} because subproblem: {leaf_node.sub_value} < {self.tree.upperBound} upper boundary")
            self.tree.upperBound = leaf_node.sub_value 
            prune_logger.debug(f"Updated upper boundary: {self.tree.upperBound}")
            print(f"Updated upperBound: {self.tree.upperBound}")

    def should_prune(self, node):
        """
        Determine whether a node should be pruned.

        Args:
            node (TreeNode): The node to evaluate for pruning.

        Returns:
            bool: True if the node should be pruned, False otherwise.
        """
        if self.remainder_flag:
            prune_logger.debug(f"Remainder_value = {self.remainder_value}")
        if not self.tree.leaf_nodes:
            prune_logger.info(f"Not pruning, because no leafs: {self.tree.leaf_nodes}")
            return False
        
        calculated_sub_value = self.calculate_potential_bound(node)
        if self.initial_remainder_flag:
            self.tree.upperBound = self.remainder_value
        prune_logger.warning(f"Pruning {calculated_sub_value <= self.tree.upperBound}, because sub value {calculated_sub_value} <= {self.tree.upperBound} upperBound")
        return calculated_sub_value <= self.tree.upperBound
