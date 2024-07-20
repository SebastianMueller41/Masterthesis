    
    

    def calculate_bbvalue(self, current_node, element, dataset):
        assigned_value = dataset.element_values.get(element, 0)
        transformed_value = 1 / (assigned_value) if assigned_value != 0 else 0
        return current_node.bbvalue + transformed_value
    
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