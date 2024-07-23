import csv
import logging
from src.database.database import log_execution_data
from src.structs.logger import setup_logging
from src.structs.dataset import get_random_values,get_incon_values

# Set up logging for this module
setup_logging()

# Get the logger for this module
str_logger = logging.getLogger(__name__)

class ResultCalculator:
    def __init__(self, tree, pruner):
        self.random_values = get_random_values()
        self.incon_values = get_incon_values()
        self.tree = tree
        self.pruner = pruner
        self.leaf_nodes = []
        self.create_leaf_node_dict()
        self.max_vals = {}
        self.min_vals = {}

    def create_leaf_node_dict(self):
        # Create a list of tuples containing (BBVALUE, hitting_set, LEAF_NODE)
        self.leaf_nodes = [(bbvalue, len(self.tree.get_hitting_set_for_leaf(leaf).get_elements()), leaf) for bbvalue, leaf in self.tree.leaf_nodes]
        self.sort_leaf_nodes()

        #HS = self.tree.get_hitting_set_for_leaf(leaf)
        #random_HS_value = sum(self.random_values[element] for element in HS.get_elements())
        #incon_HS_value = sum(self.incon_values[element] for element in HS.get_elements())
            
            #leafs_random[leaf] = random_HS_value
            #leafs_incon[leaf] = incon_HS_value

    def sort_leaf_nodes(self):
        # Sort the list based on BBVALUE (descending) and then Cardinality (ascending)
        self.leaf_nodes = sorted(self.leaf_nodes, key=lambda x: (-x[0], -x[1])) 

    def print_results(self):
        self.calculate()
        print()
        for bbvalue, hitting_set, leaf in self.leaf_nodes:
            print(f"{bbvalue}, {hitting_set}, {self.tree.get_hitting_set_for_leaf(leaf).get_elements()}")

        self.max_vals['max_card_card'] = max(self.leaf_nodes, key=lambda x: x[1])[1]
        self.max_vals['max_val_rand'] = max(self.leaf_nodes, key=lambda x: x[1])[1]
        #self.max_vals[]
        #self.max_vals[]
        #self.max_vals[]

        min_card = min(self.leaf_nodes, key=lambda x: x[1])[1]

        #print(max_card, min_card)
        
        """
        print(f"\nExecution time: {execution_time}s, Memory Used: {resources_used}, Alpha: {args.alpha}, Strategy: {args.sp}, Search Strategy: {args.ss}, Kernels: {num_kernels}, Branches: {num_branches}, Tree depth: {tree_depth}, Pruned branches: {pruned_branches_count}, Boundary: {boundary}, Pruner: {args.pruner},Shrink Sliding Window size: {args.shrink_sw_size}, Expand Sliding Window size: {args.expand_sw_size}, Shrink Divide and Conquer: {args.shrink_div_conq}, Expand Divide and Conquer: {args.expand_div_conq}, Lowest Cardinality: {lowest_card}, Max Value Random: {best_random}, Max Value Incon: {best_incon}, Optimal Random Cardinality: {best_random_card}, Optimal Incon Cardinality: {best_incon_card}, Min Value Random: {min_val_rand}, Min Value Incon: {min_val_incon}")
        print(f"\nResult: \nOptimal hitting set: {optimal_hitting_set} with: \n- value: {optimal_value} \n- Optimal Value: {optimal_value}, \n- Cardinality: {optimal_cardinality}")
        print(f"\nVerification parameters: ")
        print(f"\nMax values: \nValue: {max_card_value}, {max_random_value}, {max_incon_val} \nCardinality: ")
        print(f"\nMin values: \Value: {min_card}, {min_rand_value}, {min_incon_val}")
        
        if self.pruner == 'NONE':
            print(f"\nBest: \nValue, Cardinality: {best_card}, {best_random}, {best_incon}")
        pass
        """

    def print_results_to_file(self, result_path="Results/All_hitting_sets.csv", execution_time = 0, alpha = 'alpha', file_name='xx'):
        self.write_to_csv(result_path, execution_time, alpha, file_name)

    def log_results(self, conn):
        log_execution_data()
        conn.close()

    def write_to_csv(self, filename, execution_time, alpha, file_name):
        num_kernels, num_branches = self.tree.count_kernels_and_branches()
        tree_depth = self.tree.tree_depth()
        strategy_param=2
        # Write the leaf nodes with their BBVALUE, cardinality, and hitting set to a CSV file
        with open(filename, 'a', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow([execution_time, file_name, strategy_param, num_kernels, num_branches, tree_depth, alpha, 'NONE'])
            for bbvalue, cardinality, leaf in self.leaf_nodes:
                hitting_set = self.tree.get_hitting_set_for_leaf(leaf).get_elements()
                # Convert hitting_set to a string
                hitting_set_str = ', '.join(hitting_set)
                csvwriter.writerow([bbvalue, cardinality, hitting_set_str])

        """
        file_repair = result_path
        if optimal_hitting_set:
            repaired_dataset = dataset.clone()
            for element in optimal_hitting_set:
                repaired_dataset.remove_element(element)
            repaired_dataset.to_file(file_repair)
            cnf_converter = CNFConverter(verbose=False)
            cnf_converter.convert_to_cnf(file_repair, file_repair)
            if repaired_dataset.get_elements():
                dataset_elements = repaired_dataset.get_elements()
            else:
                main_logger("Dataset empty.")
                dataset_elements = "Empty."
        else:
            dataset_elements = "No solution found."

        with open(file_repair, 'a') as file:
            file.write(f"\nFile: {args.filepath}, DataSet: {dataset}")
            file.write(f"\nBranch and Bound strategy: {args.pruner} with Search strategy: {args.ss} and Weight Assignment: {args.sp}")
            file.write(f"\nExecution time: {execution_time}s, Memory Used: {resources_used}, Strategy: {args.sp}, Search Strategy: {args.ss}, Kernels: {num_kernels}, Branches: {num_branches}, Tree depth: {tree_depth}, Pruned branches: {pruned_branches_count}, Boundary: {boundary}, Pruner: {args.pruner},Shrink Sliding Window size: {args.shrink_sw_size}, Expand Sliding Window size: {args.expand_sw_size}, Shrink Divide and Conquer: {args.shrink_div_conq}, Expand Divide and Conquer: {args.expand_div_conq}, Lowest Cardinality: {lowest_card}, Optimal Value Random: {best_random}, Optimal Value Incon: {best_incon}")
            file.write(f"\nOptimal hitting set: {optimal_hitting_set} with value: {optimal_value}, Alpha: {args.alpha}, Optimal Value: {optimal_value}")
            file.write(f"\nOptimal solution: {optimal_hitting_set}")
            file.write(f"\nOptimal value: {optimal_value}, Optimal cardinality: {optimal_cardinality}")
            file.write(f"\nRepaired dataset: {dataset_elements}\n")

            file.write(f"\nMax random value: {best_random} with card: {best_random_card}")
            file.write(f"\nMax incon value: {best_incon}\n")

            file.write(f"\nMin random value: {min_val_rand} with card: {min_card_rand}")
            file.write(f"\nMin incon value: {min_val_incon}\n")

            file.write(f"\nAll explored hitting sets: \n(Value, Cardinality, Hitting set)\n")
            # Print the sorted list
            for bbvalue, cardinality, leaf in self.leaf_nodes:
                print(f"{bbvalue}, {cardinality}, {leaf}")
        

        data_logger.debug(f"\nExecution time: {execution_time}s, Memory Used: {resources_used}, Alpha: {args.alpha}, Strategy: {args.sp}, Search Strategy: {args.ss}, Kernels: {num_kernels}, Branches: {num_branches}, Tree depth: {tree_depth}, Pruned branches: {pruned_branches_count}, Boundary: {boundary}, Pruner: {args.pruner},Shrink Sliding Window size: {args.shrink_sw_size}, Expand Sliding Window size: {args.expand_sw_size}, Shrink Divide and Conquer: {args.shrink_div_conq}, Expand Divide and Conquer: {args.expand_div_conq}, Lowest Cardinality: {lowest_card}, Max Value Random: {best_random}, Max Value Incon: {best_incon}, Optimal Random Cardinality: {best_random_card}, Optimal Incon Cardinality: {best_incon_card}, Min Value Random: {min_val_rand}, Min Value Incon: {min_val_incon}")
        data_logger.debug(f"\nResult: \nOptimal hitting set: {optimal_hitting_set} with: \n- value: {optimal_value} \n- Optimal Value: {optimal_value}, \n- Cardinality: {optimal_cardinality}")

        print(f"\nRepaired dataset in CNF saved to {file_repair}")
        """
        pass

    def calculate(self):
        if self.pruner == 'NONE':
            self.calc_complete_tree_values()
        elif self.pruner == 'UPPER':
            self.calc_max_results()
        elif self.pruner == 'LOWER':
            self.calc_min_results()
        elif self.pruner == 'BEST':
            self.calc_best_results()
        else:
            pass

    def calc_complete_tree_values(self):
        self.calc_max_results()
        self.calc_min_results()

    def calc_max_results(self):
        max_card = max(self.leaf_nodes, key=lambda x: x[1])[1]
        print(max_card)
        
        """
        self.max_val_random =
        self.max_val_incon = 
        self.max_card_random = 
        self.max_card_incon =

        self.max_vals[self.pruner] = max_card

                    min_val_rand, min_card_rand, min_val_incon, min_card_incon = calc_best_HS_val(hitting_set_tree, -1)
                else:
                    max_random_val, best_random_card, best_incon, best_incon_card, lowest_card, min_val_rand, min_card_rand, min_val_incon, min_card_incon = None, None, None, None, None, None, None, None, None
        for _,leaf in HSTree.leaf_nodes:
            HS = HSTree.get_hitting_set_for_leaf(leaf)
            random_HS_value = sum(self.random_values[element] for element in HS.get_elements())
            incon_HS_value = sum(self.incon_values[element] for element in HS.get_elements())
            
            self.leafs_random[leaf] = random_HS_value
            self.leafs_incon[leaf] = incon_HS_value
        
        if index == 0:
            # Find the maximum values
            best_random_leaf = max(leafs_random, key=leafs_random.get)
            best_random_card = len(HSTree.get_hitting_set_for_leaf(best_random_leaf).get_elements())

            best_incon_leaf = max(leafs_incon, key=leafs_incon.get)
            best_incon_card = len(HSTree.get_hitting_set_for_leaf(best_incon_leaf).get_elements())  
        
        if index == -1:
            best_random_leaf = min(leafs_random, key=leafs_random.get)
            best_random_card = len(HSTree.get_hitting_set_for_leaf(best_random_leaf).get_elements())
            best_incon_leaf = min(leafs_incon, key=leafs_incon.get)
            best_incon_card = len(HSTree.get_hitting_set_for_leaf(best_incon_leaf).get_elements())  

        best_random = leafs_random[best_random_leaf]
        best_incon = leafs_incon[best_incon_leaf]

        return best_random, best_random_card, best_incon, best_incon_card
        """
        pass

    def calc_min_results(self):

        pass

    def calc_best_reults(self):
        pass

    def calculate_measures(self):
        """
        if self.hitting_set_tree:
            optimal_hitting_set = hitting_set_tree.get_hitting_set_for_optimal_solution(best_index)
            if optimal_hitting_set is not None:
                num_kernels, num_branches = hitting_set_tree.count_kernels_and_branches()
                pruned_branches_count = hitting_set_tree.count_pruned_nodes()
                tree_depth = hitting_set_tree.tree_depth()
                boundary = pruner.boundary
                dataset_log = dataset.get_elements()
                optimal_hitting_set = hitting_set_tree.get_hitting_set_for_optimal_solution(best_index).get_elements()
                optimal_cardinality = len(optimal_hitting_set) if optimal_hitting_set else 0
                optimal_hs = hitting_set_tree.get_hitting_set_for_optimal_solution(best_index)
                optimal_value = optimal_hs.sum_values() if optimal_hitting_set else None

            else:
                num_kernels, num_branches, pruned_branches_count = 0, 0, 0
                tree_depth = boundary = None
                optimal_hitting_set = None
                optimal_value = None
                dataset_log = []
                optimal_cardinality = 0
                best_random, best_random_card, best_incon, best_incon_card, lowest_card, min_val_rand, min_card_rand, min_val_incon, min_card_incon = None, None, None, None, None, None, None, None, None
        
        resources_used = f"{resource.getrusage(resource.RUSAGE_SELF).ru_maxrss} KB"
        """
        pass
        
 
    



        




