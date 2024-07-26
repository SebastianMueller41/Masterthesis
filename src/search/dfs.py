from src.search.search import Search
from src.tree.hittingsettree import HSTreeNode
import logging
from src.structs.logger import setup_logging

# Set up logging for this module
setup_logging()

# Get the logger for this module
ss_logger = logging.getLogger(__name__)

class DFS(Search):
    def __init__(self, kernelStrategy, dataset, pruner):
        super().__init__(kernelStrategy, dataset, pruner)
        ss_logger.debug("Initialized DFS")

    def find_kernels(self) -> None:
        ss_logger.debug("FINDING KERNEL")
        self.dfs(self.dataset, None)
        self.tree.print_tree()
        self.log_tree()


    def dfs(self, dataset, parent: HSTreeNode = None):
        if parent is None:
            result = self.kernelStrategy.find_kernel(dataset)
            if result is None:
                ss_logger.info("Initial kernel is None, no need to span the tree.")
                return
            self.tree.root = HSTreeNode(kernel=result.get_elements(), dataset=dataset, path_value=0, parent=None)
            self.dfs(self.tree.root.dataset, self.tree.root)
        else:
            if self.pruner.should_prune(parent):
                parent.kernel = "PRUNED"
                parent.set_pruned()
                return

            child_nodes = self.brancher.expand_children(parent)
            ss_logger.info(f"Child nodes from brancher: {child_nodes}")
            for child_node in child_nodes:
                if child_node.kernel == 'LEAF':
                    self.pruner.update_boundary_with_leaf(child_node)
                else:
                    self.dfs(child_node.get_dataset(), child_node)
        self.log_tree()

