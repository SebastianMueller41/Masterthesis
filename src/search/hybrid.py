"""
This module sets up logging and defines the HYS class, which extends the Search class.
The HYS class implements a hybrid search strategy that starts with Depth-First Search (DFS)
and switches to Breadth-First Search (BFS) after the first leaf is found.
"""

import logging
from src.search.dfs import DFS
from src.search.bfs import BFS
from src.search.search import Search
from src.structs.logger import setup_logging

# Set up logging for this module
setup_logging()

# Get the logger for this module
ss_logger = logging.getLogger(__name__)

class HYS(Search):
    """
    A class for performing a hybrid search strategy that starts with Depth-First Search (DFS)
    and switches to Breadth-First Search (BFS) after the first leaf is found.
    """

    def __init__(self, kernelStrategy, dataset, pruner):
        """
        Initialize the HYS with a kernel strategy, dataset, and pruner.

        Args:
            kernelStrategy (KernelStrategy): The strategy used to find kernels.
            dataset (DataSet): The dataset to search.
            pruner (Pruner): The pruner used to prune nodes in the search tree.
        """
        super().__init__(kernelStrategy, dataset, pruner)
        self.dfs_search = DFS(kernelStrategy, dataset, pruner)
        self.search = self.dfs_search
        self.kernelStrategy = self.kernelStrategy
        self.first_leaf_found = False
        self.pruner = self.search.pruner

    def find_kernels(self) -> None:
        """
        Find kernels in the dataset using a hybrid search strategy.

        Returns:
            None
        """
        if self.first_leaf_found:
            ss_logger.info("First LEAF found, switching to BFS")
            self.search.find_kernels()
        else:
            self.search.find_kernels()
        
        if self.search.tree.leaf_nodes:
            self.first_leaf_found = True
            bfs = BFS(self.search.kernelStrategy, self.search.dataset, self.search.pruner)
            self.tree = self.search.tree
            self.search = bfs
