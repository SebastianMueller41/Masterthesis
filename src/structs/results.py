import csv
import io
import logging
import sys
from src.CNFconverter.parse import CNFConverter
from src.database.database import log_execution_data
from src.pruner.lower_max import LowerPruner
from src.pruner.upper_min import UpperPruner
from src.pruner.best import BestPruner  # Assuming BestPruner is imported from this module
from src.structs.dataset import get_incon_values, get_random_values
from src.structs.logger import setup_logging

# Set up logging for this module
setup_logging()

# Get the logger for this module
data_logger = logging.getLogger(__name__)

class ResultCalculator:
    def __init__(self, conn, kernelStrategy, dataset, search_strategy, tree, execution_time, resources, filename, output_file, value):
        self.random_values = get_random_values()
        self.incon_values = get_incon_values()
        self.conn = conn
        self.kernelStrategy = kernelStrategy
        self.search_strategy = search_strategy
        self.tree = tree
        self.execution_time = execution_time
        self.resources = resources
        self.value_param = value
        self.filename = filename
        self.output_file = output_file
        self.dataset = dataset
        self.best_leaf_index = 0
        self.leaf_nodes = []
        self.result = {
            'num_kernels': None,
            'num_branches': None,
            'tree_depth': None,
            'upperBound': None,
            'lowerBound': None,
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
            'min_hs_incon_card': None,
            'card_max_random': None,
            'card_max_incon': None,
            'card_min_random': None,
            'card_min_incon': None,
            'min_card_max_value_random': None,
            'min_card_max_value_random': None,
            'optimal_solution_found': False
        }

    def create_leaf_node_dict(self):
        # Create a list of tuples containing (BBVALUE, hitting_set, LEAF_NODE)
        self.leaf_nodes = [(bbvalue, len(self.tree.get_hitting_set_for_leaf(leaf).get_elements()), leaf) for bbvalue, leaf in self.tree.leaf_nodes]
        self.sort_leaf_nodes_desc()

    def sort_leaf_nodes_asc(self):
        # Sort the list based on BBVALUE (ascending) and then Cardinality (ascending)
        self.leaf_nodes = sorted(self.leaf_nodes, key=lambda x: (x[0], x[1]))

    def sort_leaf_nodes_desc(self):
        # Sort the list based on BBVALUE (descending) and then Cardinality (ascending)
        self.leaf_nodes = sorted(self.leaf_nodes, key=lambda x: (-x[0], x[1]))

    def print_results(self):
        if self.tree is None:
            pass
        self.create_leaf_node_dict()
        self.calculate()

        print(f"\n*********** EXECUTION AND PERFORMANCE PARAMETERS ***********")
        print(f"\nExecution time: {self.execution_time} \nMemory Used: {self.resources} \nKernels: {self.result['num_kernels']}")
        print(f"\nBranches: {self.result['num_branches']} \nTree depth: {self.result['tree_depth']} \nPruned branches: {self.result['pruned_branches_count']}")
        
        print(f"Upper Bound: {self.tree.upperBound}, Lower Bound: {self.tree.lowerBound}")

        print(f"\n*********** SEARCH & STRATEGY PARAMETERS ***********")
        print(f"\nAlpha: {self.kernelStrategy.alpha} \nValue Assignment Strategy: {self.value_param}, \nSearch Strategy: {self.search_strategy.__class__.__name__}")
        print(f"Pruner: {self.search_strategy.pruner_type} \nShrink Sliding Window size: {self.search_strategy.kernelStrategy.sw_shrink} \nExpand Sliding Window size: {self.search_strategy.kernelStrategy.sw_expand} \nShrink Divide and Conquer: {self.search_strategy.kernelStrategy.div_conq_shrink} \nExpand Divide and Conquer: {self.search_strategy.kernelStrategy.div_conq_expand}")

        print(f"\n*********** RESULT PARAMETERS ***********")
        if self.leaf_nodes:
            print(f"\nOptimal hitting set: {self.result['optimal_HS'].get_elements()} with: \n- Value: {self.result['result_value']} \n- Cardinality: {self.result['cardinality_value']}")
        else:
            print(f"No Hitting Sets Found.")

        print()
        for bbvalue, hitting_set_card, leaf in self.leaf_nodes:
            print(f"{bbvalue}, {hitting_set_card}, {self.tree.get_hitting_set_for_leaf(leaf).get_elements()}")

        print(f"\n*********** VERIFICATION ***********")
        print(f"\nMax values (Cardinality, Random, Inconsistency): \n- Value: {self.result['max_card']}, {self.result['max_random_value']}, {self.result['max_incon_value']}\n- Cardinality: {self.result['max_card']}, {self.result['card_max_random']}, {self.result['card_max_incon']}")
        print(f"\nMin values (Cardinality, Random, Inconsistency): \n- Value: {self.result['min_card']}, {self.result['min_rand_value']}, {self.result['min_incon_val']}\n- Cardinality: {self.result['min_card']}, {self.result['card_min_random']}, {self.result['card_min_incon']}")

        print("\nLEAFS found in order: (Path_value, Cardinality, Hitting_set)")
        for leaf in self.search_strategy.leaf_nodes: 
            print(f"{leaf.path_value}, {len(self.tree.get_hitting_set_for_leaf(leaf).get_elements())},{self.tree.get_hitting_set_for_leaf(leaf).get_elements()}") 

        # Print the optimal solution found status
        print("\n*** OPTIMAL RESULT FOUND? ***")
        print(f"----------> {self.result['optimal_solution_found']} <----------")

    def print_results_to_file(self):
        # Create a StringIO object to capture the print output
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout

        try:
            # Call the print_results method to capture its output
            self.print_results()
        finally:
            # Restore the original standard output
            sys.stdout = old_stdout

        # Get the captured output
        output = new_stdout.getvalue()

        # Write the captured output to the output file
        with open(self.output_file, 'a') as file:
            file.write(output)
        self.print_cnf_repair()

    def print_cnf_repair(self):
        file_repair = "Results/dataset_repair.cnf"
        if self.leaf_nodes:
            repaired_dataset = self.dataset.clone()
            for element in self.result['optimal_HS'].get_elements():
                repaired_dataset.remove_element(element)
            repaired_dataset.to_file(file_repair)
            cnf_converter = CNFConverter(verbose=False)
            cnf_converter.convert_to_cnf(file_repair, file_repair)

    def print_baseline_results_to_file(self):
        self.write_to_csv()

    def log_results(self):
        log_execution_data(
            self.conn,
            self.execution_time,
            self.resources,
            self.tree.dataset.get_elements(),
            self.value_param,
            self.result['num_kernels'],
            self.result['num_branches'],
            self.result['tree_depth'],
            self.result['pruned_branches_count'],
            self.filename,
            self.result['optimal_HS'].get_elements(),
            self.kernelStrategy.div_conq_shrink,
            self.kernelStrategy.sw_expand,
            self.kernelStrategy.alpha,
            self.search_strategy.__class__.__name__,
            self.result['opt_hs_value'],
            self.kernelStrategy.div_conq_expand,
            self.kernelStrategy.sw_shrink,
            self.result['opt_hs_card'],
            self.search_strategy.pruner_type,
            self.tree.lowerBound,
            self.tree.upperBound,
            self.result['optimal_solution_found']
        )
        self.conn.close()

    def write_to_csv(self):
        print(self.tree.leaf_nodes)
        num_kernels, num_branches = self.tree.count_kernels_and_branches()
        tree_depth = self.tree.tree_depth()
        # Write the leaf nodes with their BBVALUE, cardinality, and hitting set to a CSV file
        with open(self.output_file, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow([self.execution_time, self.filename, self.value_param, num_kernels, num_branches, tree_depth, self.kernelStrategy.alpha, 'NONE'])
            for bbvalue, leaf in self.tree.leaf_nodes:
                hitting_set = self.tree.get_hitting_set_for_leaf(leaf).get_elements()
                hitting_set_card = len(hitting_set)
                # Convert hitting_set to a string
                hitting_set_str = ', '.join(hitting_set)
                csvwriter.writerow([bbvalue, hitting_set_card, hitting_set_str])

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
            self.result['opt_hs_value'] = int(self.leaf_nodes[0][0])
            self.result['opt_hs_card'] = self.leaf_nodes[0][1]
            self.result['optimal_HS'] = self.tree.get_hitting_set_for_leaf(self.leaf_nodes[self.best_leaf_index][2])
            print(f"\nOptimal Hitting Set: \n{self.result['optimal_HS'].get_elements()}")
            print(f"\nOptimal HS Value: {self.result['opt_hs_value']}, Optimal HS Cardinality: {self.result['opt_hs_card']}")

        self.result['num_kernels'], self.result['num_branches'] = self.tree.count_kernels_and_branches()
        self.result['tree_depth'] = self.tree.tree_depth()
        self.result['pruned_branches_count'] = self.tree.count_pruned_nodes()
        self.best_leaf = self.leaf_nodes[self.best_leaf_index][2]
        self.best_hitting_set = self.tree.get_hitting_set_for_leaf(self.best_leaf)
        self.result['result_value'] = self.best_hitting_set.sum_values()
        self.result['cardinality_value'] = len(self.best_hitting_set.get_elements())

        self.get_values_from_db()

        # Determine if the optimal solution is found based on parameters and pruner type
        optimal_solution_found = False

        if isinstance(self.search_strategy.pruner, LowerPruner):
            print(f"{self.value_param} == 1 and {self.result['result_value']} == {self.result['max_card']}")
            if self.value_param == 1 and self.result['result_value'] == self.result['max_card']:
                optimal_solution_found = True
            elif self.value_param == 2 and self.result['opt_hs_value'] == self.result['max_random_value']:
                optimal_solution_found = True
            elif self.value_param == 3 and self.result['opt_hs_value'] == self.result['max_incon_value']:
                optimal_solution_found = True

        elif isinstance(self.search_strategy.pruner, UpperPruner):
            if self.value_param == 1 and self.result['opt_hs_value'] == self.result['min_card']:
                optimal_solution_found = True
            elif self.value_param == 2 and self.result['opt_hs_value'] == self.result['min_rand_value']:
                optimal_solution_found = True
            elif self.value_param == 3 and self.result['opt_hs_value'] == self.result['min_incon_val']:
                optimal_solution_found = True

        elif isinstance(self.search_strategy.pruner, BestPruner): 
            if self.value_param == 1:
                optimal_solution_found = self.result['opt_hs_value'] == self.result['max_card'] and self.result['opt_hs_card'] == self.result['max_card']
            elif self.value_param == 2:
                optimal_solution_found = self.result['opt_hs_value'] == self.result['max_random_value'] and self.result['opt_hs_card'] == self.result['min_card_max_value_random']
            elif self.value_param == 3:
                print(f"{self.result['opt_hs_value']} == {self.result['max_incon_value']} and {self.result['opt_hs_card']} == {self.result['min_card_max_value_incon']}")
                optimal_solution_found = self.result['opt_hs_value'] == self.result['max_incon_value'] and self.result['opt_hs_card'] == self.result['min_card_max_value_incon']

        self.result['optimal_solution_found'] = optimal_solution_found

    def get_values_from_db(self):
        # Define the SQL query to retrieve the values
        query = """
        SELECT max_random_value, max_incon_value, min_random_value, min_incon_value, max_cardinality, min_cardinality, card_max_random, card_max_incon, card_min_random, card_min_incon, min_card_max_value_random, min_card_max_value_incon
        FROM EXE_RESULTS.OPTIMAL
        WHERE filename = %s
        """

        try:
            # Create a cursor object
            cursor = self.conn.cursor()
            
            # Execute the query
            cursor.execute(query, (self.filename,))
            
            # Fetch the result
            row = cursor.fetchone()
            
            if row:
                # Assign the fetched values to the corresponding keys in self.result
                self.result['max_random_value'] = row[0]
                self.result['max_incon_value'] = row[1]
                self.result['min_rand_value'] = row[2]
                self.result['min_incon_val'] = row[3]
                self.result['max_card'] = row[4]
                self.result['min_card'] = row[5]
                self.result['card_max_random'] = row[6]
                self.result['card_max_incon'] = row[7]
                self.result['card_min_random'] = row[8]
                self.result['card_min_incon'] = row[9]
                self.result['min_card_max_value_random'] = row[10]
                self.result['min_card_max_value_incon'] = row[11]
            else:
                raise ValueError("No data found in the table EXE_RESULTS.OPTIMAL")
            
        except Exception as e:
            print(f"An error occurred while fetching data from the database: {e}")
        finally:
            # Close the cursor
            cursor.close()
