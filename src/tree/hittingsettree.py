import heapq
from src.structs.dataset import DataSet

class HSTreeNode:
    def __init__(self, kernel=None, children=None, edge=None, level=0, dataset=None, bbvalue=0, parent=None, pruned=False):
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
        return (self.dataset.element_values.get(self.edge, 0) if self.edge else 0) < (self.dataset.element_values.get(other.edge, 0) if other.edge else 0)

class HittingSetTree:
    def __init__(self, dataset=None, initial_kernel=None, output_file="tmp/tree_output.txt"):
        self.root = HSTreeNode(kernel=initial_kernel)
        self.boundary = float('inf')
        self.dataset = dataset
        self.leaf_nodes = []
        self.output_file = output_file
        self.tree_sum = dataset.sum_values()

        with open(self.output_file, 'w') as file:
            file.truncate()

    def insert_kernel(self, kernel, parent=None):
        if parent is None:
            parent = self.root
        elif parent == self.root and self.root.kernel is None:
            self.root.kernel = kernel
            return self.root
        new_node = HSTreeNode(kernel=kernel)
        parent.add_child(new_node)
        return new_node
    
    def add_leaf_node(self, leaf_node):
        bbvalue = self.calculate_path_bbvalue_up_to_root(leaf_node)
        heapq.heappush(self.leaf_nodes, (bbvalue, leaf_node))

    def calculate_path_bbvalue_up_to_root(self, node):
        cumulative_bbvalue = 0.0
        current_node = node
        while current_node is not None and current_node.edge is not None:
            edge_value = self.dataset.element_values.get(current_node.edge, None)
            if edge_value is None:
                edge_value = 0
            cumulative_bbvalue += 1 / (float(edge_value)) if edge_value != 0 else 0
            current_node = current_node.parent
        return cumulative_bbvalue

    def get_hitting_set_for_leaf(self, leaf_node):
        hitting_set = DataSet()
        current_node = leaf_node
        while current_node is not None and current_node.parent is not None:
            if current_node.edge is not None:
                element_value = self.dataset.get_element_value(current_node.edge)
                hitting_set.add_element(current_node.edge, element_value)
            current_node = current_node.parent
        return hitting_set
    
    def get_hitting_set_for_optimal_solution(self):
        if self.leaf_nodes:
            # Ensure leaf_nodes is sorted by bbvalue descending and cardinality ascending
            sorted_leaf_nodes = sorted(
                self.leaf_nodes, 
                key=lambda x: (-x[0], len(self.get_hitting_set_for_leaf(x[1]).get_elements()))
            )
            _, best_leaf = sorted_leaf_nodes[0]  # Peek at the highest priority leaf
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
            
    def print_tree_to_file(self, node=None, level=0, output_file="tmp/tree_output.txt"):
        if node is None:
            node = self.root

        indent = "  " * level
        hitting_set_value = self.calculate_path_bbvalue_up_to_root(node)

        output_text = f"{level}{indent}Kernel: {node.kernel}, Edge: {node.edge}, Level: {node.level}, Bound: {self.boundary}, Hitting Set Value: {hitting_set_value}\n"

        with open(output_file, 'a') as file:
            file.write(output_text)

        for child in node.children:
            self.print_tree_to_file(child, level + 1, output_file)
        
    def print_newline(self, output_file="tmp/tree_output.txt"):    
        with open(output_file, "a") as file:
            file.write("\n\n")
            
    def print_all_hitting_sets_to_file(self, output_file="tmp/all_hitting_sets.txt"):
        # Convert heap to list for sorting
        leaf_nodes_with_values = [
            (bbvalue, len(self.get_hitting_set_for_leaf(leaf_node).get_elements()), leaf_node)
            for bbvalue, leaf_node in self.leaf_nodes
        ]

        # Sort by bbvalue descending and cardinality ascending
        sorted_leaf_nodes = sorted(leaf_nodes_with_values, key=lambda x: (-x[0], x[1]))

        # Write to file
        with open(output_file, 'a') as file:
            for bbvalue, cardinality, leaf_node in sorted_leaf_nodes:
                hitting_set = self.get_hitting_set_for_leaf(leaf_node)
                if hitting_set is not None:
                    hitting_set_elements = hitting_set.get_elements_with_values()
                    HSvalue = hitting_set.sum_values()
                    file.write(f"{HSvalue}, {bbvalue}, {cardinality}, Hitting Set: {hitting_set_elements}\n")