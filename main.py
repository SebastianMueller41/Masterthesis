"""
This script takes a dataset file as input and applies an expand-shrink algorithm to 
find a kernel with respect to a given parameter. The resulting kernel is then used to 
initialize a hitting set tree. This script demonstrates the setup and initial steps of 
the kernelization process for the given dataset.

The script can be executed from the command line with the dataset file and strategy 
parameter as arguments. Logging to a database can be enabled or disabled via an 
optional flag.
"""

import argparse
import os
import sys
import time
import resource
from src.search.hybrid import HybridSearch
from src.search.bfs import BFS
from src.solver.kernelsolver import KernelSolver
from src.kernels.expandshrink import ExpandShrink
from src.structs.dataset import DataSet
from src.structs.hittingsettree import HittingSetTree

from src.database.database import create_connection, log_execution_data

# Set up argument parser
parser = argparse.ArgumentParser(description='Run the kernelization process with optional database logging.')
parser.add_argument('dataset_file', type=str, help='Path to the dataset file')
parser.add_argument('strategy_param', type=int, help='Strategy parameter value')
parser.add_argument('--log-db', action='store_true', help='Enable logging to database')

# Parse arguments
args = parser.parse_args()

def read_dataset_content(dataset_filepath):
    with open(dataset_filepath, 'r') as file:
        return file.read()

if __name__ == "__main__":
    create_connection()  # Prepare the database
    start_time = time.time()

    if not os.path.exists(args.dataset_file):
        print(f"Dataset file not found: {args.dataset_file}")
        sys.exit(1)

    dataset_content = read_dataset_content(args.dataset_file)

    hitting_set_tree = None  # Initialize the hitting set tree to None

    try:
        if args.strategy_param == 0:
            hitting_set_tree = KernelSolver(BFS(ExpandShrink(), DataSet(args.dataset_file, args.strategy_param), "A1")).solve()
        elif 0 < args.strategy_param < 4:
            hitting_set_tree = KernelSolver(HybridSearch(ExpandShrink(), DataSet(args.dataset_file, args.strategy_param), "A1", args.strategy_param)).solve()
        else:
            print("WRONG STRATEGY PARAM! MUST BE 0 = no B&B, 1 = Cardinality, 2 = Random, 3 = Inconsistency")
            sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

    execution_time = time.time() - start_time  # Measure execution time

    if hitting_set_tree:
        num_kernels, num_branches = hitting_set_tree.count_kernels_and_branches()
        pruned_branches_count = hitting_set_tree.count_pruned_nodes()
        tree_depth = hitting_set_tree.tree_depth()
    else:
        num_kernels = num_branches = pruned_branches_count = 0

    resources_used = f"{resource.getrusage(resource.RUSAGE_SELF).ru_maxrss} KB"

    if args.log_db:
        log_execution_data(execution_time, resources_used, dataset_content, args.strategy_param, num_kernels, num_branches, tree_depth, pruned_branches_count, args.dataset_file)

    print(f"Execution time: {execution_time}s, Memory Used: {resources_used}, Tree depth: {tree_depth}, Pruned branches: {pruned_branches_count}, Kernels: {num_kernels}, Branches: {num_branches}")
