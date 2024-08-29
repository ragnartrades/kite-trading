from enum import Enum
from datetime import date, time
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
    REPORT_COMPLETED = 'REPORT_COMPLETED'


class LiveInfo:
    date: date = None

    lot_size: int = None
    lot_qty: int = None

    stock_symbol: str = None
    stock_instrument_token: int = None
    stock_ltp: float = None

    ce_symbol: str = None
    ce_instrument_token: int = None
    ce_ltp: float = None

    pe_symbol: str = None
    pe_instrument_token: int = None
    pe_ltp: float = None

    tot_ce_pe_ltp: float = None  # ce_ltp + pe_ltp

    sl: float = None

    entry_time: time = None
    entry_stock_price: float = None
    entry_ce_price: float = None
    entry_pe_price: float = None
    entry_tot_price: float = None  # entry_ce_price + entry_pe_price
    tot_buying_value: float = None  # (entry_tot_price * lot_size * lot_qty)

    strike_price = None

    exit_time: time = None
    exit_stock_price: float = None
    exit_ce_price: float = None
    exit_pe_price: float = None
    exit_tot_price: float = None  # exit_ce_price + exit_pe_price
    tot_selling_value: float = None  # (exit_tot_price * lot_size * lot_qty)
    exit_reason: TradeExitReason = None

    trading_state: TradingState = TradingState.NOT_STARTED

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

    @classmethod
    def to_dict(cls):
        def serialize_date(d):
            return d.strftime("%Y-%m-%d") if d else None

        def serialize_time(t):
            return t.strftime("%H:%M:%S") if t else None

        def serialize_enum(e):
            return e.value if e else None

        return {
            "date": serialize_date(cls.date),
            "lot_size": cls.lot_size,
            "lot_qty": cls.lot_qty,
            "stock_symbol": cls.stock_symbol,
            "stock_instrument_token": cls.stock_instrument_token,
            "stock_ltp": cls.stock_ltp,
            "ce_symbol": cls.ce_symbol,
            "ce_instrument_token": cls.ce_instrument_token,
            "ce_ltp": cls.ce_ltp,
            "pe_symbol": cls.pe_symbol,
            "pe_instrument_token": cls.pe_instrument_token,
            "pe_ltp": cls.pe_ltp,
            "tot_ce_pe_ltp": cls.tot_ce_pe_ltp,
            "sl": cls.sl,
            "entry_time": serialize_time(cls.entry_time),
            "entry_stock_price": cls.entry_stock_price,
            "entry_ce_price": cls.entry_ce_price,
            "entry_pe_price": cls.entry_pe_price,
            "entry_tot_price": cls.entry_tot_price,
            "tot_buying_value": cls.tot_buying_value,
            "strike_price": cls.strike_price,
            "exit_time": serialize_time(cls.exit_time),
            "exit_stock_price": cls.exit_stock_price,
            "exit_ce_price": cls.exit_ce_price,
            "exit_pe_price": cls.exit_pe_price,
            "exit_tot_price": cls.exit_tot_price,
            "tot_selling_value": cls.tot_selling_value,
            "exit_reason": serialize_enum(cls.exit_reason),
            "trading_state": serialize_enum(cls.trading_state),
        }
