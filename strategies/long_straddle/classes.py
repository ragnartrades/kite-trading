from typing import TypedDict


class TickerData(TypedDict):
    tradable: bool
    mode: str
    instrument_token: int
    last_price: float
