from collections import deque
from src.search.search import Search
from src.tree.hittingsettree import HSTreeNode
import logging
from src.structs.logger import setup_logging

# Set up logging for this module
setup_logging()

# Get the logger for this module
ss_logger = logging.getLogger(__name__)

class BFS(Search):
    def __init__(self, kernelStrategy, dataset, pruner):
        super().__init__(kernelStrategy, dataset, pruner)

    def find_kernels(self) -> None:
        self.search(self.dataset)
        self.tree.print_tree()
        self.log_tree()

    def search(self, dataset):
        queue = deque()
        result = self.kernelStrategy.find_kernel(dataset)
        if result is not None:
            self.tree.root = HSTreeNode(kernel=result.get_elements(), dataset=dataset, path_value=0, parent=None)
            queue.append(self.tree.root)

        while queue:
            current_node = queue.popleft()
            if self.pruner.should_prune(current_node):
                current_node.kernel = "PRUNED"
                current_node.set_pruned()
                continue
            
            child_nodes = self.brancher.expand_children(current_node)
            ss_logger.info(f"Child nodes from brancher: {child_nodes}")
            for child_node in child_nodes:
                if child_node.kernel == 'LEAF':
                    self.pruner.update_boundary_with_leaf(current_node)
                else:
                    queue.append(child_node) 

        self.log_tree()
