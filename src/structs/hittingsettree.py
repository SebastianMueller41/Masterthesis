"""
This module defines a data structure for a hitting set tree, which is a tree where each node
contains a 'kernel'. The tree can be used in various algorithms to systematically explore and
record combinations of elements (such as in computational logic or optimization problems).

Classes:
    HSTreeNode: Represents a single node in a hitting set tree.
    HittingSetTree: Represents the entire hitting set tree structure.
"""

class HSTreeNode:
    """
    A node within a hitting set tree.

    Attributes:
        kernel (list): The data or 'kernel' for this node.
        children (list of HSTreeNode): Child nodes of this node.
    """
    
    def __init__(self, kernel=None, children=None, edge=None, level=0, dataset=None, bbvalue=0, parent=None, pruned=False):
        """
        Initialize a node for the hitting set tree.

        Args:
            kernel (list): The data or 'kernel' for this node.
            children (list of HSTreeNode, optional): Child nodes of this node.
        """
        self.kernel = kernel
        self.children = children if children is not None else []
        self.edge = edge
        self.level = level
        self.dataset = dataset
        self.bbvalue = bbvalue
        self.parent = parent
        self.pruned = pruned

    def get_kernel(self):
        return self.kernel
    
    def set_kernel(self, kernel):
        self.kernel = kernel
        
    def get_dataset(self):
        return self.dataset

    def add_child(self, child):
        """
        Add a child node to this node's children.

        Args:
            child (HSTreeNode): A child node to be added.
        """
        child.level = self.level + 1
        self.children.append(child)

    def print_node(self, level=0):
        """
        Recursively print the node and its children, indented according to their level in the tree.

        Args:
            level (int): The current level of this node within the tree.
        """
        indent = "  " * level
        print(f"{indent}Kernel: {self.kernel}")
        for child in self.children:
            child.print_node(level + 1)

    def is_pruned(self):
        return self.pruned
    
    def set_pruned(self, pruned=True):
        self.pruned = pruned

class HittingSetTree:
    """
    Represents a hitting set tree that can be used to organize and store kernels in a hierarchical manner.

    Attributes:
        root (HSTreeNode): The root node of the tree.
    """
    
    def __init__(self, dataset=None, initial_kernel=None, output_file="tmp/tree_output.txt"):
        """
        Initialize the hitting set tree with an optional initial kernel at the root.

        Args:
            initial_kernel (list, optional): An initial kernel to store at the root of the tree.
        """
        self.root = HSTreeNode(kernel=initial_kernel)
        self.boundary = float('inf')  # Initialize the upper bound.
        self.dataset = dataset
        self.leaf_nodes= []
        self.output_file = output_file
        
        # Erase previous content of the output file at initialization
        with open(self.output_file, 'w') as file:
            file.truncate()  # Clears the file


    def insert_kernel(self, kernel, parent=None):
        """
        Insert a new kernel into the tree as a child of the specified parent node or the root by default.

        Args:
            kernel (list): The kernel to insert into the tree.
            parent (HSTreeNode, optional): The parent node under which to insert the new kernel.

        Returns:
            HSTreeNode: The newly created node containing the kernel.
        """
        if parent is None:
            parent = self.root
        elif parent == self.root and self.root.kernel is None:
            # If the root is empty and no parent is specified, initialize the root with this kernel
            self.root.kernel = kernel
            return self.root
        new_node = HSTreeNode(kernel=kernel)
        parent.add_child(new_node)
        return new_node
    
    def add_leaf_node(self, leaf_node):
        self.leaf_nodes.append(leaf_node)
    
    def calculate_path_bbvalue_up_to_root(self, node, dataset):
        cumulative_bbvalue = 0.0
        current_node = node
        while current_node is not None and current_node.parent is not None:  # Assuming each node has a 'parent' reference.
            inconsistency_value = dataset.element_values.get(current_node.edge, 0)
            cumulative_bbvalue += 1 / inconsistency_value if inconsistency_value != 0 else 0
            current_node = current_node.parent
        return cumulative_bbvalue
    
    def get_hitting_set_for_leaf(self, leaf_node):
        """
        Traverses from a given leaf node up to the root node, collecting all edges.

        Args:
            leaf_node (HSTreeNode): The leaf node to start from.

        Returns:
            list: The hitting set consisting of all edges from the leaf to the root.
        """
        hitting_set = []
        current_node = leaf_node
        while current_node is not None and current_node.parent is not None:  # Ensure not at root
            if current_node.edge is not None:  # Assuming edge attribute is used
                hitting_set.append(current_node.edge)
            current_node = current_node.parent
        return hitting_set

    def get_hitting_set_for_optimal_solution(self):
        """
        """
        if self.leaf_nodes:
            return self.get_hitting_set_for_leaf(self.leaf_nodes[-1])
        else:
            return None

    def count_kernels_and_branches(self, node=None):
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
        if node is None:
            node = self.root
        count = 1 if node.is_pruned() else 0
        for child in node.children:
            count += self.count_pruned_nodes(child)
        return count
    
    def tree_depth(self, node=None):
        """
        Calculate the depth of the tree from the given node down to the deepest leaf.
        
        Args:
            node (HSTreeNode, optional): The node to start calculating depth from. If None, start from the root.
            
        Returns:
            int: The depth of the tree.
        """
        if node is None:
            node = self.root
        
        # A leaf node has a depth of 0
        if node.children == []:
            return 0

        # Recursively calculate the depth of each subtree and find the maximum
        max_depth = 0
        for child in node.children:
            child_depth = self.tree_depth(child)
            max_depth = max(max_depth, child_depth)

        # Add 1 to the maximum depth of the subtree to account for the current node
        return max_depth + 1

    def print_tree(self, node=None, level=0):
        if node is None:
            node = self.root
        indent = "  " * level
        print(f"{indent}Kernel: {node.kernel}")
        for child in node.children:
            self.print_tree(child, level + 1)
            
    def print_tree_to_file(self, node=None, level=0, output_file="tmp/tree_output.txt", dataset=None):
        if node is None:
            node = self.root

        indent = "  " * level
        # Calculate the hitting set value for the current node
        hitting_set_value = self.calculate_path_bbvalue_up_to_root(node, dataset=dataset)

        output_text = f"{level}{indent}Kernel: {node.kernel}, Edge: {node.edge}, Level: {node.level}, Bound: {self.boundary}, Hitting Set Value: {hitting_set_value}\n"

        with open(output_file, 'a') as file:
            file.write(output_text)

        for child in node.children:
            self.print_tree_to_file(child, level + 1, output_file, dataset=dataset)
        
    def print_newline(self, output_file="tmp/tree_output.txt"):    
        with open(output_file, "a") as file:
            file.write("\n\n")