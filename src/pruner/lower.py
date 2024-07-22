from src.pruner.basepruner import BasePruner
import logging
from src.structs.logger import setup_logging

# Set up logging for this module
setup_logging()

# Get the logger for this module
prune_logger = logging.getLogger(__name__)

class LowerPruner(BasePruner):
    def __init__(self, tree, strategy_param):
        self.tree = tree
        self.best_solution = None
        self.boundary = 0
        self.strategy_param = strategy_param

    # This approach is not used but maybe interesting for future work
    def calculate_bbvalue(self, element, dataset):
        assigned_value = dataset.get_element_value(element)
        transformed_value = 1 / (assigned_value) if assigned_value != 0 else 0
        return transformed_value

    def update_boundary_with_leaf(self, leaf_node):
        #leaf_path_measure = self.tree.calculate_path_bbvalue_up_to_root(leaf_node)
        leaf_path_measure = self.tree.get_hitting_set_for_leaf(leaf_node).sum_values()
        if leaf_path_measure > self.boundary:
            self.boundary = leaf_path_measure
            prune_logger.debug(f"Updated boundary: {self.boundary}")

    def should_prune(self, node):
        if self.boundary == 0:
            return False
        path_value = self.tree.calculate_path_bbvalue_up_to_root(node) 
        prune_logger.info(f"Should prune? {path_value <= self.boundary}")
        return path_value <= self.boundary