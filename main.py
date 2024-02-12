"""
This script takes a dataset file as input and applies an expand-shrink algorithm to 
find a kernel with respect to a given parameter. The resulting kernel is then used to 
initialize a hitting set tree. This script demonstrates the setup and initial steps of 
the kernelization process for the given dataset.

The script is executed from the command line with the dataset file as an argument.
"""

import os
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

    # dataset_filepath = sys.argv[1]
    #dataset_filepath = "data/Test_Datasets/test_UNSAT2.txt"
    dataset_filepath = "data/Dataset_A/sig3_5_15/srs_0.txt"
    
    KernelSolver(BFS(ExpandShrink(), DataSet(dataset_filepath), "A1" )).solve()
    KernelSolver(HybridSearch(ExpandShrink(), DataSet(dataset_filepath), "A1" )).solve()