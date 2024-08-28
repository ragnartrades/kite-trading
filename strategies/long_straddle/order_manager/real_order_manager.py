from strategies.long_straddle.order_manager.interface import IOrderManager


class RealOrderManager(IOrderManager):
    def buy(self):
        pass

    def sell(self):
        pass


def new_real_order_manager() -> RealOrderManager:
    return RealOrderManager()
