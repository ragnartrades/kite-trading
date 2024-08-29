import threading
import time

from strategies.long_straddle.live_info import LiveInfo, TradingState
from strategies.long_straddle.reports.report import TradeReportHandler, TradeReport


def async_spawn_profit_report_maker():
    print('[ASYNC SPAWN] - async_spawn_profit_report_maker ...')

    thread = threading.Thread(target=generate_trade_report)
    thread.start()


def generate_trade_report():
    while LiveInfo.trading_state != TradingState.EXITED:
        time.sleep(1)

    print('generating trade report ...')
    trade_report: TradeReport = TradeReportHandler.generate_report()

    print('writing trade report ...')
    TradeReportHandler.write_report(trade_report)

    LiveInfo.trade_state = TradingState.REPORT_COMPLETED
