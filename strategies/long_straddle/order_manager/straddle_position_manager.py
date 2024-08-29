import time

from strategies.long_straddle import config as strategy_config
from common.utils import MONTH_NUMBER_TO_OPTION_MONTH_SYMBOL_MAP
from strategies.long_straddle.classes import TradeExitReason
from strategies.long_straddle.config import STOCK_NAME
from strategies.long_straddle.live_info import LiveInfo, TradingState
from strategies.long_straddle.order_manager import get_new_order_manager
from strategies.long_straddle.order_manager.interface import IOrderManager
from common.data import Data
from datetime import datetime


class StraddlePositionManager:
    def __init__(self):
        self.order_manager: IOrderManager = get_new_order_manager()
        self.ce_instrument_symbol = None
        self.pe_instrument_symbol = None
        self.ce_instrument_token = None
        self.pe_instrument_token = None

    def MakeEntry(self, strike_price: int):
        self.ce_instrument_symbol = self._get_instrument_symbol(strike_price, 'CE')
        self.pe_instrument_symbol = self._get_instrument_symbol(strike_price, 'PE')
        self.ce_instrument_token = self._get_NFO_instrument_token_from_symbol(self.ce_instrument_symbol)
        self.pe_instrument_token = self._get_NFO_instrument_token_from_symbol(self.pe_instrument_symbol)

        self.order_manager.buy(self.ce_instrument_token, LiveInfo.lot_size * LiveInfo.lot_qty)
        self.order_manager.buy(self.pe_instrument_token, LiveInfo.lot_size * LiveInfo.lot_qty)

        LiveInfo.ce_symbol = self.ce_instrument_symbol
        LiveInfo.pe_symbol = self.pe_instrument_symbol
        LiveInfo.ce_instrument_token = self.ce_instrument_token
        LiveInfo.pe_instrument_token = self.pe_instrument_token

        # wait while LiveInfo.ce_ltp and LiveInfo.pe_ltp is not fetched
        while LiveInfo.ce_ltp is None or LiveInfo.pe_ltp is None or \
                LiveInfo.tot_ce_pe_ltp is None:
            time.sleep(1)

        LiveInfo.strike_price = strike_price
        LiveInfo.entry_time = datetime.now().time()
        LiveInfo.entry_stock_price = LiveInfo.stock_ltp
        LiveInfo.entry_ce_price = LiveInfo.ce_ltp
        LiveInfo.entry_pe_price = LiveInfo.pe_ltp
        LiveInfo.entry_tot_price = LiveInfo.tot_ce_pe_ltp
        LiveInfo.tot_buying_value = LiveInfo.tot_ce_pe_ltp * LiveInfo.lot_size * LiveInfo.lot_qty

        LiveInfo.trading_state = TradingState.LOOKING_FOR_INITIAL_SL

    def TakeExit(self, trade_exit_reason: TradeExitReason):
        self.order_manager.sell(self.ce_instrument_token, LiveInfo.lot_size * LiveInfo.lot_qty)
        self.order_manager.sell(self.pe_instrument_token, LiveInfo.lot_size * LiveInfo.lot_qty)

        LiveInfo.exit_time = datetime.now().time()
        LiveInfo.exit_stock_price = LiveInfo.stock_ltp
        LiveInfo.exit_ce_price = LiveInfo.ce_ltp
        LiveInfo.exit_pe_price = LiveInfo.pe_ltp
        LiveInfo.exit_tot_price = LiveInfo.tot_ce_pe_ltp
        LiveInfo.tot_selling_value = LiveInfo.tot_ce_pe_ltp * LiveInfo.lot_size * LiveInfo.lot_qty
        LiveInfo.exit_reason = trade_exit_reason

        LiveInfo.trading_state = TradingState.EXITED

    @staticmethod
    def _get_instrument_symbol(strike_price: int, option_type: str) -> str:
        today_date_time = datetime.today()

        year = today_date_time.year
        last_two_digit_in_year = year % 2000

        month_str = strategy_config.TRADING_MONTH

        return f'{STOCK_NAME}{last_two_digit_in_year}{month_str}{int(strike_price)}{option_type}'

    @staticmethod
    def _get_NFO_instrument_token_from_symbol(instrument_symbol: str) -> int:
        instrument_data = Data.nfo_instruments[instrument_symbol]
        return instrument_data['instrument_token']


def new_straddle_position_manager() -> StraddlePositionManager:
    return StraddlePositionManager()


straddle_position_manager: StraddlePositionManager = new_straddle_position_manager()
