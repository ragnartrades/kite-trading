from strategies.long_straddle.classes import TradeExitReason
from strategies.long_straddle.order_manager import get_new_order_manager
from strategies.long_straddle.order_manager.interface import IOrderManager


class StraddlePositionManager:
    def __init__(self):
        self.order_manager: IOrderManager = get_new_order_manager()

    def MakeEntry(self):
        pass

    def TakeExit(self, trade_exit_reason: TradeExitReason):
        pass


def new_straddle_position_manager() -> StraddlePositionManager:
    return StraddlePositionManager()


straddle_position_manager: StraddlePositionManager = new_straddle_position_manager()
