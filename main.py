import argparse
import sys
import time
import resource
import signal
import logging
from src.CNFconverter.parse import CNFConverter
from src.pruner.basepruner import BasePruner
from src.search.hybrid import HYS
from src.search.priority import PBS
from src.search.bfs import BFS
from src.search.dfs import DFS
from src.solver.kernelsolver import KernelSolver
from src.kernels.expandshrink import ExpandShrink
from src.structs.dataset import initialize_dataset, get_incon_values, get_random_values
from src.database.database import create_ssh_tunnel_and_connect, log_execution_data
from src.structs.logger import setup_logging
from src.pruner.best import BestPruner
from src.tree.brancher import Brancher
from src.pruner.lower import LowerPruner
from src.pruner.upper import UpperPruner
from src.tree.hittingsettree import HittingSetTree

# Set up argument parser
parser = argparse.ArgumentParser(description='Run the kernelization process with optional database main_logger.')
parser.add_argument('filepath', type=str, help='Path to the dataset file')
parser.add_argument('--sp', type=int, choices=range(0, 4), required=True, help='Strategy parameter for value assignment being used for Branch-and-Bound: 1: Cardinality, 2: Random Values, 3: Inconsistency Values)')
parser.add_argument('--ss', '--search-strategy', type=str, default='P', choices=['BFS', 'DFS', 'HYS', 'PBS'], required=True, help='Search strategy to use: BFS, DFS, Hybrid, Priority')
parser.add_argument('--alpha', type=str, required=True, help='A string value to be used as alpha')
parser.add_argument('--pruner', type=str, default='NONE', choices=['UPPER', 'LOWER', 'BEST', 'NONE'], help='Pruning/Boundary strategy to use: UPPER, LOWER, BEST, NONE')

# Expand group with mutually exclusive options
expand_group = parser.add_argument_group('expand')
expand_me_group = expand_group.add_mutually_exclusive_group(required=False)
expand_me_group.add_argument('--expand-div-conq', action='store_true', default=False, help='Activate the divide and conquer technique for expand')
expand_me_group.add_argument('--expand-sw-size', type=int, default=1, help='Window size for the sliding-window technique during expand')

# Shrink group with mutually exclusive options
shrink_group = parser.add_argument_group('shrink')
shrink_me_group = shrink_group.add_mutually_exclusive_group(required=False)
shrink_me_group.add_argument('--shrink-div-conq', action='store_true', default=False, help='Activate the divide and conquer technique for shrink')
shrink_me_group.add_argument('--shrink-sw-size', type=int, default=1, help='Window size for the sliding-window technique during shrink')

parser.add_argument('-res-db', action='store_true', help='Save results to database')
parser.add_argument('-no-log', action='store_true', help='Disable logging')
parser.add_argument('-path-db', action='store_true', help='Indicate that the dataset should be called from the database')

args = parser.parse_args()

# Configure logging
setup_logging(disable_logging=args.no_log)

# Get the logger for main
main_logger = logging.getLogger('main')

# Function to handle timeout
def timeout_handler(signum, frame):
    raise TimeoutError("Program exceeded the specified time limit.")

def calc_best_HS_val(HSTree, index):
    random_values = get_random_values()
    incon_values = get_incon_values()
    leafs_random = {}
    leafs_incon = {}

    for _,leaf in HSTree.leaf_nodes:
        HS = HSTree.get_hitting_set_for_leaf(leaf)
        random_HS_value = sum(random_values[element] for element in HS.get_elements())
        incon_HS_value = sum(incon_values[element] for element in HS.get_elements())
        
        leafs_random[leaf] = random_HS_value
        leafs_incon[leaf] = incon_HS_value
    
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

def get_ranked_node(HSTree, index):
    sorted_leaf_nodes = sorted(
        HSTree.leaf_nodes,
        key=lambda item: len(hitting_set_tree.get_hitting_set_for_leaf(item[1]).get_elements())
    )
    return sorted_leaf_nodes[index]

