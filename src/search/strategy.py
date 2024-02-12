from abc import ABC, abstractmethod

from src.kernels.kernelstrategy import KernelStrategy
from src.structs.dataset import DataSet

## Strategy interface 
class Strategy(ABC):
    @abstractmethod
    def find_kernels(self, kernelStrategy: KernelStrategy, dataset: DataSet, alpha) -> None:
        pass

    def methodForAll(self) -> None:
        print("method that is inherited by strategies")