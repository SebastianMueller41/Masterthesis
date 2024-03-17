import random
from collections import deque
from src.kernels.kernelstrategy import KernelStrategy
from src.structs.dataset import DataSet
from src.structs.hittingsettree import HSTreeNode, HittingSetTree
from .strategy import Strategy

class HybridSearch(Strategy):
    def __init__(self, kernelStrategy: KernelStrategy, dataset: DataSet, alpha, strategy_param):
        self.kernelStrategy = kernelStrategy
        self.dataset = dataset
        self.alpha = alpha
        self.strategy_param = strategy_param
        self.tree = HittingSetTree(dataset=dataset)  # Pass the dataset here

    def find_kernels(self) -> None:
        self.dfs(self.dataset, self.alpha)
        self.bfs(self.alpha, self.tree.root)
        self.tree.print_tree()

    def dfs(self, dataset, alpha, parent: HSTreeNode = None):
        if parent is None:
            result = self.kernelStrategy.find_kernel(dataset, alpha)
            self.tree.root = HSTreeNode(kernel=result.get_elements(), dataset=dataset, bbvalue=0, parent=None)
            self.dfs(self.tree.root.dataset, alpha, self.tree.root)
        else:
            if self.should_prune(parent):
                # Instead of returning, mark the parent as "PRUNED" and stop further processing
                parent.kernel = "PRUNED"
                parent.set_pruned()
                return
            for element in parent.get_kernel():
                reduced_dataset = parent.get_dataset().clone()
                reduced_dataset.remove_element(element)

                bbvalue = self.calculate_bbvalue(parent, element, reduced_dataset)

                child_node = HSTreeNode(kernel=None, dataset=reduced_dataset, edge=element, level=parent.level + 1, bbvalue=bbvalue, parent=parent)
                parent.add_child(child_node)

                result = self.kernelStrategy.find_kernel(reduced_dataset, alpha)
                if result is not None:
                    child_node.set_kernel(result.get_elements())
                    self.dfs(child_node.get_dataset(), alpha, child_node)
                else:
                    child_node.set_kernel("LEAF")
                    self.tree.add_leaf_node(child_node)
                    self.update_boundary_with_leaf(child_node)
        self.log_tree()

    def calculate_bbvalue(self, current_node, element, dataset):
        # Retrieve the assigned value for the current element (either random or based on inconsistency)
        assigned_value = dataset.element_values.get(element, 0)
        
        # Apply the 1/x transformation, treating 1/0 as 0
        transformed_value = 1 / assigned_value if assigned_value != 0 else 0
        
        # Update the bbvalue by adding the transformed value of the current element
        return current_node.bbvalue + transformed_value

    def update_boundary_with_leaf(self, leaf_node):
        leaf_path_measure = self.calculate_path_bbvalue_up_to_root(leaf_node, self.dataset)
        if leaf_path_measure < self.tree.boundary:  # Assuming minimization
            self.tree.boundary = leaf_path_measure
            # Optionally, log or print the updated boundary for debugging
            print(f"Updated boundary: {self.tree.boundary}")

    def bfs(self, alpha, root: HSTreeNode):
        queue = deque([root])
        while queue:
            current_node = queue.popleft()
            # Determine if the current node should be pruned
            if self.should_prune(current_node):
                # Mark this node as pruned and skip further processing
                current_node.edge = "PRUNED"
                continue  # Skip adding children or further processing for this node

            if current_node.get_kernel() is None:
                result = self.kernelStrategy.find_kernel(current_node.get_dataset(), alpha)
                if result is not None:
                    current_node.set_kernel(result.get_elements())
                    for element in current_node.get_kernel():
                        reduced_dataset = current_node.get_dataset().clone()
                        reduced_dataset.remove_element(element)

                        bbvalue = self.calculate_bbvalue(current_node, element, reduced_dataset)

                        # Check again if the node should be pruned after calculating the new bbvalue
                        if not self.should_prune(current_node):
                            child_node = HSTreeNode(dataset=reduced_dataset, edge=element, bbvalue=bbvalue, parent=current_node)
                            current_node.add_child(child_node)
                            queue.append(child_node)
                        else:
                            # If the node is determined to be pruned at this stage, mark accordingly
                            child_node = HSTreeNode(dataset=reduced_dataset, edge="PRUNED", parent=current_node)
                            current_node.add_child(child_node)
                else:
                    current_node.set_kernel("LEAF")
                    self.tree.add_leaf_node(child_node)
                    self.update_boundary_with_leaf(current_node)

            self.log_tree()

    def calculate_path_bbvalue_up_to_root(self, node, dataset):
        cumulative_bbvalue = 0.0
        current_node = node
        while current_node is not None and current_node.edge is not None:
            # Retrieve the inconsistency value for the current edge/formula
            inconsistency_value = dataset.element_values.get(current_node.edge, 0)
            cumulative_bbvalue += 1 / float(inconsistency_value) if inconsistency_value != 0 else 0
            current_node = current_node.parent
        return cumulative_bbvalue

    def should_prune(self, node):
        # Calculate the hitting set value for the node up to the root.
        # Ensure this method returns a float representing the cumulative inconsistency value.
        hitting_set_value = self.tree.calculate_path_bbvalue_up_to_root(node, self.dataset)

        # Now compare the hitting set value (float) with the boundary (float).
        return hitting_set_value >= self.tree.boundary

    def log_tree(self):
        self.tree.print_tree_to_file(dataset=self.dataset)    
        self.tree.print_newline()
