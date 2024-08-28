from abc import ABC, abstractmethod


class IOrderManager(ABC):
    @abstractmethod
    def buy(self): ...
    @abstractmethod
    def sell(self): ...
