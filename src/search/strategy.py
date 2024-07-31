"""
This module defines the abstract base class for search strategies.
"""

from abc import ABC, abstractmethod

class Strategy(ABC):
    """
    Abstract base class for search strategies.
    """

    @abstractmethod
    def find_kernels(self) -> None:
        """
        Abstract method to find kernels in a dataset.

        Returns:
            None
        """
        pass
