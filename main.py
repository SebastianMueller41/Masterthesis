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
from graphviz import Digraph

def generate_output_filename(input_filename):
    name, ext = os.path.splitext(input_filename)
    return f"{name}_CNF{ext}"

def span_tree_with_kernels(dataset, alpha, tree_node, found_kernels, removed_elements=None):
    if removed_elements is None:
        removed_elements = []
    
    print("REMOVED ELEMENTS: ")
    for elem in removed_elements:
        print(elem)

    result = expand_shrink(dataset, alpha)
    if result is not None:
        found_kernel = result.get_elements()
        
        if found_kernel:
            found_kernels.append(set(found_kernel))
            
            # Create a new tree node with the entire found kernel
            new_node = HSTreeNode(kernel=found_kernel)
            tree_node.add_child(new_node)

            # Create branches for each element in the kernel
            for element in found_kernel:
                # Create a copy of dataset without the current element
                reduced_dataset = dataset.clone()
                reduced_dataset.remove_element(element)
                
                # Recursively span the tree for the child node without the element
                span_tree_with_kernels(reduced_dataset, alpha, new_node, found_kernels, removed_elements + [element])
        else:
            # If the kernel is empty, it's a leaf node
            found_kernels.append(set())
            tree_node.add_child(HSTreeNode(kernel=['-']))  # Mark this node as a leaf

def print_tree(node, level=0):
    indent = "  " * level
    kernel_str = ', '.join(node.kernel) if node.kernel else 'None'
    print(f"{indent}Kernel: {kernel_str}")
    for child in node.children:
        print_tree(child, level + 1)

counter = 1  # Start with 1 since the root is node0

def visualize_tree(node, graph=None, parent_name=None, edge_label=None):
    global counter

    if graph is None:
        graph = Digraph(comment='Hitting Set Tree')
        graph.attr(rankdir='TB', size='8,5', nodesep='0.5', ranksep='1')
        graph.node('node0', 'Root', shape='ellipse', style='filled', fillcolor='lightgrey')
        parent_name = 'node0'

    # Unique node identifier
    current_name = f"node{counter}"
    counter += 1
    
    # Node label should display the entire kernel correctly
    node_label = '{' + '}, {'.join(node.kernel) + '}' if node.kernel else 'Root'
    graph.node(current_name, node_label, shape='ellipse', style='filled', fillcolor='lightgrey')

    # Edge label should be the removed element leading to this node
    if parent_name and edge_label is not None:
        graph.edge(parent_name, current_name, label=edge_label)
        print("PARENT_NAME: " + parent_name + ", CURRENT NAME: " + current_name + ", VISUALIZE: "+ edge_label)

    # Recursively create graph for children
    for child in node.children:
        # The label for edges is the element that was removed
        child_edge_label = ', '.join(child.kernel) if child.kernel else 'Leaf'
        visualize_tree(child, graph, current_name, child_edge_label)

    return graph

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

    # Initialize an empty list to collect found kernels
    found_kernels = []

    # Initial call
    root = HSTreeNode()
    span_tree_with_kernels(input_dataset, "A1", tree.root, found_kernels)

    # Print all found kernels, which should now be a list of sets
    print("All Found Kernels:")
    for kernel in found_kernels:
        print(kernel)

    # After spanning the tree, print it
    print("Final Hitting Set Tree:")
    print_tree(tree.root)

    # Assuming 'tree' is your HittingSetTree instance and 'tree.root' is the root node
    tree_graph = visualize_tree(tree.root)
    # Use a valid path where you have write permissions
    output_path = '/Users/sebastian/git/Masterthesis/output/tree'

    tree_graph.render(output_path, view=True, format='png')