if __name__ == "__main__":
    if args.no_log:
        logging.disable(logging.CRITICAL)
    
    main_logger.debug("Starting main script")
    # Prepare for timeout
    signal.signal(signal.SIGALRM, timeout_handler)
    timeout_duration = 1800  # 1800 seconds or 30 minutes
    signal.alarm(timeout_duration)  # Start the timer

    try:
        conn = create_ssh_tunnel_and_connect()
        start_time = time.time()
        dataset = initialize_dataset(conn, input_file_path=args.filepath, strategy_param=args.sp, db=args.path_db)
        
        if dataset.size() == 0:
            main_logger.error("No Dataset found, please use a dataset from DB or change code to use files.")
            sys.exit(1)

        if not 1 <= args.shrink_sw_size <= dataset.size() or not 1 <= args.expand_sw_size <= dataset.size():
            adjusted_shrink_sw_size = min(args.shrink_sw_size, dataset.size())
            adjusted_expand_sw_size = min(args.expand_sw_size, dataset.size())
            main_logger.warning(f"--shrink-sw-size/--expand-sw-size must be between 1 and the length of the dataset ({dataset.size()}). Adjusting shrink_sw_size to {adjusted_shrink_sw_size} and expand_sw_size to {adjusted_expand_sw_size}.")
            args.shrink_sw_size = adjusted_shrink_sw_size
            args.expand_sw_size = adjusted_expand_sw_size

        if args.alpha:
            main_logger.info(f"Alpha: {args.alpha}")

        hitting_set_tree = None
        kernel_strategy = ExpandShrink(args.expand_sw_size, args.shrink_sw_size, args.shrink_div_conq, args.expand_div_conq)

        if dataset.sum_values() == 0 and args.sp == 3:
                print(f"DataSet Inconsistency Weights == {dataset.sum_values()}")
                main_logger.error(f"DataSet Inconsistency Values == {dataset.sum_values()}")
                sys.exit(1)

        # Initialize the HittingSetTree
        hitting_set_tree = HittingSetTree(dataset)
        main_logger.debug("Tree initialized.")

        brancher = Brancher(dataset, hitting_set_tree)
        main_logger.debug("Brancher initialized.")

        best_index = 0 # Index to peak at hitting_set_collection
        # Initialize the appropriate pruner based on user input
        if args.pruner == 'UPPER':
            pruner = UpperPruner(hitting_set_tree, args.sp, args.alpha, args.shrink_sw_size, args.expand_sw_size)
        elif args.pruner == 'LOWER':
            best_index = -1 # To get leaf with least priority 
            pruner = LowerPruner(hitting_set_tree, args.sp)
        elif args.pruner == 'BEST':
            pruner = BestPruner(hitting_set_tree, args.sp)
        else:  # Default to BasePruner for no pruning
            pruner = BasePruner(hitting_set_tree, args.sp)
        
        main_logger.debug("Pruner initialized.")

        if args.ss == 'BFS':
            search_strategy = BFS(kernel_strategy, dataset, brancher, pruner, args.alpha, args.sp)
        elif args.ss == 'DFS':
            search_strategy = DFS(kernel_strategy, dataset, brancher, pruner, args.alpha, args.sp)
        elif args.ss == 'HYS':
            search_strategy = HYS(kernel_strategy, dataset, brancher, pruner, args.alpha, args.sp)
        elif args.ss == 'PBS':
            search_strategy = PBS(kernel_strategy, dataset, brancher, pruner, args.alpha, args.sp)
        else:
            main_logger.error("Invalid search strategy")
            sys.exit(1)

        main_logger.debug("Search initialized.")

        hitting_set_tree = KernelSolver(search_strategy).solve()

    except TimeoutError as e:
        main_logger.error(f"Timeout occurred: {e}")
        execution_time = time.time() - start_time
        resources_used = f"{resource.getrusage(resource.RUSAGE_SELF).ru_maxrss} KB"
        if args.res_db and conn is not None:
            log_execution_data(conn, execution_time, resources_used, dataset.get_elements(), args.sp, None, None, None, None, args.filepath, None, None, args.shrink_div_conq, args.expand_sw_size, args.alpha, args.ss, None, args.expand_div_conq, args.shrink_sw_size, None, args.pruner, None,None,None,None,None,None)
            conn.close()
        sys.exit(1)
    except Exception as e:
        main_logger.error(f"An error occurred: {e}")
        sys.exit(1)
    finally:
        signal.alarm(0)  # Cancel the timeout

    execution_time = time.time() - start_time
    if hitting_set_tree:
        optimal_hitting_set = hitting_set_tree.get_hitting_set_for_optimal_solution(best_index)
        if optimal_hitting_set is not None:
            num_kernels, num_branches = hitting_set_tree.count_kernels_and_branches()
            pruned_branches_count = hitting_set_tree.count_pruned_nodes()
            tree_depth = hitting_set_tree.tree_depth()
            boundary = pruner.boundary
            optimal_hitting_set = hitting_set_tree.get_hitting_set_for_optimal_solution(best_index).get_elements()
            optimal_cardinality = len(optimal_hitting_set) if optimal_hitting_set else 0
            optimal_hs = hitting_set_tree.get_hitting_set_for_optimal_solution(best_index)
            optimal_value = optimal_hs.sum_values() if optimal_hitting_set else None
            if args.pruner == 'NONE':
                best_random, best_random_card, best_incon, best_incon_card = calc_best_HS_val(hitting_set_tree, 0)
                _,lowest_leaf = get_ranked_node(hitting_set_tree, best_index)
                lowest_card = len(hitting_set_tree.get_hitting_set_for_leaf(lowest_leaf).get_elements()) 
                min_val_rand, min_card_rand, min_val_incon, min_card_incon = calc_best_HS_val(hitting_set_tree, -1)
            else:
                best_random, best_random_card, best_incon, best_incon_card, lowest_card, min_val_rand, min_card_rand, min_val_incon, min_card_incon = None, None, None, None, None, None, None, None, None

        else:
            num_kernels, num_branches, pruned_branches_count = 0, 0, 0
            tree_depth = boundary = None
            optimal_hitting_set = None
            optimal_value = None
            optimal_cardinality = 0
            best_random, best_random_card, best_incon, best_incon_card, lowest_card, min_val_rand, min_card_rand, min_val_incon, min_card_incon = None, None, None, None, None, None, None, None, None

    resources_used = f"{resource.getrusage(resource.RUSAGE_SELF).ru_maxrss} KB"

    print(f"Execution time: {execution_time}s, Memory Used: {resources_used}, Strategy: {args.sp}, Search Strategy: {args.ss}, Kernels: {num_kernels}, Branches: {num_branches}, Tree depth: {tree_depth}, Pruned branches: {pruned_branches_count}, Boundary: {boundary}, Pruner: {args.pruner},Shrink Sliding Window size: {args.shrink_sw_size}, Expand Sliding Window size: {args.expand_sw_size}, Shrink Divide and Conquer: {args.shrink_div_conq}, Expand Divide and Conquer: {args.expand_div_conq}, Lowest Cardinality: {lowest_card}, Max Value Random: {best_random}, Max Value Incon: {best_incon}, Optimal Random Cardinality: {best_random_card}, Optimal Incon Cardinality: {best_incon_card}, Min Value Random: {min_val_rand}, Min Value Incon: {min_val_incon}")
    print(f"Optimal hitting set: {optimal_hitting_set} with value: {optimal_value}, Alpha: {args.alpha}, Optimal Value: {optimal_value}, Optimal Cardinality: {optimal_cardinality}")

    if args.res_db:
        if conn is not None:
            log_execution_data(conn, execution_time, resources_used, dataset.get_elements(), args.sp, num_kernels, num_branches, tree_depth, pruned_branches_count, args.filepath, boundary, optimal_hitting_set.get_elements(), args.shrink_div_conq, args.expand_sw_size, args.alpha, args.ss, optimal_value, args.expand_div_conq, args.shrink_sw_size, optimal_cardinality, args.pruner, lowest_card, best_random, best_incon, best_random_card, best_incon_card,min_val_rand,min_val_incon)
            conn.close()
        else:
            print("Connection to MySQL database failed")

    main_logger.debug(f"Execution time: {execution_time}s, Memory Used: {resources_used}, Strategy: {args.sp}, Search Strategy: {args.ss}, Kernels: {num_kernels}, Branches: {num_branches}, Tree depth: {tree_depth}, Pruned branches: {pruned_branches_count}, Boundary: {boundary}, Pruner: {args.pruner},Shrink Sliding Window size: {args.shrink_sw_size}, Expand Sliding Window size: {args.expand_sw_size}, Shrink Divide and Conquer: {args.shrink_div_conq}, Expand Divide and Conquer: {args.expand_div_conq}, Lowest Cardinality: {lowest_card}, Max Value Random: {best_random}, Max Value Incon: {best_incon}, Optimal Random Cardinality: {best_random_card}, Optimal Incon Cardinality: {best_incon_card}, Min Value Random: {min_val_rand}, Min Value Incon: {min_val_incon}")
    main_logger.debug(f"Optimal hitting set: {optimal_hitting_set} with value: {optimal_value}, Alpha: {args.alpha}, Optimal Value: {optimal_value}, Cardinality: {optimal_cardinality}")

    file_repair = "Results/Results.out"
    repaired_dataset = dataset.clone()
    if optimal_hitting_set:
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
        repaired_dataset.to_file(file_repair)
        dataset_elements = "No solution found."

    with open(file_repair, 'a') as file:
        file.write(f"\nFile: {args.filepath}, DataSet Value: {dataset.sum_values()}")
        file.write(f"\nBranch and Bound strategy: {args.pruner} with Search strategy: {args.ss} and Weight Assignment: {args.sp}")
        file.write(f"\nExecution time: {execution_time}s, Memory Used: {resources_used}, Strategy: {args.sp}, Search Strategy: {args.ss}, Kernels: {num_kernels}, Branches: {num_branches}, Tree depth: {tree_depth}, Pruned branches: {pruned_branches_count}, Boundary: {boundary}, Pruner: {args.pruner},Shrink Sliding Window size: {args.shrink_sw_size}, Expand Sliding Window size: {args.expand_sw_size}, Shrink Divide and Conquer: {args.shrink_div_conq}, Expand Divide and Conquer: {args.expand_div_conq}, Lowest Cardinality: {lowest_card}, Optimal Value Random: {best_random}, Optimal Value Incon: {best_incon}")
        file.write(f"\nOptimal hitting set: {optimal_hitting_set} with value: {optimal_value}, Alpha: {args.alpha}, Optimal Value: {optimal_value}")
        file.write(f"\nOptimal solution: {optimal_hitting_set}")
        file.write(f"\nOptimal value: {optimal_value}, Optimal cardinality: {optimal_cardinality}")
        file.write(f"\nRepaired dataset: {dataset_elements}\n")

        file.write(f"\nMax random value: {best_random} with card: {best_random_card}")
        file.write(f"\nMax incon value: {best_incon} with card: {best_incon_card}\n")

        file.write(f"\nMin random value: {min_val_rand} with card: {min_card_rand}")
        file.write(f"\nMin incon value: {min_val_incon} with card: {min_card_incon}\n")

        file.write(f"\nAll explored hitting sets: \n(Value, Cardinality, Hitting set)\n")
    
    hitting_set_tree.print_all_hitting_sets_to_file(file_repair)

    print(f"Repaired dataset in CNF saved to {file_repair}")