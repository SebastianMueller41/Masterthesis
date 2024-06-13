"""
This script takes a dataset from a MySQL database and applies an expand-shrink algorithm to 
find a kernel with respect to a given parameter. The resulting kernel is then used to 
initialize a hitting set tree. This script demonstrates the setup and initial steps of 
the kernelization process for the given dataset.

The script can be executed from the command line with the dataset name and strategy 
parameter as arguments. Logging to a database can be enabled or disabled via an 
optional flag.
"""
import argparse
import os
import sys
import time
import resource
import signal
import logging
from src.search.hybrid import HybridSearch
from src.search.bfs import BFS
from src.solver.kernelsolver import KernelSolver
from src.kernels.expandshrink import ExpandShrink
from src.kernels.shrinkexpand import ShrinkExpand
from src.structs.dataset import DataSet
from src.database.database import create_ssh_tunnel_and_connect, log_execution_data

# Configure logging
logging.basicConfig(filename='log/main.log', level=logging.CRITICAL, format='%(asctime)s %(levelname)s:%(message)s')

# Set up argument parser
parser = argparse.ArgumentParser(description='Run the kernelization process with optional database logging.')
parser.add_argument('dataset_name', type=str, help='Name of the dataset stored in the database')
parser.add_argument('strategy_param', type=int, help='Strategy parameter value')
parser.add_argument('--sw-size', '--sliding-window', type=int, default=1, help='Define the window size for the sliding-window technique (default: 1)')
parser.add_argument('-dc', '--divide-conquer', action='store_true', help='Activate the divide and conquer technique')
parser.add_argument('--log-db', action='store_true', help='Enable logging to database')
parser.add_argument('--alpha', type=str, help='A string value to be used as alpha')
group = parser.add_mutually_exclusive_group()
group.add_argument('-k', '--kernel', action='store_const', const='kernel', dest='method', help='Use the kernel method')
group.add_argument('-r', '--remainder', action='store_const', const='remainder', dest='method', help='Use the remainder method')
args = parser.parse_args()

# Function to handle timeout
def timeout_handler(signum, frame):
    raise TimeoutError("Program exceeded the specified time limit.")

if __name__ == "__main__":
    # Prepare for timeout
    signal.signal(signal.SIGALRM, timeout_handler)
    timeout_duration = 1800  # 1800 seconds or 30 minutes
    signal.alarm(timeout_duration)  # Start the timer

    conn = create_ssh_tunnel_and_connect()

    start_time = time.time()

    dataset = DataSet(conn, input_file_path=args.dataset_name, strategy_param=args.strategy_param)
    if not 1 <= args.sw_size <= dataset.size():
        sys.exit(f"--sw-size/--sliding-window must be between 1 and the length of the dataset ({dataset.size()}).")
    if args.alpha:
        logging.info(f"Alpha: {args.alpha}")

    hitting_set_tree = None
    try:
        if args.method == 'kernel':
            if args.strategy_param == 0:
                hitting_set_tree = KernelSolver(BFS(ExpandShrink(args.sw_size, args.divide_conquer), dataset, args.alpha)).solve()
            elif 0 < args.strategy_param < 4:
                hitting_set_tree = KernelSolver(HybridSearch(ExpandShrink(args.sw_size, args.divide_conquer), dataset, args.alpha, args.strategy_param)).solve()
            else:
                logging.error("WRONG STRATEGY PARAM! MUST BE 0 = no B&B, 1 = Cardinality, 2 = Random, 3 = Inconsistency")
                sys.exit(1)
        elif args.method == 'remainder':
            if args.strategy_param == 0:
                hitting_set_tree = KernelSolver(BFS(ShrinkExpand(args.sw_size, args.divide_conquer), dataset, args.alpha)).solve()
            elif 0 < args.strategy_param < 4:
                hitting_set_tree = KernelSolver(HybridSearch(ShrinkExpand(args.sw_size, args.divide_conquer), dataset, args.alpha, args.strategy_param)).solve()
            else:
                logging.error("WRONG STRATEGY PARAM! MUST BE 0 = no B&B, 1 = Cardinality, 2 = Random, 3 = Inconsistency")
                sys.exit(1)
    except TimeoutError as e:
        logging.error(f"Timeout occurred: {e}")
        execution_time = time.time() - start_time
        resources_used = f"{resource.getrusage(resource.RUSAGE_SELF).ru_maxrss} KB"
        if args.log_db and conn is not None:
            log_execution_data(conn, execution_time, resources_used, dataset.get_elements(), args.strategy_param, None, None, None, None, None, args.dataset_name, None, args.divide_conquer, args.sw_size, args.method, args.alpha)
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
    else:
        num_kernels = num_branches = pruned_branches_count = 0
        tree_depth = boundary = None
        optimal_hitting_set = None

    resources_used = f"{resource.getrusage(resource.RUSAGE_SELF).ru_maxrss} KB"

    print(f"Execution time: {execution_time}s, Memory Used: {resources_used}, Strategy: {args.strategy_param}, Kernel_Remainder: {args.method}, Sliding Window size: {args.sw_size}, Divide and conquer: {args.divide_conquer}, Kernels: {num_kernels}, Branches: {num_branches}, Tree depth: {tree_depth}, Pruned branches: {pruned_branches_count}, Boundary: {boundary}")
    print(f"Optimal hitting set: {optimal_hitting_set}, Alpha: {args.alpha}")

    if args.log_db:
        if conn is not None:
            log_execution_data(conn, execution_time, resources_used, dataset.get_elements(), args.strategy_param, num_kernels, num_branches, tree_depth, pruned_branches_count, boundary, args.dataset_name, optimal_hitting_set, args.divide_conquer, args.sw_size, args.method, args.alpha)
            conn.close()
        else:
            print("Connection to MySQL database failed")

    logging.info(f"Execution time: {execution_time}s, Memory Used: {resources_used}, Strategy: {args.strategy_param}, Kernel_Remainder: {args.method}, Sliding Window size: {args.sw_size}, Divide and conquer: {args.divide_conquer}, Kernels: {num_kernels}, Branches: {num_branches}, Tree depth: {tree_depth}, Pruned branches: {pruned_branches_count}, Boundary: {boundary}")
    logging.info(f"Optimal hitting set: {optimal_hitting_set}, Alpha: {args.alpha}")
