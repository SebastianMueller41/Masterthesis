import logging
from src.search.strategy import Strategy
from src.search.search import Search
from src.search.dfs import DFS
from src.search.bfs import BFS
from src.structs.logger import setup_logging

# Set up logging for this module
setup_logging()

# Get the logger for this module
ss_logger = logging.getLogger(__name__)

class HYS(Strategy, Search):
    def __init__(self, kernelStrategy, dataset, brancher, pruner, alpha, strategy_param):
        Search.__init__(self, kernelStrategy, dataset, alpha, strategy_param)
        self.first_leaf_found = False
        self.dfs_search = DFS(kernelStrategy, dataset, brancher, pruner, alpha, strategy_param)
        self.bfs_search = BFS(kernelStrategy, dataset, brancher, pruner, alpha, strategy_param)

    def find_kernels(self) -> None:
        if self.first_leaf_found:
            ss_logger.info(f"First LEAF found, switching to BFS")
            self.tree = self.dfs_search.tree
            self.bfs_search.tree = self.tree
            self.bfs_search.find_kernels()
            self.tree = self.dfs_search.tree
        else:
            self.dfs_search.find_kernels()
            self.tree = self.dfs_search.tree

