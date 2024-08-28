from abc import ABC, abstractmethod


class IOrderManager(ABC):
    @abstractmethod
    def buy(self, instrument_token: int, qty: int): ...
    @abstractmethod
    def sell(self, instrument_token: int, qty: int): ...
