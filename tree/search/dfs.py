from .strategy import Strategy

class DFS(Strategy):
    def find_kernels(self) -> None:
        print("Found DFS kernel")
        self.methodForAll()