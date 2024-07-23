from src.pruner.basepruner import BasePruner
import logging
from src.structs.logger import setup_logging
from src.structs.dataset import get_strategy_param

# Set up logging for this module
setup_logging()

# Get the logger for this module
prune_logger = logging.getLogger(__name__)

class BestPruner(BasePruner):
    def __init__(self, tree, strategy_param):
        self.tree = tree
        self.optimal_reached = False
        self.best_solution = None
        self.boundary = 0
        self.strategy_param = strategy_param
        self.card_check = self.has_zero_value(self.tree.dataset)
        prune_logger.debug(f"Cardinality set to: {self.card_check}, because {self.tree.dataset.sum_values()} <= {len(self.tree.dataset.get_elements())}")

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
        # Check if node is None
        if node is None:
            prune_logger.debug(f"Node is {node}")
            return True
        
        # Check if boundary is zero
        if self.boundary == 0:
            prune_logger.debug(f"Lower boundary is {self.boundary}, returning False.")
            return False
        
        # Check if optimal solution is reached
        if not self.optimal_reached:
            prune_logger.debug(f"Upper bound = {self.optimal_reached}, Optimal solution not reached, returning False.")
            return False
        
        # Check hitting set cardinality
        if self.card_check:
            prune_logger.debug(f"Upper bound = {self.optimal_reached}, Lower bound = {self.boundary}")
            hs_cardinality = len(self.tree.get_hitting_set_for_leaf(node).get_elements())
            best_cardinality = len(self.tree.get_hitting_set_for_leaf(self.best_leaf).get_elements())
            prune_logger.info(f"Hitting set length: {hs_cardinality}, Best leaf cardinality: {best_cardinality}")
            return hs_cardinality >= best_cardinality

        return False
    
    # Check if any element of the dataset has a value of 0
    def has_zero_value(self, dataset):
        for _, value in dataset.get_elements_with_values():
            if value == 0:
                return True
        return False