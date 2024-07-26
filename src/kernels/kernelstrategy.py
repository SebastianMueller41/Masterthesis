from abc import ABC, abstractmethod

## Strategy interface 
class KernelStrategy(ABC):
    @abstractmethod
    def find_kernel(self, dataset):
        pass