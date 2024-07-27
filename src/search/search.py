import logging
from src.pruner.basepruner import BasePruner
from src.pruner.best import BestPruner
from src.pruner.lower_max import LowerPruner
from src.pruner.upper_min import UpperPruner
from src.tree.brancher import Brancher
from src.tree.hittingsettree import HittingSetTree
from src.kernels.kernelstrategy import KernelStrategy
from src.structs.dataset import DataSet
from src.search.strategy import Strategy
from src.structs.logger import setup_logging

# Set up logging for this module
setup_logging()

ss_logger = logging.getLogger(__name__)

class Search(Strategy):
    def __init__(self, kernelStrategy: KernelStrategy, dataset: DataSet, pruner_type):
        self.kernelStrategy = kernelStrategy
        self.dataset = dataset
        self.tree = HittingSetTree(dataset=dataset)
        self.brancher = Brancher(kernelStrategy, self.dataset, self.tree)
        ss_logger.info("BRANCHER INITIALIZED")
        self.pruner_type = pruner_type
        self.leaf_nodes = []
        self.pruned_nodes = []
        
        # Initialize the appropriate pruner based on user input
        if pruner_type == 'UPPER':
            self.pruner = UpperPruner(kernelStrategy, self.tree)
        elif pruner_type == 'LOWER':
            self.pruner = LowerPruner(kernelStrategy, self.tree)
        elif pruner_type == 'BEST':
            self.pruner = BestPruner(kernelStrategy, self.tree)
        else:  # Default to BasePruner for no pruning
            self.pruner = BasePruner(kernelStrategy, self.tree)
        ss_logger.info("PRUNER INITIALIZED")

    def find_kernels(self) -> None:
        self.strategy.find_kernels()

    def search(self) -> None:
        self.strategy.search()

    def compute_node_kernel(self, node):
        result = self.kernelStrategy.find_kernel(node.dataset)
        if result is not None:
            node.set_kernel(result.get_elements())
        else:
            node.set_kernel("LEAF")
            ss_logger.info(f"ADDING LEAF NODE TO self.tree.LEAF_NODES: {node}")
            self.tree.add_leaf_node(node)

    def log_tree(self):
        self.tree.print_tree_to_file()
        self.tree.print_newline()
