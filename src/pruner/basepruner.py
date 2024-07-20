# src/tree/base_pruner.py

from abc import ABC, abstractmethod

class BasePruner(ABC):
    def __init__(self, tree):
        self.tree = tree
        self.optimal_reached = False
        self.best_solution = None

    @abstractmethod
    def should_prune(self, node):
        pass

    @abstractmethod
    def update_boundary_with_leaf(self, leaf_node):
        pass
