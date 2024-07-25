from src.pruner.basepruner import BasePruner
import logging
from src.structs.logger import setup_logging

# Set up logging for this module
setup_logging()

# Get the logger for this module
prune_logger = logging.getLogger(__name__)
prune_logger.info("Pruner called.")

class BestPruner(BasePruner):
    def __init__(self, kernel_strategy, tree, alpha):
        super().__init__(kernel_strategy, tree, alpha)
        self.card_check = self.has_zero_value(self.tree.dataset)
        prune_logger.debug(f"Cardinality check set to: {self.card_check}, because {self.tree.dataset.sum_values()} <= {len(self.tree.dataset.get_elements())}")
        self.max_reached = False  # Initialize max_reached
        self.boundary = 0  # Initialize boundary

    def update_boundary_with_leaf(self, leaf_node):
        leaf_path_measure = self.tree.get_hitting_set_for_leaf(leaf_node).sum_values()
        dataset_sum = self.tree.dataset.sum_values()
        
        prune_logger.debug(f"Leaf path measure: {leaf_path_measure}, Dataset sum: {dataset_sum}")

        if leaf_path_measure == dataset_sum:
            self.max_reached = True
            self.best_leaf = leaf_node
            self.boundary = len(self.tree.get_hitting_set_for_leaf(leaf_node).get_elements())
            self.tree.boundary = self.boundary
            prune_logger.info(f"Optimal reached with: {self.tree.get_hitting_set_for_leaf(leaf_node).get_elements()}")

    def should_prune(self, node):
        if node is None:
            prune_logger.debug("Node is None, pruning.")
            return True
        
        prune_logger.debug(f"Node BBValue: {node.bbvalue}, Current boundary: {self.boundary}, Max reached: {self.max_reached}")
        
        if self.boundary == 0:
            prune_logger.debug("Boundary is zero, not pruning.")
            return False
        
        if not self.max_reached:
            prune_logger.debug("Max not reached, not pruning.")
            return False
        
        if self.card_check:
            hs_cardinality = len(self.tree.get_hitting_set_for_leaf(node).get_elements())
            best_cardinality = len(self.tree.get_hitting_set_for_leaf(self.best_leaf).get_elements())
            prune_logger.info(f"Hitting set cardinality: {hs_cardinality}, Best leaf cardinality: {best_cardinality}")
            return hs_cardinality >= best_cardinality
        
        return False
    
    def has_zero_value(self, dataset):
        for _, value in dataset.get_elements_with_values():
            if value == 0:
                return True
        return False
