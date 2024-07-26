from itertools import combinations
from src.kernels.shrinkexpand import ShrinkExpand
from src.pruner.basepruner import BasePruner
import logging
from src.structs.logger import setup_logging

# Set up logging for this module
setup_logging()

# Get the logger for this module
prune_logger = logging.getLogger(__name__)
prune_logger.info("Pruner called.")

class BestPruner(BasePruner):
    def __init__(self, kernel_strategy, tree):
        super().__init__(kernel_strategy, tree)
        self.card_check = self.has_potential_duplicate_sums() # Initial check if dataset qualifies for this approach
        prune_logger.info(f"Cardinality check set to: {self.card_check}, because {self.tree.dataset.sum_values()} <= {len(self.tree.dataset.get_elements())}")
        self.max_reached = False  # Initialize max_reached
        if not self.card_check:
            return None

    def update_boundary_with_leaf(self, leaf_node):
        leaf_path_measure = leaf_node.path_value
        dataset_sum = self.tree.dataset.sum_values()
        
        prune_logger.info(f"Leaf path measure: {leaf_path_measure}, Dataset sum: {dataset_sum}")

        remainder_value = self.find_remainder_in_dataaset(self.tree.dataset).sum_values()
        prune_logger.debug(f"Remaidner_value = {remainder_value}")

        if leaf_path_measure >= self.tree.lowerBound: # ASSUMPTION: We find the highest possible value with the first leaf!
            self.tree.lowerBound = leaf_path_measure
            upperBoundCard = len(self.tree.get_hitting_set_for_leaf(leaf_node).get_elements()) 
            prune_logger.debug(f"Highest value reached: {leaf_path_measure}, checking for lower cardinality lower than {upperBoundCard}")
            if upperBoundCard < self.tree.upperBound:
                self.tree.upperBound = upperBoundCard
                prune_logger.debug(f"Lower found, updating upperBound to {upperBoundCard}")

    def should_prune(self, node):        
        prune_logger.debug(f"Node path_value: {node.path_value}, Current lowerBound: {self.tree.lowerBound}, Max reached: {self.max_reached}")
        
        if self.tree.lowerBound == 0:
            prune_logger.debug("Boundary is zero, not pruning.")
            return False
        
        if not self.max_reached or self.tree.lowerBound:
            prune_logger.debug("Max not reached, not pruning.")
            return False
        
        if self.card_check:
            hs_cardinality = len(self.tree.get_hitting_set_for_leaf(node).get_elements())
            prune_logger.info(f"Hitting set cardinality: {hs_cardinality}, Best leaf cardinality: {self.tree.upperBound}")
            return hs_cardinality >= self.tree.upperBound
        
        return False
    
    # Check if sum values of dataset qualify for best approach. 
    # True, if two subsets of the list with the same score and different cardinalities is possible
    def has_potential_duplicate_sums(self):
        elements_with_values = self.tree.dataset.get_elements_with_values()
        n = len(elements_with_values)
        sum_cardinality_map = {}

        # Iterate over all possible subsets
        for r in range(1, n + 1):  # Start from 1 to n, excluding empty subset
            for subset in combinations(elements_with_values, r):
                subset_sum = sum(value for _, value in subset)
                cardinality = len(subset)

                # Check if there is already a subset with the same sum but different cardinality
                if subset_sum in sum_cardinality_map:
                    if sum_cardinality_map[subset_sum] != cardinality:
                        return True
                else:
                    sum_cardinality_map[subset_sum] = cardinality

        return False

