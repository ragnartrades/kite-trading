from enum import Enum
from . import config as strategy_config
from common import constants as common_constants
from . import utils as strategy_utils
from .classes import TradeExitReason


class TradingState(Enum):
    NOT_STARTED = 'NOT_STARTED'
    LOOKING_FOR_ENTRY = 'LOOKING_FOR_ENTRY'
    LOOKING_FOR_INITIAL_SL = 'LOOKING_FOR_INITIAL_SL'
    SL_UPDATION_IN_PROGRESS = 'SL_UPDATION_IN_PROGRESS'
    EXITED = 'EXITED'


class LiveInfo:
    date: None

    lot_size = None
    lot_qty = None

    stock_symbol = None
    stock_instrument_token = None
    stock_ltp = None

    ce_symbol = None
    ce_instrument_token = None
    ce_ltp = None

    pe_symbol = None
    pe_instrument_token = None
    pe_ltp = None

    tot_ce_pe_ltp = None  # ce_ltp + pe_ltp

    sl = None

    entry_time = None
    entry_stock_price = None
    entry_ce_price = None
    entry_pe_price = None
    entry_tot_price = None  # entry_ce_price + entry_pe_price
    tot_buying_value = None  # (entry_tot_price * lot_size * lot_qty)

    strike_price = None

    exit_time = None
    exit_stock_price = None
    exit_ce_price = None
    exit_pe_price = None
    exit_tot_price = None  # exit_ce_price + exit_pe_price
    tot_selling_value = None  # (exit_tot_price * lot_size * lot_qty)
    exit_reason: TradeExitReason = None

    trading_state = TradingState.NOT_STARTED

    @classmethod
    def current_basic_profit(cls) -> float:
        return cls.exit_tot_price - cls.entry_tot_price

    # @property
    @classmethod
    def current_net_profit(cls) -> float:
        return cls.current_basic_profit() - cls.charges()

    @classmethod
    def charges(cls) -> float:  # APPROXIMATION
        return 2 * 42.550717 + \
            2 * (0.234258 * LiveInfo.lot_qty * LiveInfo.lot_size) + \
            (0.109864 * cls.current_basic_profit())
