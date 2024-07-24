import csv
from src.pruner.lower_max import LowerPruner
from src.pruner.upper_min import UpperPruner
from src.structs.dataset import get_incon_values, get_random_values


class ResultCalculator:
    def __init__(self, tree, pruner, execution_time, ressources, alpha, search_strategy, value, filename, output_file):
        self.random_values = get_random_values()
        self.incon_values = get_incon_values()
        self.tree = tree
        self.pruner = pruner
        self.execution_time = execution_time
        self.ressources = ressources
        self.ss = search_strategy
        self.alpha = alpha
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
            'upper_bound' : None,
            'lower_bound': None,
            'pruned_branches_count': None,
            'result_value': None,
            'cardinality_value': None,
            'max_random_value': None,
            'max_incon_value': None,
            'min_rand_value': None,
            'min_incon_val': None,
            'max_card': None,
            'min_card': None,
        }
        self.create_leaf_node_dict()

    def create_leaf_node_dict(self):
        # Create a list of tuples containing (BBVALUE, hitting_set, LEAF_NODE)
        self.leaf_nodes = [(bbvalue, len(self.tree.get_hitting_set_for_leaf(leaf).get_elements()), leaf) for bbvalue, leaf in self.tree.leaf_nodes]
        self.sort_leaf_nodes()

    def sort_leaf_nodes(self):
        # Sort the list based on BBVALUE (descending) and then Cardinality (ascending)
        self.leaf_nodes = sorted(self.leaf_nodes, key=lambda x: (-x[0], -x[1])) 
    def print_results(self):
        self.calculate()

        print(f"\n*********** EXECUTION AND PERFORMANCE PARAMETERS ***********")
        print(f"\nExecution time: {self.execution_time} \nMemory Used: {self.ressources} \nKernels: {self.result['num_kernels']}, \nBranches {self.result['num_branches']}:")
        print(f"\nBranches: {self.result['num_branches']} \nTree depth: {self.result['tree_depth']} \nPruned branches: {self.result['pruned_branches_count']}")
        
        print(f"Upper Bound: {self.result['upper_bound']}, Lower Bound: {self.result['lower_bound']}")

        print(f"\n*********** SEARCH & STRATEGY PARAMETERS ***********")
        print(f"\nAlpha: {self.alpha} \nValue Assignment Strategy: {self.value}, \nSearch Strategy: {self.ss}")
        print(f"Pruner: {self.pruner.__class__.__name__} \nShrink Sliding Window size: {self.pruner.kernel_strategy.sw_shrink} \nExpand Sliding Window size: {self.pruner.kernel_strategy.sw_expand} \nShrink Divide and Conquer: {self.pruner.kernel_strategy.div_conq_shrink} \nExpand Divide and Conquer: {self.pruner.kernel_strategy.div_conq_expand}")

        print(f"\n*********** RESULTS ***********")
        print(f"\nOptimal hitting set: {self.tree.get_hitting_set_for_leaf(self.leaf_nodes[self.best_leaf_index][2]).get_elements()} with: \n- Value: {self.result['result_value']} \n- Cardinality: {self.result['cardinality_value']}")

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
            csvwriter.writerow([self.execution_time, self.filename, strategy_param, num_kernels, num_branches, tree_depth, self.alpha, 'NONE'])
            for bbvalue, cardinality, leaf in self.leaf_nodes:
                hitting_set = self.tree.get_hitting_set_for_leaf(leaf).get_elements()
                # Convert hitting_set to a string
                hitting_set_str = ', '.join(hitting_set)
                csvwriter.writerow([bbvalue, cardinality, hitting_set_str])

    def calculate(self):
        # Debugging statement to print leaf_nodes
        print(f"\nLeaf nodes: {self.leaf_nodes}")

        # Ensure leaf_nodes is not empty
        if not self.leaf_nodes:
            print("No leaf nodes found.")
            return

        for bbvalue, hitting_set_card, leaf in self.leaf_nodes:
            print(f"{bbvalue}, {hitting_set_card}, {self.tree.get_hitting_set_for_leaf(leaf).get_elements()}")

        # Check and calculate max_hs_val and max_hs_card
        if isinstance(self.pruner, UpperPruner):
            if self.leaf_nodes:

                min_hs_val = max(self.leaf_nodes, key=lambda x: x[0])[0]
                min_hs_card = max(self.leaf_nodes, key=lambda x: x[1])[1]
                self.result['min_hs_val'] = min_hs_val
                self.result['min_hs_card'] = min_hs_card
                print(f"\nMin HS Val: {self.result['min_hs_val']}, Min HS Card: {self.result['min_hs_card']}")
            else:
                print("No leaf nodes available for calculating max values.")

        # Check and calculate min_hs_val and min_hs_card
        if isinstance(self.pruner, LowerPruner):
            if self.leaf_nodes:
                self.best_leaf_index = -1
                self.result['max_hs_val'] = min(self.leaf_nodes, key=lambda x: x[0])[0]
                self.result['max_hs_card'] = min(self.leaf_nodes, key=lambda x: x[1])[1]
                print(f"\nMax HS Val: {self.result['max_hs_val']}, Max HS Card: {self.result['max_hs_card']}")
            else:
                print("No leaf nodes available for calculating min values.")

        self.result['upper_bound'] = self.pruner.upper_bound
        self.result['lower_bound'] = self.pruner.lower_bound
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
