from src.search.strategy import Strategy

class KernelSolver:
    def __init__(self, strategy: Strategy):
        self.strategy = strategy

    def solve(self) -> None:
        self.strategy.find_kernels()