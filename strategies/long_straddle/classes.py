from enum import Enum
from typing import TypedDict


class TickerData(TypedDict):
    tradable: bool
    mode: str
    instrument_token: int
    last_price: float


class TradeExitReason(Enum):
    MAX_TRADE_TIME_CROSSED = 'MAX_TRADE_TIME_CROSSED'
    TIME_ELAPSED_NO_ENTRY = 'TIME_ELAPSED_NO_ENTRY'
    MAX_LOSS_WHILE_LOOKING_FOR_INITIAL_SL = 'MAX_LOSS_WHILE_LOOKING_FOR_INITIAL_SL'
    TIME_ELAPSED_WHILE_LOOKING_FOR_INITIAL_SL = 'TIME_ELAPSED_WHILE_LOOKING_FOR_INITIAL_SL'
    MAX_LOSS_WHILE_TRAILING_SL = 'MAX_LOSS_WHILE_TRAILING_SL'
    SL_HIT = 'SL_HIT'
