from abc import ABC, abstractmethod

## Strategy interface 
class RemainderStrategy(ABC):
    @abstractmethod
    def find_remainder(self, dataset, alpha):
        pass

    def methodForAll(self) -> None:
        print("method that is inherited by strategies")