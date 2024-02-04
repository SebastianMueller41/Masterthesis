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
    
    # Initialize the hitting set tree
    tree = HittingSetTree()

    # Load the dataset from the specified file
    input_dataset = DataSet(dataset_filepath)

    # Apply the expand-shrink algorithm to find the initial kernel
    found_kernel = expand_shrink(input_dataset, "A1").get_elements()

    # Insert the found kernel into the hitting set tree
    tree.insert_kernel(found_kernel)

    # Print the kernel of the first child node, if it exists
    if tree.root.children:  # Check if there are children to avoid IndexError
        first_child_node = tree.root.children[0]
        if first_child_node.kernel:  # Check if kernel has elements
            first_set = first_child_node.kernel[0]
            second_set = first_child_node.kernel[1]
            print("First set:", first_set)
            print("Second set:", second_set)
    else:
        print("No child nodes found.")

    print("Next step, find kernel without: " + str(first_set))
