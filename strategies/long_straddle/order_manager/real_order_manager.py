from strategies.long_straddle.order_manager.interface import IOrderManager


class RealOrderManager(IOrderManager):
    def buy(self, instrument_token: int, qty: int):
        pass

    def sell(self, instrument_token: int, qty: int):
        pass


def new_real_order_manager() -> RealOrderManager:
    return RealOrderManager()
