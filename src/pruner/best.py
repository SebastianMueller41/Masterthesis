from src.pruner.basepruner import BasePruner
import logging
from src.structs.logger import setup_logging

# Set up logging for this module
setup_logging()

# Get the logger for this module
prune_logger = logging.getLogger(__name__)

class BestPruner(BasePruner):
    def __init__(self, tree):
        self.tree = tree
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
            self.boundary = len(self.tree.get_hitting_set_for_leaf(leaf_node).get_elements())
            self.tree.boundary = self.boundary
            prune_logger.info(f"Optimal reached with: {self.tree.get_hitting_set_for_leaf(leaf_node).get_elements()}")

    def should_prune(self, node):
        if self.boundary == 0:
            prune_logger.debug("Boundary == 0, Return False")
            return False
        if not self.optimal_reached:
            prune_logger.debug("Optimal reached, Return False")
            return False
        if node is None:
            prune_logger.debug(f"Node is None: {node}, node.get_kernrel() is None: {node.get_kernel()}")
            return True
        HS_card = len(self.tree.get_hitting_set_for_leaf(node).get_elements())
        Best_card = len(self.tree.get_hitting_set_for_leaf(self.best_leaf).get_elements())
        prune_logger.info(f"Hitting_set_length: {HS_card}, Leaf_card: {Best_card}")
        return HS_card >= Best_card


#104, 120