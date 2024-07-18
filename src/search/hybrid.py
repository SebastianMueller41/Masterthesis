import logging
from src.search.strategy import Strategy
from src.search.search import Search
from src.search.dfs import DFS
from src.search.bfs import BFS

class HybridSearch(Strategy, Search):
    def __init__(self, kernelStrategy, dataset, alpha, strategy_param):
        Search.__init__(self, kernelStrategy, dataset, alpha, strategy_param)
        self.first_leaf_found = False
        self.dfs_search = DFS(kernelStrategy, dataset, alpha, strategy_param)
        self.bfs_search = BFS(kernelStrategy, dataset, alpha, strategy_param)

    def find_kernels(self) -> None:
        if self.first_leaf_found:
            logging.info(f"First LEAF found, switching to BFS")
            self.tree = self.dfs_search.tree
            self.bfs_search.tree = self.tree
            self.bfs_search.find_kernels()
        else:
            self.dfs_search.find_kernels()
            self.first_leaf_found = self.dfs_search.tree.leaf_nodes
