import csv
import logging
from src.pruner.lower_max import LowerPruner
from src.pruner.upper_min import UpperPruner
from src.structs.dataset import get_incon_values, get_random_values
from src.structs.logger import setup_logging

# Set up logging for this module
setup_logging()

# Get the logger for this module
data_logger = logging.getLogger(__name__)

class ResultCalculator:
    def __init__(self, kernelStrategy, search_strategy, tree, execution_time, ressources, value, filename, output_file):
        self.random_values = get_random_values()
        self.incon_values = get_incon_values()
        self.kernelStrategy = kernelStrategy
        self.search_strategy = search_strategy
        self.tree = tree
        self.execution_time = execution_time
        self.ressources = ressources
        self.value = value
        self.filename = filename
        self.output_file = output_file
        self.best_leaf_index = 0
        self.leaf_nodes = []
        self.result = {
            'max_hs_val': None,
            'max_hs_card': None,
            'min_hs_val': None,
            'min_hs_card': None,
            'num_kernels': None,
            'num_branches': None,
            'tree_depth': None,
            #'upperBound' : None,
            #'lowerBound': None,
            'pruned_branches_count': None,
            'result_value': None,
            'cardinality_value': None,
            'max_random_value': None,
            'max_incon_value': None,
            'min_rand_value': None,
            'min_incon_val': None,
            'max_card': None,
            'min_card': None,
            'opt_hs_value': None,
            'opt_hs_card': None,
            'max_hs_random_card': None,
            'max_hs_incon_card': None,
            'min_hs_random_card': None,
            'min_hs_incon_card': None
        }
        self.create_leaf_node_dict()

    def create_leaf_node_dict(self):
        # Create a list of tuples containing (BBVALUE, hitting_set, LEAF_NODE)
        self.leaf_nodes = [(bbvalue, len(self.tree.get_hitting_set_for_leaf(leaf).get_elements()), leaf) for bbvalue, leaf in self.tree.leaf_nodes]
        self.sort_leaf_nodes_desc()

    def sort_leaf_nodes_asc(self):
        # Sort the list based on BBVALUE (descending) and then Cardinality (ascending)
        self.leaf_nodes = sorted(self.leaf_nodes, key=lambda x: (x[0], -x[1])) 

    def sort_leaf_nodes_desc(self):
        # Sort the list based on BBVALUE (descending) and then Cardinality (ascending)
        self.leaf_nodes = sorted(self.leaf_nodes, key=lambda x: (-x[0], -x[1])) 

    def print_results(self):
        self.calculate()

        print(f"\n*********** EXECUTION AND PERFORMANCE PARAMETERS ***********")
        print(f"\nExecution time: {self.execution_time} \nMemory Used: {self.ressources} \nKernels: {self.result['num_kernels']}, \nBranches {self.result['num_branches']}:")
        print(f"\nBranches: {self.result['num_branches']} \nTree depth: {self.result['tree_depth']} \nPruned branches: {self.result['pruned_branches_count']}")
        
        print(f"Upper Bound: {self.tree.upperBound}, Lower Bound: {self.tree.lowerBound}")

        print(f"\n*********** SEARCH & STRATEGY PARAMETERS ***********")
        print(f"\nAlpha: {self.kernelStrategy.alpha} \nValue Assignment Strategy: {self.value}, \nSearch Strategy: {self.search_strategy}")
        print(f"Pruner: {self.search_strategy.pruner.__class__.__name__} \nShrink Sliding Window size: {self.search_strategy.kernelStrategy.sw_shrink} \nExpand Sliding Window size: {self.search_strategy.kernelStrategy.sw_expand} \nShrink Divide and Conquer: {self.search_strategy.kernelStrategy.div_conq_shrink} \nExpand Divide and Conquer: {self.search_strategy.kernelStrategy.div_conq_expand}")

        print(f"\n*********** RESULTS ***********")
        if self.leaf_nodes:
            print(f"\nOptimal hitting set: {self.tree.get_hitting_set_for_leaf(self.leaf_nodes[self.best_leaf_index][2]).get_elements()} with: \n- Value: {self.result['result_value']} \n- Cardinality: {self.result['cardinality_value']}")
        else:
            print(f"No Hitting Sets Found.")

        print()
        for bbvalue, hitting_set_card, leaf in self.leaf_nodes:
            print(f"{bbvalue}, {hitting_set_card}, {self.tree.get_hitting_set_for_leaf(leaf).get_elements()}")

        print(f"\n*********** VERIFICATION ***********")
        print(f"\nMax values (Cardinality, Random, Inconsistency): \n- Value: {self.result['max_hs_val']}, {self.result['max_random_value']}, {self.result['max_incon_value']}\n- Cardinality: {self.result['max_hs_random_card']}, {self.result['max_hs_incon_card']}")
        print(f"\nMin values (Cardinality, Random, Inconsistency): \n- Value: {self.result['min_hs_val']}, {self.result['min_rand_value']}, {self.result['min_incon_val']}\n- Cardinality: {self.result['min_hs_random_card']}, {self.result['min_hs_incon_card']}")

    def print_results_to_file(self):
        self.write_to_csv()

    def log_results(self, conn):
        self.log_execution_data()
        conn.close()

    def write_to_csv(self):
        num_kernels, num_branches = self.tree.count_kernels_and_branches()
        tree_depth = self.tree.tree_depth()
        strategy_param = 2
        # Write the leaf nodes with their BBVALUE, cardinality, and hitting set to a CSV file
        with open(self.output_file, 'a', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow([self.execution_time, self.filename, strategy_param, num_kernels, num_branches, tree_depth, self.kernelStrategy.alpha, 'NONE'])
            for bbvalue, cardinality, leaf in self.leaf_nodes:
                hitting_set = self.tree.get_hitting_set_for_leaf(leaf).get_elements()
                # Convert hitting_set to a string
                hitting_set_str = ', '.join(hitting_set)
                csvwriter.writerow([bbvalue, cardinality, hitting_set_str])

    def calculate(self):
        if isinstance(self.search_strategy.pruner, UpperPruner):
            self.sort_leaf_nodes_asc()

        # Debugging statement to print leaf_nodes
        data_logger.debug(f"\nLeaf nodes: {self.leaf_nodes}")

        # Ensure leaf_nodes is not empty
        if not self.leaf_nodes:
            data_logger.debug("No leaf nodes found.")
            return

        # Check and calculate max_hs_val and max_hs_card
        if self.leaf_nodes:
            self.result['opt_hs_val'] = self.leaf_nodes[0][0]
            self.result['opt_hs_card'] = self.leaf_nodes[0][1]
            print(f"\nOptimal HS Val: {self.result['opt_hs_val']}, Optimal HS Card: {self.result['opt_hs_card']}")

        #self.result['upperBound'] = self.search_strategy.pruner.upperBound
        #self.result['lowerBound'] = self.search_strategy.pruner.lowerBound
        self.result['num_kernels'], self.result['num_branches'] = self.tree.count_kernels_and_branches()
        self.result['tree_depth'] = self.tree.tree_depth()
        self.result['pruned_branches_count'] = self.tree.count_pruned_nodes()
        self.best_leaf = self.leaf_nodes[self.best_leaf_index][2]
        self.best_hitting_set = self.tree.get_hitting_set_for_leaf(self.best_leaf)
        self.result['result_value'] = self.best_hitting_set.sum_values()
        self.result['cardinality_value'] = len(self.best_hitting_set.get_elements())

        max_random_value, max_incon_value, min_rand_value, min_incon_val, max_card, min_card = self.get_values_from_db()

        self.result['max_random_value'] = max_random_value
        self.result['max_incon_value'] = max_incon_value
        self.result['min_rand_value'] = min_rand_value
        self.result['min_incon_val'] = min_incon_val
        self.result['max_card'] = max_card
        self.result['min_card'] = min_card
        self.result['max_hs_random_card'] = 0
        self.result['max_hs_incon_card'] = 0
        self.result['min_hs_random_card'] = 0
        self.result['min_hs_incon_card'] = 0

    def get_values_from_db(self):
        return 0, 0, 0, 0, 0, 0
