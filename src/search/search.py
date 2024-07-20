from src.tree.hittingsettree import HSTreeNode, HittingSetTree
from src.kernels.kernelstrategy import KernelStrategy
from src.structs.dataset import DataSet
import logging
from src.structs.logger import setup_logging

# Set up logging for this module
setup_logging()

# Get the logger for this module
ss_logger = logging.getLogger(__name__)

class Search:
    def __init__(self, kernelStrategy: KernelStrategy, dataset: DataSet, alpha, strategy_param):
        self.kernelStrategy = kernelStrategy
        self.dataset = dataset
        self.alpha = alpha
        self.strategy_param = strategy_param
        self.tree = HittingSetTree(dataset=dataset)

    def log_tree(self):
        self.tree.print_tree_to_file()
        self.tree.print_newline()
