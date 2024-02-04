"""
This script takes a dataset file as input and applies an expand-shrink algorithm to 
find a kernel with respect to a given parameter. The resulting kernel is then used to 
initialize a hitting set tree. This script demonstrates the setup and initial steps of 
the kernelization process for the given dataset.

The script is executed from the command line with the dataset file as an argument.
"""

import os
import sys
from hittingsettree import HittingSetTree
from kernel import expand_shrink
from dataset import DataSet

def generate_output_filename(input_filename):
    """
    Generate an output filename with '_CNF' appended before the file extension.

    Args:
        input_filename (str): The name of the input file.

    Returns:
        str: The name of the output file with '_CNF' appended before the extension.
    """
    name, ext = os.path.splitext(input_filename)
    return f"{name}_CNF{ext}"

if __name__ == "__main__":
    # Ensure the correct number of command line arguments
    if len(sys.argv) < 2:
        print("Usage: python main.py <dataset_file>")
        sys.exit(1)

    dataset_filepath = sys.argv[1]
    output_directory = 'Results'

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    # Assuming the necessary imports and class definitions are already in place

    def print_tree(node, level=0):
        """
        Recursively print the tree starting from the given node.
        
        Args:
            node (HSTreeNode): The current node to print.
            level (int): The current level in the tree for indentation purposes.
        """
        indent = "  " * level
        print(f"{indent}Kernel: {node.kernel}")
        for child in node.children:
            print_tree(child, level + 1)

    # Load the dataset from the specified file
    input_dataset = DataSet(dataset_filepath)

    # Initialize the hitting set tree
    tree = HittingSetTree()

    # Keep a mutable copy of the input dataset that can be modified in each iteration
    mutable_dataset = DataSet(dataset_filepath)

    while True:  # Continue until no more kernels are found
        # Apply the expand-shrink algorithm to find a kernel
        result = expand_shrink(mutable_dataset, "A1")

        # Check if a kernel was found by ensuring result is not None
        if result is not None:
            found_kernel = result.get_elements()
            print(f"Kernel output: {found_kernel}")

            # Check if the found kernel list is empty, indicating a leaf node
            if not found_kernel:
                print("Reached a leaf node (empty kernel). Terminating loop.")
                break

            # Insert the found kernel into the hitting set tree
            tree.insert_kernel(found_kernel)

            # Remove the first element of the found kernel from mutable_dataset for the next iteration
            element_to_remove = found_kernel[0]
            mutable_dataset.remove_element(element_to_remove)
            print(f"Removed '{element_to_remove}' from dataset for next iteration.")
        else:
            print("No kernel found. Terminating loop.")
            break

    # After finding no more kernels, print the tree
    print("Final Hitting Set Tree:")
    print_tree(tree.root)

