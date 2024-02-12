from src.kernels.kernelstrategy import KernelStrategy
from src.structs.dataset import DataSet
from src.structs.hittingsettree import HSTreeNode, HittingSetTree
from .strategy import Strategy

from collections import deque

class HybridSearch(Strategy):
    
    def __init__(self, kernelStrategy: KernelStrategy, dataset: DataSet, alpha):
        self.kernelStrategy = kernelStrategy
        self.dataset = dataset
        self.alpha = alpha
    
    def find_kernels(self) -> None:
        self.tree = HittingSetTree()
        self.dfs(self.dataset, self.alpha)
        self.bfs(self.alpha, self.tree.root)

        ## print afterwards
        self.tree.print_tree()
        
    def dfs(self, dataset, alpha, parent:HSTreeNode=None):
        #get root
        if parent is None:
            result = self.kernelStrategy.find_kernel(dataset, alpha)
            self.tree.root = HSTreeNode(kernel=result.get_elements(), dataset=dataset)
            self.dfs(self.tree.root.dataset, alpha, self.tree.root)
        else:
            for element in parent.get_kernel():
                reduced_dataset = parent.get_dataset().clone()
                reduced_dataset.remove_element(element)
                parent.add_child(HSTreeNode(dataset=reduced_dataset, edge=element))
            curr = parent.children[0]
            result = self.kernelStrategy.find_kernel(curr.get_dataset(), alpha)
            if result is not None:
                curr.set_kernel(result.get_elements())
                
                self.log_tree()
                
                self.dfs(curr.get_dataset(), alpha, curr)
            else:
                curr.set_kernel("LEAF")
                self.tree.boundary = curr.level
                
                self.log_tree()
                
    def bfs(self, alpha, root:HSTreeNode):
        #enqueue root as first element
        queue = deque([root])
        
        while queue:
            current_node = queue.popleft()
            # if no kernel is calculated yet (based on dfs which produces child) do it, if boundary is leq
            if not current_node.get_kernel() and current_node.level <= self.tree.boundary:
                result = self.kernelStrategy.find_kernel(current_node.get_dataset(), alpha)
                if result is not None:
                    #kernel found, need to generate children
                    current_node.set_kernel(result.get_elements())
                    
                    self.log_tree()
                    
                    for element in current_node.get_kernel():
                        reduced_dataset = current_node.get_dataset().clone()
                        reduced_dataset.remove_element(element)
                        #only add nodes that are below the boundary, can still be leafs
                        if current_node.level + 1 <= self.tree.boundary:
                            current_node.add_child(HSTreeNode(dataset=reduced_dataset, edge=element))
                    
                    #self.dfs(current_node.get_dataset(), alpha, curr)
                else:
                    current_node.set_kernel("LEAF")
                    self.tree.boundary = current_node.level
                    
                    self.log_tree()
            
            # add childs to end of queue
            queue.extend(current_node.children)
            
    def log_tree(self):
        self.tree.print_tree_to_file()    
        self.tree.print_newline()