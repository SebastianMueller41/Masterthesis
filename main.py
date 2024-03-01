"""
This script takes a dataset file as input and applies an expand-shrink algorithm to 
find a kernel with respect to a given parameter. The resulting kernel is then used to 
initialize a hitting set tree. This script demonstrates the setup and initial steps of 
the kernelization process for the given dataset.

The script is executed from the command line with the dataset file as an argument.
"""

import os, sys
from src.search.hybrid import HybridSearch
from src.search.bfs import BFS
from src.solver.kernelsolver import KernelSolver
from src.kernels.expandshrink import ExpandShrink
from src.structs.hittingsettree import HittingSetTree, HSTreeNode
from src.structs.dataset import DataSet

output_directory = 'Results'

def generate_output_filename(input_filename):
    name, ext = os.path.splitext(input_filename)
    return f"{name}_CNF{ext}"

def setup():
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

if __name__ == "__main__":
    setup()
    # if len(sys.argv) < 2:
    #     print("Usage: python main.py <dataset_file>")
    #     sys.exit(1)

    dataset_filepath = sys.argv[1]
    strategy_param = sys.argv[2]

    #print(f"sys.argv[2] = {strategy_param}")
    #dataset_filepath = "data/Test_Datasets/test_UNSAT2.txt"
    #dataset_filepath = "data/Dataset_A/sig3_5_15/srs_0.txt"
    #datas = DataSet(dataset_filepath,strategy_param)
    #print(datas.get_elements_with_values())

    # Ensure strategy_param is an integer for comparison
    try:
        strategy_param = int(strategy_param)
    except ValueError:
        print(f"Invalid strategy_param: {strategy_param}. Must be an integer.")

    with open("tmp/tree_output.txt", 'w') as file:
        pass  # Opening in write mode 'w' clears the file

    if strategy_param == 0:
        KernelSolver(BFS(ExpandShrink(), DataSet(dataset_filepath,strategy_param), "A1" )).solve()
    elif 0 < strategy_param < 4:
        KernelSolver(HybridSearch(ExpandShrink(), DataSet(dataset_filepath,strategy_param), "A1", strategy_param)).solve()
    else:
        print("WRONG STRATEGY PARAM! MUST BE 0 = no B&B, 1 = Cardinality, 2 = Random, 3 = Inconsistency")
    