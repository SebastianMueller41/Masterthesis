# src/tree/pruner.py

class OptimalPruner:
    def __init__(self, tree):
        self.tree = tree
        self.optimal_reached = False
        self.best_solution = None

    def should_prune(self, node):
        if self.tree.boundary == 0:
            return False
        if not self.optimal_reached:
            return False
        if node is not None:
            return len(node.get_kernel()) >= len(self.best_solution.get_kernel())
        return True

    def update_boundary_with_leaf(self, leaf_node):
        leaf_path_measure = self.tree.calculate_path_bbvalue_up_to_root(leaf_node)
        leaf_cardinality = len(self.tree.get_hitting_set_for_leaf(leaf_node).get_elements())

        if leaf_path_measure == self.tree.tree_sum:
            if self.best_solution is None or leaf_cardinality < len(self.best_solution.get_kernel()):
                self.optimal_reached = True
                self.best_solution = leaf_node
                print(f"New optimal solution found with cardinality {leaf_cardinality}")
            elif leaf_cardinality == 3 and len(self.best_solution.get_kernel()) > 3:
                self.optimal_reached = True
                self.best_solution = leaf_node
                print(f"New optimal solution found with cardinality {leaf_cardinality} and tree sum 3")
    
    def update_boundary_with_leaf(self, leaf_node):
        leaf_path_measure = self.tree.calculate_path_bbvalue_up_to_root(leaf_node)
        if 0 < leaf_path_measure < self.tree.boundary:
            self.tree.boundary = leaf_path_measure
            print(f"Updated boundary: {self.tree.boundary}")

    def should_prune(self, node):
        hitting_set_value = self.tree.calculate_path_bbvalue_up_to_root(node)
        if self.tree.boundary == 0:
            return False
        return hitting_set_value >= self.tree.boundary
    

class LowerPruner:
    def __init__(self, tree):
        self.tree = tree




class UpperPruner:
    def __init__(self, tree):
        self.tree = tree

    def calculate_bbvalue(self, current_node, element, dataset):
        assigned_value = dataset.element_values.get(element, 0)
        return current_node.bbvalue + assigned_value
    
    def calculate_potential_bound(self, node):
        # A simple heuristic: sum the values of all remaining elements in the dataset
        potential_bound = self.tree.get_hitting_set_for_leaf(node).sum_values()
        potential_bound += node.get_dataset().sum_values() # Add sum value of remaining elements
        return potential_bound 

    def update_boundary_with_leaf(self, leaf_node):
        #leaf_path_measure = self.tree.calculate_path_bbvalue_up_to_root(leaf_node)
        leaf_path_measure = self.tree.get_hitting_set_for_leaf(leaf_node).sum_values()
        if leaf_path_measure > self.tree.boundary:
            self.tree.boundary = leaf_path_measure
            print(f"Updated boundary: {self.tree.boundary}")

    def should_prune(self, node):
        if self.tree.boundary == 0:
            return False
        return self.calculate_potential_bound(node) <= self.tree.boundary