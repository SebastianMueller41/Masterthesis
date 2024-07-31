"""
This module defines the HSTreeNode and HittingSetTree classes for managing and manipulating 
a hitting set tree structure. It includes methods for expanding child nodes, calculating path 
values, and printing the tree structure.
"""

import heapq
from src.structs.dataset import DataSet
import logging
from src.structs.logger import setup_logging

# Set up logging for this module
setup_logging()

class HSTreeNode:
    """
    A class representing a node in the hitting set tree.

    Attributes:
        kernel (list): The kernel associated with this node.
        children (list): The child nodes of this node.
        edge (str): The edge value used to expand to this node.
        level (int): The level of the node in the tree.
        dataset (DataSet): The dataset associated with this node.
        path_value (float): The path value of the node.
        sub_value (float): The subproblem value of the node.
        parent (HSTreeNode): The parent node.
        pruned (bool): Whether the node is pruned.
    """

    def __init__(self, kernel=None, children=None, edge=None, level=0, dataset=None, path_value=0, sub_value=0, parent=None, pruned=False):
        """
        Initialize an HSTreeNode.

        Args:
            kernel (list, optional): The kernel associated with this node. Defaults to None.
            children (list, optional): The child nodes of this node. Defaults to None.
            edge (str, optional): The edge value used to expand to this node. Defaults to None.
            level (int, optional): The level of the node in the tree. Defaults to 0.
            dataset (DataSet, optional): The dataset associated with this node. Defaults to None.
            path_value (float, optional): The path value of the node. Defaults to 0.
            sub_value (float, optional): The subproblem value of the node. Defaults to 0.
            parent (HSTreeNode, optional): The parent node. Defaults to None.
            pruned (bool, optional): Whether the node is pruned. Defaults to False.
        """
        self.kernel = kernel
        self.children = children if children is not None else []
        self.edge = edge
        self.level = level
        self.dataset = dataset
        self.path_value = path_value
        self.sub_value = sub_value
        self.parent = parent
        self.pruned = pruned

    def get_kernel(self):
        """
        Get the kernel associated with this node.

        Returns:
            list: The kernel.
        """
        return self.kernel
    
    def set_kernel(self, kernel):
        """
        Set the kernel for this node.

        Args:
            kernel (list): The kernel to set.
        """
        self.kernel = kernel
        
    def get_dataset(self):
        """
        Get the dataset associated with this node.

        Returns:
            DataSet: The dataset.
        """
        return self.dataset

    def add_child(self, child):
        """
        Add a child node to this node.

        Args:
            child (HSTreeNode): The child node to add.
        """
        child.level = self.level + 1
        self.children.append(child)

    def print_node(self, level=0):
        """
        Print the node and its children recursively.

        Args:
            level (int, optional): The current level in the tree. Defaults to 0.
        """
        indent = "  " * level
        print(f"{indent}Kernel: {self.kernel}")
        for child in self.children:
            child.print_node(level + 1)

    def is_pruned(self):
        """
        Check if the node is pruned.

        Returns:
            bool: True if the node is pruned, False otherwise.
        """
        return self.pruned
    
    def set_pruned(self, pruned=True):
        """
        Set the pruned status of the node.

        Args:
            pruned (bool, optional): The pruned status to set. Defaults to True.
        """
        self.pruned = pruned
    
    def __lt__(self, other):
        """
        Less than comparison based on path value.

        Args:
            other (HSTreeNode): The other node to compare.

        Returns:
            bool: True if this node's path value is less than the other node's path value.
        """
        return self.path_value < other.path_value

    def __str__(self):
        """
        String representation of the node.

        Returns:
            str: The string representation of the node.
        """
        return f"HSTreeNode(kernel={self.kernel}, path_value={self.path_value})"

    def __repr__(self):
        """
        String representation of the node for debugging.

        Returns:
            str: The string representation of the node.
        """
        return self.__str__()

