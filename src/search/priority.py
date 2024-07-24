import heapq
import logging
from src.pruner.lower_max import LowerPruner
from src.pruner.upper_min import UpperPruner
from src.search.search import Search
from src.search.strategy import Strategy
from src.tree.hittingsettree import HSTreeNode, HittingSetTree
from src.structs.logger import setup_logging

# Set up logging for this module
setup_logging()

# Get the logger for this module
ss_logger = logging.getLogger(__name__)

class PBS(Strategy, Search):
    def __init__(self, kernelStrategy, dataset, brancher, pruner, alpha, strategy_param):
        Search.__init__(self, kernelStrategy, dataset, alpha, strategy_param)
        self.kernelStrategy = kernelStrategy
        self.dataset = dataset
        self.alpha = alpha
        self.strategy_param = strategy_param
        self.tree = HittingSetTree(dataset=dataset)
        self.brancher = brancher
        self.pruner = pruner
        self.best_leaf = HSTreeNode(dataset=dataset)
        self.priority_queue = self.brancher.min_heap  # Use the min_heap from brancher

    def find_kernels(self) -> None:
        initial_node = self.create_initial_node(self.dataset, self.alpha)
        ss_logger.info("Initial kernel found!")
        if initial_node is None:
            ss_logger.info("Initial kernel is None, no need to span the tree.")
            return
        self.priority_search(initial_node)
        self.tree.print_tree()
        self.log_tree()

    def create_initial_node(self, dataset, alpha):
        result = self.kernelStrategy.find_kernel(dataset, alpha)
        if result is None:
            return None
        initial_node = HSTreeNode(kernel=result.get_elements(), dataset=dataset, bbvalue=0, parent=None)
        self.tree.root = initial_node
        return initial_node

    def priority_search(self, root: HSTreeNode):
        self.brancher.add_to_priority_queue(root, 0)
        ss_logger.info(f"Priority search started")

        while self.priority_queue:
            element = self.brancher.pop_element(self.pruner)
            ss_logger.debug(f"Popped element: {element}")
            if element is None:
                ss_logger.error("Attempted to pop from an empty heap")
                break
            _, current_node = element
            ss_logger.info("CHECK PRUNE!")
            if self.pruner.should_prune(current_node):
                ss_logger.info("Node pruned")
                current_node.kernel = "PRUNED"
                current_node.set_pruned()
                continue
            if current_node.get_kernel() is None:
                result = self.kernelStrategy.find_kernel(current_node.get_dataset(), self.alpha)
                if result is not None:
                    current_node.set_kernel(result.get_elements())
                    self.brancher.expand_children(current_node, self.priority_queue)
                else:
                    current_node.set_kernel("LEAF")
                    self.tree.add_leaf_node(current_node)
                    self.pruner.update_boundary_with_leaf(current_node)
            else:
                self.brancher.expand_children(current_node, self.priority_queue)

            self.log_tree()
