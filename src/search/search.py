from src.structs.hittingsettree import HSTreeNode, HittingSetTree
from src.kernels.kernelstrategy import KernelStrategy
from src.structs.dataset import DataSet

class Search:
    def __init__(self, kernelStrategy: KernelStrategy, dataset: DataSet, alpha, strategy_param):
        self.kernelStrategy = kernelStrategy
        self.dataset = dataset
        self.alpha = alpha
        self.strategy_param = strategy_param
        self.tree = HittingSetTree(dataset=dataset)

    def calculate_bbvalue(self, current_node, element, dataset):
        assigned_value = dataset.element_values.get(element, 0)
        transformed_value = 1 / assigned_value if assigned_value != 0 else 0
        return current_node.bbvalue + transformed_value

    def update_boundary_with_leaf(self, leaf_node):
        leaf_path_measure = self.calculate_path_bbvalue_up_to_root(leaf_node, self.dataset)
        if leaf_path_measure < self.tree.boundary:
            self.tree.boundary = leaf_path_measure
            print(f"Updated boundary: {self.tree.boundary}")

    def calculate_path_bbvalue_up_to_root(self, node, dataset):
        cumulative_bbvalue = 0.0
        current_node = node
        while current_node is not None and current_node.edge is not None:
            edge_value = dataset.element_values.get(current_node.edge, None)
            if edge_value is None:
                print(f"Warning: edge_value for {current_node.edge} is None. Defaulting to 0.")
                edge_value = 0
            cumulative_bbvalue += 1 / float(edge_value) if edge_value != 0 else 0
            current_node = current_node.parent
        return cumulative_bbvalue

    def should_prune(self, node):
        hitting_set_value = self.tree.calculate_path_bbvalue_up_to_root(node, self.dataset)
        if self.tree.boundary == 0:
            return False
        return hitting_set_value >= self.tree.boundary

    def log_tree(self):
        self.tree.print_tree_to_file(dataset=self.dataset)
        self.tree.print_newline()
