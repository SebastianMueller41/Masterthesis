"""
This module sets up logging and defines the UpperPruner class, which extends the BasePruner class.
The UpperPruner class includes methods for pruning nodes in a search tree to optimize the search for solutions.
"""

import logging
from src.pruner.basepruner import BasePruner
from src.structs.logger import setup_logging

# Set up logging for this module
setup_logging()

# Get the logger for this module
prune_logger = logging.getLogger(__name__)
prune_logger.info("Pruner called.")

class UpperPruner(BasePruner):
    """
    A class for pruning nodes in a search tree using the upper bound strategy.
    """

    def __init__(self, kernel_strategy, tree):
        """
        Initialize the UpperPruner with a kernel strategy and a search tree.

        Args:
            kernel_strategy (KernelStrategy): The strategy used to find kernels.
            tree (SearchTree): The search tree to be pruned.
        """
        super().__init__(kernel_strategy, tree)

    def update_boundary_with_leaf(self, leaf_node):
        """
        Update the lower boundary of the search tree with a leaf node's value.

        Args:
            leaf_node (TreeNode): The leaf node to update the boundary with.

        Returns:
            None
        """
        prune_logger.warning(f"UPDATE CHECK: {leaf_node.sub_value} > {self.tree.lowerBound}")
        if leaf_node.sub_value > self.tree.lowerBound:
            prune_logger.warning(f"Lower Bound Update to: {leaf_node.sub_value}, because > {self.tree.lowerBound}")
            self.tree.lowerBound = leaf_node.sub_value
        else:
            prune_logger.debug(f"Path value {leaf_node.sub_value} >= {self.tree.lowerBound} lower boundary")

    def should_prune(self, node):
        """
        Determine whether a node should be pruned.

        Args:
            node (TreeNode): The node to evaluate for pruning.

        Returns:
            bool: True if the node should be pruned, False otherwise.
        """
        prune_logger.debug(f"Prune CHECK: {node.sub_value <= self.tree.lowerBound}, because {node.sub_value} <= {self.tree.lowerBound}")
        if self.tree.lowerBound == 0:
            prune_logger.info(f"Not pruning, lowerBound = 0, {self.tree.lowerBound}")
            return False
        prune_logger.debug(f"Prune: {node.sub_value <= self.tree.lowerBound}, because {node.sub_value} <= {self.tree.lowerBound}")
        return node.sub_value <= self.tree.lowerBound
