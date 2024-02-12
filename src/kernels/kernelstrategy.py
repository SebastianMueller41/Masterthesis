from abc import ABC, abstractmethod

## Strategy interface 
class KernelStrategy(ABC):
    @abstractmethod
    def find_kernel(self, dataset, alpha):
        pass

    def methodForAll(self) -> None:
        print("method that is inherited by strategies")