from enum import Enum


class TradeReport(Enum):
    date: str
    lot_size: int
    lot_qty: int

    entry_time: str
    entry_stock_point: float
    entry_ce_price: float
    entry_pe_price: float
    entry_tot_price: float
    tot_buying_value: float

    strike_price: int

    exit_time: str
    exit_stock_point: float
    exit_ce_price: float
    exit_pe_price: float
    exit_tot_price: float
    tot_selling_value: float

    per_unit_basic_profit: float
    tot_basic_profit: float
    all_charges: float
    net_profit: float
    net_profit_percentage: float
    exit_reason: str


class TradeReportHandler:
    @classmethod
    def generate_report(cls) -> TradeReport:
        pass

    @classmethod
    def write_report(cls, report: TradeReport):
        pass
