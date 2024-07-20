from abc import ABC, abstractmethod

class Strategy(ABC):
    @abstractmethod
    def find_kernels(self) -> None:
        pass

    def methodForAll(self) -> None:
        print("method that is inherited by strategies")