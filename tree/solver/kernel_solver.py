from search.bfs import BFS
from search.strategy import Strategy

class KernelSolver:
    def __init__(self, strategy: Strategy = None):
        self.strategy = strategy if strategy is not None else BFS()

    def executeStrategy(self) -> str:
        return self.strategy.find_kernels()