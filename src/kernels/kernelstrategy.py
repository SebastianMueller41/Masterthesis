"""
This module defines the abstract base class for kernel finding strategies.
"""

from abc import ABC, abstractmethod

class KernelStrategy(ABC):
    """
    Abstract base class for kernel finding strategies.
    """
    
    @abstractmethod
    def find_kernel(self, dataset):
        """
        Abstract method to find the kernel of a dataset.

        Args:
            dataset (DataSet): The dataset to find the kernel in.

        Returns:
            DataSet: The resulting kernel if found, else None.
        """
        pass
