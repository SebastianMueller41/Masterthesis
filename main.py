import argparse
import os
import sys
import time
import resource
import signal
import logging
from src.CNFconverter.parse import CNFConverter
from src.search.hybrid import HybridSearch
from src.search.priority import PrioritySearch
from src.search.bfs import BFS
from src.search.dfs import DFS
from src.search.verification import VerificationSearch
from src.solver.kernelsolver import KernelSolver
from src.kernels.expandshrink import ExpandShrink
from src.structs.dataset import DataSet
from src.database.database import create_ssh_tunnel_and_connect, log_execution_data

# Configure the root logger
logging.basicConfig(
    filename='log/app.log',  # Log file name
    filemode='w',  # Overwrite the log file on each run
    level=logging.DEBUG,  # Set the logging level
    format='%(asctime)s %(levelname)s:%(message)s'  # Log format
)

# Set up argument parser
parser = argparse.ArgumentParser(description='Run the kernelization process with optional database logging.')
parser.add_argument('filepath', type=str, help='Path to the dataset file')
parser.add_argument('--sp', type=int, choices=range(0, 4), required=True, help='Strategy parameter value (0-3)')
parser.add_argument('--ss', '--search-strategy', type=str, default='P', choices=['BFS', 'DFS', 'H', 'P', 'V'], required=True, help='Search strategy to use: BFS, DFS, Hybrid, Priority')
parser.add_argument('--alpha', type=str, required=True, help='A string value to be used as alpha')

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


# Function to handle timeout
def timeout_handler(signum, frame):
    raise TimeoutError("Program exceeded the specified time limit.")

