import threading
import time
from strategies.long_straddle import config as strategy_config

from strategies.long_straddle.live_info import LiveInfo, TradingState


def async_spawn_stoploss_managing_process():
    print('[ASYNC SPAWN] - async_spawn_stoploss_managing_process ...')

    thread = threading.Thread(target=manage_stoploss)
    thread.start()


def manage_stoploss():
    while LiveInfo.sl is None:
        time.sleep(1)

    while LiveInfo.trading_state != TradingState.EXITED:
        new_sl = calculate_new_possible_stoploss()
        LiveInfo.sl = max(LiveInfo.sl, new_sl)

        time.sleep(1)


def calculate_new_possible_stoploss() -> float:
    point_diff = None

    if strategy_config.SL_DEVIATION_TYPE == 'ABSOLUTE':
        point_diff = strategy_config.SL_DEVIATION
    elif strategy_config.SL_DEVIATION_TYPE == 'PERCENTAGE':
        point_diff = (LiveInfo.tot_ce_pe_ltp * strategy_config.SL_DEVIATION) / 100

    return LiveInfo.tot_ce_pe_ltp - point_diff
