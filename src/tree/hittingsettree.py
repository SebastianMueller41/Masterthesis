import heapq
from src.structs.dataset import DataSet
import logging
from src.structs.logger import setup_logging

# Set up logging for this module
setup_logging()

class HSTreeNode:
    def __init__(self, kernel=None, children=None, edge=None, level=0, dataset=None, bbvalue=0, sub_value=0, parent=None, pruned=False):
        self.kernel = kernel
        self.children = children if children is not None else []
        self.edge = edge
        self.level = level
        self.dataset = dataset
        self.bbvalue = bbvalue
        self.sub_value = sub_value
        self.parent = parent
        self.pruned = pruned

    def get_kernel(self):
        return self.kernel
    
    def set_kernel(self, kernel):
        self.kernel = kernel
        
    def get_dataset(self):
        return self.dataset

    def add_child(self, child):
        child.level = self.level + 1
        self.children.append(child)

    def print_node(self, level=0):
        indent = "  " * level
        print(f"{indent}Kernel: {self.kernel}")
        for child in self.children:
            child.print_node(level + 1)

    def is_pruned(self):
        return self.pruned
    
    def set_pruned(self, pruned=True):
        self.pruned = pruned
    
    def __lt__(self, other):
        # Compare based on bbvalue or any other criteria
        return self.bbvalue < other.bbvalue

    def __str__(self):
        return f"HSTreeNode(kernel={self.kernel}, bbvalue={self.bbvalue})"

    def __repr__(self):
        return self.__str__()

class HittingSetTree:
    def __init__(self, dataset=None, kernel_strategy=None, initial_kernel=None, search_strategy=None, output_file="Results/tree_output.txt"):
        self.root = HSTreeNode(kernel=initial_kernel)
        self.dataset = dataset
        self.leaf_nodes = []
        self.output_file = output_file
        self.tree_sum = dataset.sum_values()
        self.upper_bound = float('inf')
        self.lower_bound = 0
        self.search_strategy = search_strategy

        with open(self.output_file, 'w') as file:
            file.truncate()

    def insert_kernel(self, kernel, parent=None):
        if parent is None:
            parent = self.root
        elif parent == self.root and self.root.kernel is None:
            self.root.kernel = kernel
            return self.root
        new_node = HSTreeNode(kernel=kernel, dataset=self.dataset)
        parent.add_child(new_node)
        return new_node
    
    def add_leaf_node(self, leaf_node):
        bbvalue = self.calculate_path_bbvalue_up_to_root(leaf_node)
        heapq.heappush(self.leaf_nodes, (bbvalue, leaf_node))

    def calculate_path_bbvalue_up_to_root(self, node):
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
        hitting_set = DataSet()
        current_node = leaf_node
        while current_node is not None and current_node.parent is not None:
            if current_node.edge is not None:
                hitting_set.add_element(current_node.edge)
            current_node = current_node.parent
        return hitting_set
    
    def get_hitting_set_for_optimal_solution(self, index):
        if self.leaf_nodes:
            self.sort_leaf_nodes_desc('bbvalue')
            _, best_leaf = self.leaf_nodes[index]  # To peek at the highest (UPPER) or lowest (LOWER) priority
            return self.get_hitting_set_for_leaf(best_leaf)
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
        if node is None:
            node = self.root
        
        if node.children == []:
            return 0

        max_depth = 0
        for child in node.children:
            child_depth = self.tree_depth(child)
            max_depth = max(max_depth, child_depth)

        return max_depth + 1

    def print_tree(self, node=None, level=0):
        if node is None:
            node = self.root
        indent = "  " * level
        print(f"{indent}Kernel: {node.kernel}")
        for child in node.children:
            self.print_tree(child, level + 1)
            
    def print_tree_to_file(self, node=None, level=0, output_file="Results/tree_output.txt"):
        if node is None:
            node = self.root

        indent = "  " * level
        hitting_set_value = self.calculate_path_bbvalue_up_to_root(node)

        output_text = f"{level}{indent}Kernel: {node.kernel}, Edge: {node.edge}, Level: {node.level}, Bounds L / U: {self.upper_bound} / {self.lower_bound}, Path Value: {hitting_set_value}, Sub Value: {node.sub_value}, Dataset Sum: {node.dataset.sum_values()}\n"

        with open(output_file, 'a') as file:
            file.write(output_text)

        for child in node.children:
            self.print_tree_to_file(child, level + 1, output_file)

    def print_newline(self, output_file="Results/tree_output.txt"):    
        with open(output_file, "a") as file:
            file.write("\n\n")