from .strategy import Strategy

class HybridSearch(Strategy):
    def find_kernels(self) -> None:
        print("Found Hybrid kernel")
        self.methodForAll()