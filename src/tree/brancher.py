import heapq
from src.pruner.lower_max import LowerPruner
from src.pruner.upper_min import UpperPruner
from src.tree.basebrancher import BaseBrancher
from src.tree.hittingsettree import HSTreeNode

class Brancher(BaseBrancher):
    def __init__(self, dataset, tree, pruner):
        super().__init__(dataset, tree, pruner)
        self.min_heap = []
        self.max_heap = []

    def expand_children(self, current_node, priority_queue):
        children = []
        for element in current_node.get_kernel():
            reduced_dataset = current_node.get_dataset().clone()
            reduced_dataset.remove_element(element)
            bbvalue = self.calculate_bbvalue(current_node)
            self.tree_logger.info(f"Calculated bbvalue = {bbvalue}")
            child_node = HSTreeNode(kernel=None, dataset=reduced_dataset, edge=element, level=current_node.level + 1, bbvalue=bbvalue, parent=current_node)
            current_node.add_child(child_node)

            priority = self.dataset.get_element_value(element)
            self.tree_logger.debug(f"Adding node to queue with value: {priority}")
            children.append((priority, child_node))

        children.sort(reverse=True, key=lambda x: x[0])
        for priority, child_node in children:
            self.add_to_priority_queue(child_node, priority)

    def add_to_priority_queue(self, node, priority):
        heapq.heappush(self.min_heap, (priority, node))
        heapq.heappush(self.max_heap, (-priority, node))

    def pop_min_element(self):
        if self.min_heap:
            return heapq.heappop(self.min_heap)
        return None

    def pop_max_element(self):
        if self.max_heap:
            # Pop from max_heap (negate the priority back)
            priority, node = heapq.heappop(self.max_heap)
            return (-priority, node)
        return None

    def pop_element(self, pruner):
        if isinstance(pruner, UpperPruner):
            return self.pop_min_element()
        elif isinstance(pruner, LowerPruner):
            return self.pop_max_element()
        else:
            if pruner.optimal_reached:
                return self.pop_min_element()
            else:
                return self.pop_max_element()
