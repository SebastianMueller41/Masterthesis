"""
This module sets up logging and defines the PBS class, which extends the Search class.
The PBS class implements a priority-based search algorithm for finding kernels in a dataset.
"""

import logging
from sortedcontainers import SortedList
from src.search.search import Search
from src.tree.hittingsettree import HSTreeNode
from src.structs.logger import setup_logging

# Set up logging for this module
setup_logging()

# Get the logger for this module
ss_logger = logging.getLogger(__name__)

class PBS(Search):
    """
    A class for performing priority-based search (PBS) to find kernels in a dataset.
    """

    def __init__(self, kernelStrategy, dataset, pruner):
        """
        Initialize the PBS with a kernel strategy, dataset, and pruner.

        Args:
            kernelStrategy (KernelStrategy): The strategy used to find kernels.
            dataset (DataSet): The dataset to search.
            pruner (Pruner): The pruner used to prune nodes in the search tree.
        """
        super().__init__(kernelStrategy, dataset, pruner)
        self.queue = self.initialize_queue(pruner)

    def initialize_queue(self, pruner):
        """
        Initialize the priority queue based on the pruner type.

        Args:
            pruner (str): The type of pruner ('UPPER', 'LOWER', or default).

        Returns:
            SortedList: The initialized priority queue.
        """
        if pruner == 'UPPER':
            ss_logger.warning("Upper Pruner, Initializing SortedList with sub_value DESC and cardinality DESC")
            return SortedList(key=lambda x: (-x[0], x[3]))  # Sort desc by sub_value and asc by cardinality
        elif pruner == 'LOWER':
            ss_logger.warning("Lower Pruner, Initializing SortedList with sub_value ASC, path_value DESC, and cardinality ASC")
            return SortedList(key=lambda x: (x[0], -x[1], x[3]))  # Sort by sub_value, then path_value, then cardinality
        else:
            ss_logger.warning("Default Pruner, Initializing SortedList with path_value DESC and cardinality ASC")
            return SortedList(key=lambda x: (-x[1], x[3]))  # Sort desc by path_value and asc by cardinality

    def find_kernels(self) -> None:
        """
        Find kernels in the dataset using priority-based search and populate the search tree.

        Returns:
            None
        """
        ss_logger.debug("FINDING KERNEL")
        initial_node = self.create_initial_node(self.dataset)
        if initial_node is not None:
            self.search(initial_node)
        self.tree.print_tree()
        self.log_tree()

    def create_initial_node(self, dataset):
        """
        Create the initial node for the PBS search tree.

        Args:
            dataset (DataSet): The dataset to create the initial node from.

        Returns:
            HSTreeNode: The initial node of the search tree.
        """
        result = self.kernelStrategy.find_kernel(dataset)
        if result is None:
            ss_logger.info("Initial kernel is None, no need to span the tree.")
            return None
        sub_value = dataset.sum_values()
        initial_node = HSTreeNode(kernel=result.get_elements(), dataset=dataset, path_value=0, parent=None, sub_value=sub_value)
        self.tree.root = initial_node
        return initial_node

    def search(self, root: HSTreeNode):
        """
        Perform the priority-based search (PBS) to explore the search tree and find kernels.

        Args:
            root (HSTreeNode): The root node of the search tree.

        Returns:
            None
        """
        self.add_to_priority_queue(root, self.queue)
        ss_logger.info("Priority search started")

        while self.queue:
            element = self.queue.pop(0)
            ss_logger.debug(f"Queue: {self.queue}")
            sub_value, path_value, current_node, cardinality = element
            ss_logger.debug(f"Popped element: {current_node}, with sub value: {sub_value}, path value: {path_value}, cardinality: {cardinality}")
            
            if self.pruner.should_prune(current_node):
                current_node.kernel = "PRUNED"
                current_node.set_pruned()
                self.pruned_nodes.append(current_node)
                continue

            if current_node.get_kernel() is None:
                result = self.kernelStrategy.find_kernel(current_node.get_dataset())
                if result is not None:
                    current_node.set_kernel(result.get_elements())
                    self.expand_children(current_node)
                else:
                    current_node.set_kernel("LEAF")
                    self.tree.add_leaf_node(current_node)
                    self.leaf_nodes.append(current_node)
                    self.pruner.update_boundary_with_leaf(current_node)
            else:
                self.expand_children(current_node)

            self.log_tree()

    def expand_children(self, parent):
        """
        Expand the children of a parent node and add them to the priority queue.

        Args:
            parent (HSTreeNode): The parent node to expand.

        Returns:
            None
        """
        child_nodes = self.brancher.expand_children(parent)
        ss_logger.info(f"Child nodes from brancher: {child_nodes}")
        for child_node in child_nodes:
            if child_node.get_kernel() is None:
                result = self.kernelStrategy.find_kernel(child_node.get_dataset())
                if result is not None:
                    child_node.set_kernel(result.get_elements())
            self.add_to_priority_queue(child_node, self.queue)

    def add_to_priority_queue(self, node, queue):
        """
        Add a node to the priority queue.

        Args:
            node (HSTreeNode): The node to add to the queue.
            queue (SortedList): The priority queue.

        Returns:
            None
        """
        cardinality = len(self.tree.get_hitting_set_for_leaf(node).get_elements())
        queue.add((node.sub_value, node.path_value, node, cardinality))
        ss_logger.debug(f"Added node to queue with sub_value: {node.sub_value}, path_value: {node.path_value}, cardinality: {cardinality}")
        ss_logger.debug(f"Priority Queue: {queue}")
