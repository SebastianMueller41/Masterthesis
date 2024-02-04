"""
This script takes a dataset file as input and applies an expand-shrink algorithm to 
find a kernel with respect to a given parameter. The resulting kernel is then used to 
initialize a hitting set tree. This script demonstrates the setup and initial steps of 
the kernelization process for the given dataset.

The script is executed from the command line with the dataset file as an argument.
"""

import os
import sys
from hittingsettree import HittingSetTree, HSTreeNode
from kernel import expand_shrink
from dataset import DataSet

def generate_output_filename(input_filename):
    name, ext = os.path.splitext(input_filename)
    return f"{name}_CNF{ext}"

def span_tree_with_kernels(dataset, alpha, tree_node):
    result = expand_shrink(dataset, alpha)
    if result is not None:
        found_kernel = result.get_elements()
        if not found_kernel:
            # If found_kernel is empty, we've hit a leaf node
            return
        
        for element in found_kernel:
            # Create a copy of dataset without the current element
            reduced_dataset = dataset.clone()
            reduced_dataset.remove_element(element)
            # Create a new tree node for the reduced dataset
            child_node = HSTreeNode(kernel=element)
            tree_node.add_child(child_node)
            # Recursively span the tree
            span_tree_with_kernels(reduced_dataset, alpha, child_node)

def print_tree(node, level=0):
    indent = "  " * level
    print(f"{indent}Kernel: {node.kernel}")
    for child in node.children:
        print_tree(child, level + 1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <dataset_file>")
        sys.exit(1)

    dataset_filepath = sys.argv[1]
    output_directory = 'Results'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Initialize the hitting set tree with an empty kernel at the root
    tree = HittingSetTree()

    # Load the dataset from the specified file
    input_dataset = DataSet(dataset_filepath)

    # Span the entire tree
    span_tree_with_kernels(input_dataset, "A1", tree.root)

    # After spanning the tree, print it
    print("Final Hitting Set Tree:")
    print_tree(tree.root)
