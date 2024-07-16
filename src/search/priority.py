import heapq
import logging
from src.search.strategy import Strategy
from src.search.search import Search
from src.structs.hittingsettree import HSTreeNode

class PrioritySearch(Strategy, Search):
    def __init__(self, kernelStrategy, dataset, alpha, strategy_param):
        Search.__init__(self, kernelStrategy, dataset, alpha, strategy_param)
        self.tree.boundary = float('inf')

    def find_kernels(self) -> None:
        initial_node = self.create_initial_node(self.dataset, self.alpha)
        if initial_node is None:
            logging.info("Initial kernel is None, no need to span the tree.")
            return
        self.priority_search(initial_node)
        self.tree.print_tree()
        self.log_tree()

    def create_initial_node(self, dataset, alpha):
        result = self.kernelStrategy.find_kernel(dataset, alpha)
        if result is None:
            return None
        initial_node = HSTreeNode(kernel=result.get_elements(), dataset=dataset, bbvalue=0, parent=None)
        self.tree.root = initial_node
        return initial_node

    def priority_search(self, root: HSTreeNode):
        priority_queue = []
        self.add_to_priority_queue(priority_queue, root, 0)

        while priority_queue:
            _, current_node = heapq.heappop(priority_queue)

            if self.should_prune(current_node):
                current_node.kernel = "PRUNED"
                current_node.set_pruned()
                continue

            if current_node.get_kernel() is None:
                result = self.kernelStrategy.find_kernel(current_node.get_dataset(), self.alpha)
                if result is not None:
                    current_node.set_kernel(result.get_elements())
                    self.expand_children(current_node, priority_queue)
                else:
                    current_node.set_kernel("LEAF")
                    self.tree.add_leaf_node(current_node)
                    self.update_boundary_with_leaf(current_node)
            else:
                self.expand_children(current_node, priority_queue)

            self.log_tree()

    def expand_children(self, current_node, priority_queue):
        children = []
        for element in current_node.get_kernel():
            reduced_dataset = current_node.get_dataset().clone()
            reduced_dataset.remove_element(element)

            bbvalue = self.calculate_bbvalue(current_node, element, reduced_dataset)
            child_node = HSTreeNode(kernel=None, dataset=reduced_dataset, edge=element, level=current_node.level + 1, bbvalue=bbvalue, parent=current_node)
            current_node.add_child(child_node)

            priority = self.dataset.element_values.get(element, 0)
            children.append((priority, child_node))

        children.sort(reverse=True, key=lambda x: x[0])
        for priority, child_node in children:
            self.add_to_priority_queue(priority_queue, child_node, priority)

    def add_to_priority_queue(self, queue, node, priority):
        heapq.heappush(queue, (-priority, node))

    def calculate_bbvalue(self, current_node, element, dataset):
        assigned_value = dataset.element_values.get(element, 1)
        transformed_value = 1 / assigned_value if assigned_value != 0 else 0
        new_bbvalue = current_node.bbvalue + transformed_value
        return new_bbvalue

    def update_boundary_with_leaf(self, leaf_node):
        leaf_path_measure = self.calculate_path_bbvalue_up_to_root(leaf_node, self.dataset)
        if leaf_path_measure < self.tree.boundary:
            self.tree.boundary = leaf_path_measure

    def calculate_path_bbvalue_up_to_root(self, node, dataset):
        cumulative_bbvalue = 0.0
        current_node = node
        while current_node is not None and current_node.edge is not None:
            element_value = dataset.element_values.get(current_node.edge, 1)
            cumulative_bbvalue += 1 / element_value if element_value != 0 else 0
            current_node = current_node.parent
        return cumulative_bbvalue

    def should_prune(self, node):
        hitting_set_value = self.calculate_path_bbvalue_up_to_root(node, self.dataset)
        if self.tree.boundary == 0:
            return False
        return hitting_set_value >= self.tree.boundary

    def log_tree(self):
        self.tree.print_tree_to_file(dataset=self.dataset)
        self.tree.print_newline()
