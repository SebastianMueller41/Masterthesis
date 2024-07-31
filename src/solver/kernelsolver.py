"""
This module defines the KernelSolver class, which utilizes a search strategy to find kernels in a dataset.
"""

from src.search.strategy import Strategy

class KernelSolver:
    """
    A class to solve the kernel finding problem using a specified search strategy.
    """

    def __init__(self, strategy: Strategy):
        """
        Initialize the KernelSolver with a search strategy.

        Args:
            strategy (Strategy): The search strategy to use for finding kernels.
        """
        self.strategy = strategy

    def solve(self) -> None:
        """
        Execute the search strategy to find kernels and return the resulting search tree.

        Returns:
            HittingSetTree: The search tree containing the found kernels.
        """
        self.strategy.find_kernels()
        return self.strategy.tree
