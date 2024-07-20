class BasePruner:
    def __init__(self, tree):
        self.tree = tree
        self.best_solution = None
        self.boundary = 0

    def calculate_potential_bound(self, node):
        return float('inf')

    def update_boundary_with_leaf(self, leaf_node):
        pass

    def should_prune(self, node):
        return False