if __name__ == "__main__":
    if args.no_log:
        logging.disable(logging.CRITICAL)
    
    logging.debug("Starting main script")
    # Prepare for timeout
    signal.signal(signal.SIGALRM, timeout_handler)
    timeout_duration = 1800  # 1800 seconds or 30 minutes
    signal.alarm(timeout_duration)  # Start the timer

    try:
        conn = create_ssh_tunnel_and_connect()
        start_time = time.time()
        dataset = DataSet(conn, input_file_path=args.filepath, strategy_param=args.sp, db=args.path_db)

        if dataset.size() == 0:
            logging.error("No Dataset found, please use a dataset from DB or change code to use files.")
            sys.exit(1)

        if not 1 <= args.shrink_sw_size <= dataset.size() or not 1 <= args.expand_sw_size <= dataset.size():
            adjusted_shrink_sw_size = min(args.shrink_sw_size, dataset.size())
            adjusted_expand_sw_size = min(args.expand_sw_size, dataset.size())
            logging.warning(f"--shrink-sw-size/--expand-sw-size must be between 1 and the length of the dataset ({dataset.size()}). Adjusting shrink_sw_size to {adjusted_shrink_sw_size} and expand_sw_size to {adjusted_expand_sw_size}.")
            args.shrink_sw_size = adjusted_shrink_sw_size
            args.expand_sw_size = adjusted_expand_sw_size

        if args.alpha:
            logging.info(f"Alpha: {args.alpha}")

        hitting_set_tree = None
        kernel_strategy = ExpandShrink(args.expand_sw_size, args.shrink_sw_size, args.shrink_div_conq, args.expand_div_conq)

        if args.ss == 'BFS':
            search_strategy = BFS(kernel_strategy, dataset, args.alpha, args.sp)
        elif args.ss == 'DFS':
            search_strategy = DFS(kernel_strategy, dataset, args.alpha, args.sp)
        elif args.ss == 'H':
            search_strategy = HybridSearch(kernel_strategy, dataset, args.alpha, args.sp)
        elif args.ss == 'P':
            search_strategy = PrioritySearch(kernel_strategy, dataset, args.alpha, args.sp)
        elif args.ss == 'V':
            search_strategy = VerificationSearch(kernel_strategy, dataset, args.alpha, args.sp)
        else:
            logging.error("Invalid search strategy")
            sys.exit(1)

        hitting_set_tree = KernelSolver(search_strategy).solve()

    except TimeoutError as e:
        logging.error(f"Timeout occurred: {e}")
        execution_time = time.time() - start_time
        resources_used = f"{resource.getrusage(resource.RUSAGE_SELF).ru_maxrss} KB"
        if args.res_db and conn is not None:
            log_execution_data(conn, execution_time, resources_used, dataset.get_elements(), args.sp, None, None, None, None, None, args.filepath, None, None, args.shrink_div_conq, args.expand_sw_size, args.alpha, args.ss, None, args.expand_div_conq, args.shrink_sw_size, None)
            conn.close()
        sys.exit(1)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        sys.exit(1)
    finally:
        signal.alarm(0)  # Cancel the timeout

    execution_time = time.time() - start_time
    if hitting_set_tree:
        num_kernels, num_branches = hitting_set_tree.count_kernels_and_branches()
        pruned_branches_count = hitting_set_tree.count_pruned_nodes()
        tree_depth = hitting_set_tree.tree_depth()
        boundary = hitting_set_tree.boundary
        optimal_hitting_set = hitting_set_tree.get_hitting_set_for_optimal_solution()
        optimal_value = optimal_hitting_set.sum_values() if optimal_hitting_set else None
    else:
        num_kernels = num_branches = pruned_branches_count = 0
        tree_depth = boundary = None
        optimal_hitting_set = None
        optimal_value = None

    resources_used = f"{resource.getrusage(resource.RUSAGE_SELF).ru_maxrss} KB"

    print(f"Execution time: {execution_time}s, Memory Used: {resources_used}, Strategy: {args.sp}, Search Strategy: {args.ss}, Kernels: {num_kernels}, Branches: {num_branches}, Tree depth: {tree_depth}, Pruned branches: {pruned_branches_count}, Boundary: {boundary},Shrink Sliding Window size: {args.shrink_sw_size}, Expand Sliding Window size: {args.expand_sw_size}, Shrink Divide and Conquer: {args.shrink_div_conq}, Expand Divide and Conquer: {args.expand_div_conq}")
    print(f"Optimal hitting set: {optimal_hitting_set.get_elements()} with value: {optimal_value}, Alpha: {args.alpha}, Optimal Value: {optimal_value}")

    if args.res_db:
        if conn is not None:
            log_execution_data(conn, execution_time, resources_used, dataset.get_elements(), args.sp, num_kernels, num_branches, tree_depth, pruned_branches_count, args.filepath, boundary, optimal_hitting_set.get_elements(), args.shrink_div_conq, args.expand_sw_size, args.alpha, args.ss, optimal_value, args.expand_div_conq, args.shrink_sw_size)
            conn.close()
        else:
            print("Connection to MySQL database failed")

    logging.info(f"Execution time: {execution_time}s, Memory Used: {resources_used}, Strategy: {args.sp}, Search Strategy: {args.ss}, Kernels: {num_kernels}, Branches: {num_branches}, Tree depth: {tree_depth}, Pruned branches: {pruned_branches_count}, Boundary: {boundary},Shrink Sliding Window size: {args.shrink_sw_size}, Expand Sliding Window size: {args.expand_sw_size}, Shrink Divide and Conquer: {args.shrink_div_conq}, Expand Divide and Conquer: {args.expand_div_conq}")
    logging.info(f"Optimal hitting set: {optimal_hitting_set.get_elements()} with value: {optimal_value}, Alpha: {args.alpha}, Optimal Value: {optimal_value}")

    file_repair = "log/Results.out"

    if optimal_hitting_set is not None:
        for element in optimal_hitting_set.get_elements():
            dataset.remove_element(element)
        dataset.to_file(file_repair)
        cnf_converter = CNFConverter(verbose=False)
        cnf_converter.convert_to_cnf(file_repair, file_repair)
        if dataset.get_elements():
            dataset_elements = dataset.get_elements()
        else:
            dataset_elements = "Empty."
    else:
        dataset.to_file(file_repair)
        dataset_elements = "No solution found."

    with open(file_repair, 'a') as file:
        file.write(f"\nFile: {args.filepath}")
        file.write(f"\nOptimal solution: {optimal_hitting_set.get_elements()}")
        file.write(f"\nOptimal value: {optimal_value}")
        file.write(f"\nRepaired dataset: {dataset_elements}\n")
        file.write(f"\nAll explored hitting sets: \n(Path value, hitting set)\n")
    
    hitting_set_tree.print_all_hitting_sets_to_file(file_repair)

    print(f"Repaired dataset in CNF saved to {file_repair}")
