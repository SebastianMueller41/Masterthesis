from src.tree.hittingsettree import HSTreeNode
from src.search.strategy import Strategy
from src.search.search import Search
import logging
from src.structs.logger import setup_logging

# Set up logging for this module
setup_logging()

# Get the logger for this module
ss_logger = logging.getLogger(__name__)

class DFS(Strategy, Search):
    def __init__(self, kernelStrategy, dataset, brancher, pruner, alpha, strategy_param):
        Search.__init__(self, kernelStrategy, dataset, alpha, strategy_param)
        self.pruner = pruner
        self.brancher = brancher

    def find_kernels(self) -> None:
        self.dfs(self.dataset, self.alpha)
        self.tree.print_tree()
        self.log_tree()

    def dfs(self, dataset, alpha, parent: HSTreeNode = None):
        if parent is None:
            result = self.kernelStrategy.find_kernel(dataset, alpha)
            if result is None:
                ss_logger.info("Initial kernel is None, no need to span the tree.")
                return
            self.tree.root = HSTreeNode(kernel=result.get_elements(), dataset=dataset, bbvalue=0, parent=None)
            self.dfs(self.tree.root.dataset, alpha, self.tree.root)
        else:
            if self.pruner.should_prune(parent):
                parent.kernel = "PRUNED"
                parent.set_pruned()
                return
            for element in parent.get_kernel():
                reduced_dataset = parent.get_dataset().clone()
                reduced_dataset.remove_element(element)

                bbvalue = self.brancher.calculate_bbvalue(parent, element, reduced_dataset)
                child_node = HSTreeNode(kernel=None, dataset=reduced_dataset, edge=element, level=parent.level + 1, bbvalue=bbvalue, parent=parent)
                parent.add_child(child_node)

                result = self.kernelStrategy.find_kernel(reduced_dataset, alpha)
                if result is not None:
                    child_node.set_kernel(result.get_elements())
                    self.dfs(child_node.get_dataset(), alpha, child_node)
                else:
                    child_node.set_kernel("LEAF")
                    self.tree.add_leaf_node(child_node)
                    self.pruner.update_boundary_with_leaf(child_node)
        self.log_tree()