class HittingSetTree:
    """
    A class representing a hitting set tree.

    Attributes:
        root (HSTreeNode): The root node of the tree.
        dataset (DataSet): The dataset associated with the tree.
        leaf_nodes (list): The list of leaf nodes in the tree.
        output_file (str): The file to output the tree structure.
        tree_sum (float): The sum of values in the dataset.
        upperBound (float): The upper bound for the search.
        lowerBound (float): The lower bound for the search.
        search_strategy (Search): The search strategy used.
        kernelStrategy (KernelStrategy): The kernel strategy used.
    """

    def __init__(self, dataset=None, kernel_strategy=None, initial_kernel=None, search_strategy=None, output_file="Results/tree_output.txt"):
        """
        Initialize a HittingSetTree.

        Args:
            dataset (DataSet, optional): The dataset associated with the tree. Defaults to None.
            kernel_strategy (KernelStrategy, optional): The kernel strategy used. Defaults to None.
            initial_kernel (list, optional): The initial kernel. Defaults to None.
            search_strategy (Search, optional): The search strategy used. Defaults to None.
            output_file (str, optional): The file to output the tree structure. Defaults to "Results/tree_output.txt".
        """
        self.root = HSTreeNode(kernel=initial_kernel)
        self.dataset = dataset
        self.leaf_nodes = []
        self.output_file = output_file
        self.tree_sum = dataset.sum_values()
        self.upperBound = float('inf')
        self.lowerBound = 0
        self.search_strategy = search_strategy
        self.kernelStrategy = kernel_strategy

        with open(self.output_file, 'w') as file:
            file.truncate()

    def insert_kernel(self, kernel, parent=None):
        """
        Insert a kernel into the tree.

        Args:
            kernel (list): The kernel to insert.
            parent (HSTreeNode, optional): The parent node. Defaults to None.

        Returns:
            HSTreeNode: The new node created.
        """
        if parent is None:
            parent = self.root
        elif parent == self.root and self.root.kernel is None:
            self.root.kernel = kernel
            return self.root
        new_node = HSTreeNode(kernel=kernel, dataset=self.dataset)
        parent.add_child(new_node)
        return new_node
    
    def add_leaf_node(self, leaf_node):
        """
        Add a leaf node to the tree.

        Args:
            leaf_node (HSTreeNode): The leaf node to add.
        """
        bbvalue = self.calculate_path_bbvalue_up_to_root(leaf_node)
        heapq.heappush(self.leaf_nodes, (bbvalue, leaf_node))

    def calculate_path_bbvalue_up_to_root(self, node):
        """
        Calculate the path value up to the root.

        Args:
            node (HSTreeNode): The node to calculate the path value for.

        Returns:
            float: The calculated path value.
        """
        cumulative_bbvalue = 0.0
        current_node = node
        while current_node is not None and current_node.edge is not None:
            edge_value = self.dataset.get_element_value(current_node.edge)
            if edge_value is None:
                edge_value = 0
            cumulative_bbvalue += (float(edge_value)) if edge_value != 0 else 0
            current_node = current_node.parent
        return cumulative_bbvalue

    def get_hitting_set_for_leaf(self, leaf_node):
        """
        Get the hitting set for a leaf node.

        Args:
            leaf_node (HSTreeNode): The leaf node to get the hitting set for.

        Returns:
            DataSet: The hitting set dataset.
        """
        hitting_set = DataSet()
        current_node = leaf_node
        while current_node is not None and current_node.parent is not None:
            if current_node.edge is not None:
                hitting_set.add_element(current_node.edge)
            current_node = current_node.parent
        return hitting_set
    
    def get_hitting_set_for_optimal_solution(self, index):
        """
        Get the hitting set for the optimal solution.

        Args:
            index (int): The index of the optimal solution.

        Returns:
            DataSet: The hitting set dataset.
        """
        if self.leaf_nodes:
            self.sort_leaf_nodes_desc('path_value')
            _, best_leaf = self.leaf_nodes[index]  # To peek at the highest (UPPER) or lowest (LOWER) priority
            return self.get_hitting_set_for_leaf(best_leaf)
        else:
            return None

    def count_kernels_and_branches(self, node=None):
        """
        Count the number of kernels and branches in the tree.

        Args:
            node (HSTreeNode, optional): The node to start counting from. Defaults to None.

        Returns:
            tuple: The number of kernels and branches.
        """
        if node is None:
            node = self.root
        if not node or node.is_pruned():
            return (0, 0)
        
        num_kernels = 1 if node.kernel else 0
        num_branches = len(node.children)
        
        for child in node.children:
            child_kernels, child_branches = self.count_kernels_and_branches(child)
            num_kernels += child_kernels
            num_branches += child_branches
        
        return (num_kernels, num_branches)
    
    def count_pruned_nodes(self, node=None):
        """
        Count the number of pruned nodes in the tree.

        Args:
            node (HSTreeNode, optional): The node to start counting from. Defaults to None.

        Returns:
            int: The number of pruned nodes.
        """
        if node is None:
            node = self.root
        count = 1 if node.is_pruned() else 0
        for child in node.children:
            count += self.count_pruned_nodes(child)
        return count
    
    def tree_depth(self, node=None):
        """
        Calculate the depth of the tree.

        Args:
            node (HSTreeNode, optional): The node to start calculating from. Defaults to None.

        Returns:
            int: The depth of the tree.
        """
        if node is None:
            node = self.root
        
        if not node.children:
            return 0

        max_depth = 0
        for child in node.children:
            child_depth = self.tree_depth(child)
            max_depth = max(max_depth, child_depth)

        return max_depth + 1

    def print_tree(self, node=None, level=0):
        """
        Print the tree structure.

        Args:
            node (HSTreeNode, optional): The node to start printing from. Defaults to None.
            level (int, optional): The current level in the tree. Defaults to 0.
        """
        if node is None:
            node = self.root
        indent = "  " * level
        print(f"{indent}Kernel: {node.kernel}")
        for child in node.children:
            self.print_tree(child, level + 1)
            
    def print_tree_to_file(self, node=None, level=0, output_file="Results/tree_output.txt"):
        """
        Print the tree structure to a file.

        Args:
            node (HSTreeNode, optional): The node to start printing from. Defaults to None.
            level (int, optional): The current level in the tree. Defaults to 0.
            output_file (str, optional): The file to output the tree structure. Defaults to "Results/tree_output.txt".
        """
        if node is None:
            node = self.root

        indent = "  " * level
        hitting_set_value = self.calculate_path_bbvalue_up_to_root(node)

        output_text = f"{level}{indent}Kernel: {node.kernel}, Edge: {node.edge}, Level: {node.level}, Bounds L / U: {self.upperBound} / {self.lowerBound}, Path Value: {hitting_set_value}, Sub Value: {node.sub_value}, Dataset Sum: {node.dataset.sum_values()}\n"

        with open(output_file, 'a') as file:
            file.write(output_text)

        for child in node.children:
            self.print_tree_to_file(child, level + 1, output_file)

    def print_newline(self, output_file="Results/tree_output.txt"):    
        """
        Print a newline to the output file.

        Args:
            output_file (str, optional): The file to output the newline. Defaults to "Results/tree_output.txt".
        """
        with open(output_file, "a") as file:
            file.write("\n\n")
