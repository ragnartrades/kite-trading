from strategies.long_straddle.order_manager.interface import IOrderManager


class FakeOrderManager(IOrderManager):
    def buy(self):
        pass

    def sell(self):
        pass


def new_fake_order_manager() -> FakeOrderManager:
    return FakeOrderManager()
