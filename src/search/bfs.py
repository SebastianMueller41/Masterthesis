from collections import deque
from src.search.strategy import Strategy
from src.search.search import Search
from src.structs.hittingsettree import HSTreeNode

class BFS(Strategy, Search):
    def __init__(self, kernelStrategy, dataset, alpha, strategy_param):
        Search.__init__(self, kernelStrategy, dataset, alpha, strategy_param)

    def find_kernels(self) -> None:
        self.bfs(self.dataset, self.alpha)
        self.tree.print_tree()
        self.log_tree()

    def bfs(self, dataset, alpha):
        queue = deque()
        result = self.kernelStrategy.find_kernel(dataset, alpha)
        if result is not None:
            self.tree.root = HSTreeNode(kernel=result.get_elements(), dataset=dataset, bbvalue=0, parent=None)
            queue.append(self.tree.root)

        while queue:
            current_node = queue.popleft()
            if self.should_prune(current_node):
                current_node.kernel = "PRUNED"
                current_node.set_pruned()
                continue

            for element in current_node.get_kernel():
                reduced_dataset = current_node.get_dataset().clone()
                reduced_dataset.remove_element(element)

                bbvalue = self.calculate_bbvalue(current_node, element, reduced_dataset)
                child_node = HSTreeNode(kernel=None, dataset=reduced_dataset, edge=element, level=current_node.level + 1, bbvalue=bbvalue, parent=current_node)
                current_node.add_child(child_node)

                result = self.kernelStrategy.find_kernel(reduced_dataset, alpha)
                if result is not None:
                    child_node.set_kernel(result.get_elements())
                    queue.append(child_node)
                else:
                    child_node.set_kernel("LEAF")
                    self.tree.add_leaf_node(child_node)
                    self.update_boundary_with_leaf(child_node)

        self.log_tree()
