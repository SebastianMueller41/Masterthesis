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

    def log_tree(self):
        self.tree.print_tree_to_file()
        self.tree.print_newline()
