import logging
from src.search.search import Search
from src.tree.hittingsettree import HSTreeNode
from src.structs.logger import setup_logging

# Set up logging for this module
setup_logging()

# Get the logger for this module
ss_logger = logging.getLogger(__name__)

class PBS(Search):
    def __init__(self, kernelStrategy, dataset, pruner):
        super().__init__(kernelStrategy, dataset, pruner)
        self.brancher.initialize_queue(pruner)

    def find_kernels(self) -> None:
        initial_node = self.create_initial_node(self.dataset)
        ss_logger.info("Initial kernel found!")
        if initial_node is None:
            ss_logger.info("Initial kernel is None, no need to span the tree.")
            return
        self.search(initial_node)
        self.tree.print_tree()
        self.log_tree()

    def create_initial_node(self, dataset):
        result = self.kernelStrategy.find_kernel(dataset)
        if result is None:
            return None
        sub_value = dataset.sum_values()
        initial_node = HSTreeNode(kernel=result.get_elements(), dataset=dataset, path_value=0, parent=None, sub_value=sub_value)
        self.tree.root = initial_node
        return initial_node

    def search(self, root: HSTreeNode):
        self.brancher.add_to_priority_queue(root)
        ss_logger.info(f"Priority search started")

        while self.brancher.queue:
            element = self.brancher.queue.pop(0)
            ss_logger.info(f"Queue: {self.brancher.queue}")
            if element is None:
                ss_logger.error("Attempted to pop from an empty heap")
                break
            node_path = self.tree.get_hitting_set_for_leaf(element[1]).get_elements()
            ss_logger.debug(f"Popped element: {element[1].edge}, with value: {element[0]}, Path: {node_path}")
            sub_value, current_node, cardinality = element
            if self.pruner.should_prune(current_node):
                ss_logger.info("Node pruned")
                current_node.kernel = "PRUNED"
                self.pruned_nodes.append(current_node)
                current_node.set_pruned()
                continue
            ss_logger.info(f"Not prune path: {node_path} with value: {element[0]}!")
            if current_node.get_kernel() is None:
                result = self.kernelStrategy.find_kernel(current_node.get_dataset())
                if result is not None:
                    ss_logger.info(f"Setting kernel to: {result.get_elements()}")
                    current_node.set_kernel(result.get_elements())
                    self.brancher.expand_children(current_node)
                else:
                    ss_logger.debug(f"LEAF FOUND! Calling Update Boundary wird {current_node.sub_value}")
                    current_node.set_kernel("LEAF")
                    self.tree.add_leaf_node(current_node)
                    self.leaf_nodes.append(current_node)
                    self.pruner.update_boundary_with_leaf(current_node)
            else:
                self.brancher.expand_children(current_node)

            self.log_tree()