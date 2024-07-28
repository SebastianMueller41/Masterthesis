import argparse
import sys
import time
import resource
import signal
import logging
from src.search.hybrid import HYS
from src.search.bfs import BFS
from src.search.dfs import DFS
from src.search.priority import PBS
from src.search.search import Search
from src.search.strategy import Strategy
from src.solver.kernelsolver import KernelSolver
from src.kernels.expandshrink import ExpandShrink
from src.structs.dataset import DataSet, initialize_dataset
from src.structs.results import ResultCalculator
from src.database.database import create_ssh_tunnel_and_connect, log_execution_data
from src.structs.logger import setup_logging
from src.tree.hittingsettree import HittingSetTree

# Set up argument parser
parser = argparse.ArgumentParser(description='Run the kernelization process with optional database main_logger.')
parser.add_argument('filepath', type=str, help='Path to the dataset file')
parser.add_argument('--vp', type=int, choices=range(0, 4), required=True, help='Value parameter for value assignment being used for Branch-and-Bound: 1: Cardinality, 2: Random Values, 3: Inconsistency Values)')
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
main_logger = logging.getLogger(__name__)

# Function to handle timeout
def timeout_handler(signum, frame):
    raise TimeoutError("Program exceeded the specified time limit.")

if __name__ == "__main__":
    if args.no_log:
        logging.disable(logging.CRITICAL)
    
    main_logger.debug("Starting main script")
    # Prepare for timeout
    signal.signal(signal.SIGALRM, timeout_handler)
    timeout_duration = 1800  # 1800 seconds or 30 minutes
    signal.alarm(timeout_duration)  # Start the timer

    if args.path_db:
        conn = create_ssh_tunnel_and_connect()
    else:
        conn = False

    try:
       
        dataset = initialize_dataset(conn, input_file_path=args.filepath, strategy_param=args.vp, db=args.path_db)
        start_time = time.time()
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
        kernel_strategy = ExpandShrink(args.expand_sw_size, args.shrink_sw_size, args.shrink_div_conq, args.expand_div_conq, args.alpha)

        if dataset.sum_values() == 0 and args.vp == 3:
                print(f"DataSet Inconsistency Weights == {dataset.sum_values()}")
                main_logger.error(f"DataSet Inconsistency Values == {dataset.sum_values()}")
                sys.exit(1)

        # Initialize the HittingSetTree
        hitting_set_tree = HittingSetTree(dataset=dataset)
        main_logger.debug("Tree initialized.")
        """
        best_index = 0 # Index to peak at hitting_set_collection
        # Initialize the appropriate pruner based on user input
        if args.pruner == 'UPPER':
            pruner = UpperPruner(kernel_strategy, hitting_set_tree, args.alpha)
        elif args.pruner == 'LOWER':
            best_index = -1 # To get leaf with least priority 
            pruner = LowerPruner(kernel_strategy, hitting_set_tree, args.alpha)
        elif args.pruner == 'BEST':
            pruner = BestPruner(kernel_strategy, hitting_set_tree, args.alpha)
        else:  # Default to BasePruner for no pruning
            pruner = BasePruner(kernel_strategy, hitting_set_tree, args.alpha)
        
        main_logger.debug("Pruner initialized.")
        """

        # Initialize the appropriate search strategy
        if args.ss == 'BFS':
            search_strategy = BFS(kernel_strategy, dataset, args.pruner)
        elif args.ss == 'DFS':
            search_strategy = DFS(kernel_strategy, dataset, args.pruner)
        elif args.ss == 'HYS':
            search_strategy = HYS(kernel_strategy, dataset, args.pruner)
        elif args.ss == 'PBS':
            search_strategy = PBS(kernel_strategy, dataset, args.pruner)
        else:
            main_logger.error("Invalid search strategy")
            sys.exit(1)

        main_logger.debug("Search initialized.")

        hitting_set_tree = KernelSolver(search_strategy).solve()
 
        execution_time = time.time() - start_time
        resources_used = f"{resource.getrusage(resource.RUSAGE_SELF).ru_maxrss} KB"

        results = ResultCalculator(conn, kernelStrategy=kernel_strategy, dataset=dataset, search_strategy=search_strategy, tree=hitting_set_tree, execution_time=execution_time, resources=resources_used, value=args.vp, filename=args.filepath, output_file="Results/All_hitting_sets.csv")
        results.print_results_to_file()
        results.print_results()

        if args.res_db:
            results.log_results()

    except TimeoutError as e:
        main_logger.error(f"Timeout occurred: {e}")
        execution_time = time.time() - start_time
        resources_used = f"{resource.getrusage(resource.RUSAGE_SELF).ru_maxrss} KB"
        if args.res_db and conn is not None:
            log_execution_data(conn, execution_time, resources_used, dataset.get_elements(), args.vp, None, None, None, None, args.filepath, None, args.shrink_div_conq, args.expand_sw_size, args.alpha, args.ss, None, args.expand_div_conq, args.shrink_sw_size, None, args.pruner, None,None,None)
            conn.close()
            print("Program timed out.")
        sys.exit(1)
    except Exception as e:
        main_logger.error(f"An error occurred: {e}. Error trying to process rule {str(e)}")
        sys.exit(1)
    finally:
        signal.alarm(0)  # Cancel the timeout