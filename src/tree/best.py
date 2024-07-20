from src.tree.basepruner import BasePruner
import logging
from src.structs.logger import setup_logging


# Set up logging for this module
setup_logging()

# Get the logger for this module
tree_logger = logging.getLogger(__name__)

class BestPruner(BasePruner):
    def __init__(self, tree, brancher):
        self.tree = tree
        self.brancher = brancher
        self.optimal_reached = False
        self.best_solution = None
        self.boundary = 0

    def update_boundary_with_leaf(self, leaf_node):
        #leaf_path_measure = self.tree.calculate_path_bbvalue_up_to_root(leaf_node)
        leaf_path_measure = self.tree.get_hitting_set_for_leaf(leaf_node).sum_values()
        dataset_sum = self.tree.dataset.sum_values()
        if leaf_path_measure == dataset_sum:
            self.optimal_reached = True
            self.best_leaf = leaf_node
            tree_logger.info(f"Optimal reached: {self.optimal_reached}")
            print(f"Optimal reached: {self.optimal_reached}")

    def should_prune(self, node):
        if self.boundary == 0:
            return False
        if not self.optimal_reached:
            return False
        if node is None or node.get_kernel() is None:
            return True
        return len(self.tree.get_hitting_set_for_leaf(node).get_elements()) >= len(self.tree.get_hitting_set_for_leaf(self.best_leaf).get_elements())
