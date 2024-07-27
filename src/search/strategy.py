from abc import ABC, abstractmethod

class Strategy(ABC):
    @abstractmethod
    def find_kernels(self) -> None:
        pass