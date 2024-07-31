"""
This module sets up logging and defines the BFS class, which extends the Search class.
The BFS class implements the Breadth-First Search algorithm for finding kernels in a dataset.
"""

from collections import deque
from src.search.search import Search
from src.tree.hittingsettree import HSTreeNode
import logging
from src.structs.logger import setup_logging

# Set up logging for this module
setup_logging()

# Get the logger for this module
ss_logger = logging.getLogger(__name__)

class BFS(Search):
    """
    A class for performing Breadth-First Search (BFS) to find kernels in a dataset.
    """

    def __init__(self, kernelStrategy, dataset, pruner):
        """
        Initialize the BFS with a kernel strategy, dataset, and pruner.

        Args:
            kernelStrategy (KernelStrategy): The strategy used to find kernels.
            dataset (DataSet): The dataset to search.
            pruner (Pruner): The pruner used to prune nodes in the search tree.
        """
        super().__init__(kernelStrategy, dataset, pruner)
        ss_logger.debug("Initialized BFS")
        self.queue = deque()

    def find_kernels(self) -> None:
        """
        Find kernels in the dataset using BFS and populate the search tree.

        Returns:
            None
        """
        ss_logger.debug("FINDING KERNEL")
        initial_node = self.create_initial_node(self.dataset)
        if initial_node is not None:
            self.queue.append(initial_node)
            self.bfs()
        self.tree.print_tree()
        self.log_tree()

    def create_initial_node(self, dataset):
        """
        Create the initial node for the BFS search tree.

        Args:
            dataset (DataSet): The dataset to create the initial node from.

        Returns:
            HSTreeNode: The initial node of the search tree.
        """
        result = self.kernelStrategy.find_kernel(dataset)
        if result is None:
            ss_logger.info("Initial kernel is None, no need to span the tree.")
            return None
        sub_value = dataset.sum_values()
        initial_node = HSTreeNode(kernel=result.get_elements(), dataset=dataset, path_value=0, parent=None, sub_value=sub_value)
        self.tree.root = initial_node
        return initial_node

    def bfs(self):
        """
        Perform the Breadth-First Search (BFS) to explore the search tree and find kernels.

        Returns:
            None
        """
        while self.queue:
            parent = self.queue.popleft()
            if self.pruner.should_prune(parent):
                parent.kernel = "PRUNED"
                parent.set_pruned()
                continue

            if parent.get_kernel() is None:
                parent.set_kernel("LEAF")
                self.tree.add_leaf_node(parent)
                self.leaf_nodes.append(parent)
                self.pruner.update_boundary_with_leaf(parent)
            else:
                child_nodes = self.brancher.expand_children(parent)
                ss_logger.info(f"Child nodes from brancher: {child_nodes}")
                for child_node in child_nodes:
                    if child_node.get_kernel() is None:
                        result = self.kernelStrategy.find_kernel(child_node.get_dataset())
                        if result is not None:
                            child_node.set_kernel(result.get_elements())
                    self.queue.append(child_node)
        
            self.log_tree()
