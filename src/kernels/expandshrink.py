import logging
from .kernelstrategy import KernelStrategy
from src.kernels.kernel_utils import expand, shrink, divide_and_conquer, cn

class ExpandShrink(KernelStrategy):
    def __init__(self, window_size=1, divide_and_conquer=False):
        self.window_size = window_size
        self.div_conq = divide_and_conquer

    def find_kernel(self, dataset, alpha):
        if cn(dataset, alpha):
            logging.debug(f"Finding kernel for {len(dataset.get_elements())} elements of dataset = {dataset.get_elements()}")
            expanded_dataset = expand(dataset, alpha, self.window_size)
            if expanded_dataset:
                if self.div_conq:
                    return divide_and_conquer(expanded_dataset, alpha)
                else:
                    return shrink(expanded_dataset, alpha)
            else:
                logging.debug(f"Expansion resulted in empty dataset")
                return None
        else:
            logging.debug(f"Dataset does not entail {alpha}, kernel = empty")
            return None
