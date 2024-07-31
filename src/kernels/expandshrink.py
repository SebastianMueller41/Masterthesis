"""
This module defines the ExpandShrink strategy for finding kernels within a dataset
using various expansion and shrinking techniques. Logging is set up for debugging purposes.
"""

import logging
from .kernelstrategy import KernelStrategy
from src.kernels.kernel_utils import expand, expand_divide_and_conquer, shrink, shrink_divide_and_conquer, shrink_sliding_window, cn
from src.structs.logger import setup_logging

# Set up logging for this module
setup_logging()

# Get the logger for this module
kr_logger = logging.getLogger(__name__)

class ExpandShrink(KernelStrategy):
    """
    A strategy class for expanding and shrinking datasets to find kernels.
    """

    def __init__(self, sw_expand=1, sw_shrink=1, div_conq_shrink=False, div_conq_expand=False, alpha=None):
        """
        Initialize the ExpandShrink strategy.

        Args:
            sw_expand (int): Window size for the expand phase. Default is 1.
            sw_shrink (int): Window size for the shrink phase. Default is 1.
            div_conq_shrink (bool): Flag to use divide-and-conquer in the shrink phase. Default is False.
            div_conq_expand (bool): Flag to use divide-and-conquer in the expand phase. Default is False.
            alpha (str, optional): The element to find the kernel for. Default is None.
        """
        self.div_conq_shrink = div_conq_shrink
        self.div_conq_expand = div_conq_expand
        self.sw_expand = sw_expand
        self.sw_shrink = sw_shrink
        self.alpha = alpha
        self.computed_kernels = []
        self.counter = 0

    def find_kernel(self, dataset):
        """
        Find the kernel of the dataset with respect to alpha.

        Args:
            dataset (DataSet): The dataset to find the kernel in.
        
        Returns:
            DataSet: The resulting kernel if found, else None.
        """
        self.counter += 1
        if cn(dataset, self.alpha):
            kr_logger.debug(f"Finding kernel for dataset with {len(dataset.get_elements_with_values())} elements: {dataset.get_elements_with_values()}")
            # Expand phase
            if self.div_conq_expand:
                expanded_dataset = expand_divide_and_conquer(dataset, self.alpha)
                kr_logger.debug(f"Dataset expanded using divide-and-conquer: {expanded_dataset.get_elements_with_values()}")
            else:
                expanded_dataset = expand(dataset, self.alpha, self.sw_expand)
                kr_logger.debug(f"Dataset expanded using sliding window of size {self.sw_expand}: {expanded_dataset.get_elements()}")

            # Shrink phase
            if self.div_conq_shrink:
                kernel = shrink_divide_and_conquer(expanded_dataset, self.alpha)
                kr_logger.debug(f"Dataset shrunk using divide-and-conquer: {kernel.get_elements_with_values()}")
            else:
                if self.sw_shrink > 1:
                    kernel = shrink_sliding_window(expanded_dataset, self.alpha, self.sw_shrink)
                    kr_logger.debug(f"Dataset shrunk using sliding window of size {self.sw_shrink}: {kernel.get_elements_with_values()}")
                else:
                    kernel = shrink(expanded_dataset, self.alpha)
                    kr_logger.debug(f"Dataset shrunk using basic shrink: {kernel.get_elements_with_values()}")
            self.computed_kernels.append(kernel)
            return kernel
        else:
            kr_logger.debug("Alpha is not a consequence of the dataset. Returning None.")
            self.computed_kernels.append('')
            return None
