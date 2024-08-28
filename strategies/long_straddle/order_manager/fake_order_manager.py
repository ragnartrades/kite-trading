from strategies.long_straddle.order_manager.interface import IOrderManager


class FakeOrderManager(IOrderManager):
    def buy(self, instrument_token: int, qty: int):
        print(f'[FAKE BUYING] - instrument_token: {instrument_token}, qty: {qty}')

    def sell(self, instrument_token: int, qty: int):
        print(f'[FAKE SELLING] - instrument_token: {instrument_token}, qty: {qty}')
        pass


def new_fake_order_manager() -> FakeOrderManager:
    return FakeOrderManager()
