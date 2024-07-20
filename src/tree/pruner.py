


    def expand_children(self, current_node, priority_queue):
        children = []
        for element in current_node.get_kernel():
            reduced_dataset = current_node.get_dataset().clone()
            reduced_dataset.remove_element(element)

            bbvalue = self.calculate_bbvalue(current_node, element, reduced_dataset)
            child_node = HSTreeNode(kernel=None, dataset=reduced_dataset, edge=element, level=current_node.level + 1,
                                    bbvalue=bbvalue, parent=current_node)
            current_node.add_child(child_node)

            priority = self.tree.calculate_path_bbvalue_up_to_root(current_node)
            if priority == 0:
                priority = float('inf')  # Assign a very low priority for 0 values
            children.append((priority, child_node))

        # Sort children by priority in ascending order
        children.sort(key=lambda x: x[0])
        for priority, child_node in children:
            self.add_to_priority_queue(priority_queue, child_node, priority)

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