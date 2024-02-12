import sys
from src.structs.dataset import DataSet
from src.structs.hittingsettree import HSTreeNode, HittingSetTree
from src.kernels.kernelstrategy import KernelStrategy
from .strategy import Strategy

class BFS(Strategy):
    
    def __init__(self, kernelStrategy: KernelStrategy, dataset: DataSet, alpha):
        self.kernelStrategy = kernelStrategy
        self.dataset = dataset
        self.alpha = alpha
    
    def find_kernels(self) -> None:
        self.tree = HittingSetTree()
        self.span_tree_with_kernels(self.dataset, self.alpha)
        
        ## print afterwards
        self.tree.print_tree()
            
            
        
    def span_tree_with_kernels(self, dataset, alpha, parent=None, removed=None):
        result = self.kernelStrategy.find_kernel(dataset, alpha)
        if result is not None:
            found_kernel = result.get_elements()
            if not found_kernel:
                # If found_kernel is empty, we've hit a leaf node
                child_node = HSTreeNode(kernel="LEAF")
                parent.add_child(child_node)
                return
            
            if parent is None:
                # set root to first kernel
                self.tree.root.set_kernel(found_kernel)
                parent = self.tree.root
            else: 
                child_node = HSTreeNode(kernel=found_kernel, edge=removed)
                parent.add_child(child_node)
                parent = child_node
            
            #logging
            self.tree.print_tree_to_file()    
            self.tree.print_newline()


            for element in found_kernel:
                # Create a copy of dataset without the current element
                reduced_dataset = dataset.clone()
                reduced_dataset.remove_element(element)                

                # Recursively span the tree
                self.span_tree_with_kernels(reduced_dataset, alpha, parent, element)
        else:
            child_node = HSTreeNode(kernel="LEAF", edge=removed)
            parent.add_child(child_node)
            #logging
            self.tree.print_tree_to_file()    
            self.tree.print_newline()