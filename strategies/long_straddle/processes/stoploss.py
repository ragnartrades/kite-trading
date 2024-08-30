import threading
import time
from strategies.long_straddle import config as strategy_config

from strategies.long_straddle.live_info import LiveInfo, TradingState


def async_spawn_stoploss_managing_process():
    print('[ASYNC SPAWN] - async_spawn_stoploss_managing_process ...')

    thread = threading.Thread(target=manage_stoploss)
    thread.start()


def calculate_new_possible_stoploss() -> float:
    return LiveInfo.tot_ce_pe_ltp - strategy_config.SL_DEVIATION


def get_min_tot_ce_pe_price_for_min_profit(
        entry_tot_price: float,
        min_profit_percentage: float,
) -> float:
    return entry_tot_price * (1 + float(min_profit_percentage)/100)


def try_setting_initial_Stoploss() -> bool:
    if LiveInfo.entry_tot_price is None or LiveInfo.tot_ce_pe_ltp is None:
        return False

    min_ce_pe_price_for_min_profit: float = \
        get_min_tot_ce_pe_price_for_min_profit(
            LiveInfo.entry_tot_price,
            strategy_config.MIN_PROFIT_PERCENTAGE,
        )

    sl_deviation_point: float = strategy_config.SL_DEVIATION

    min_ce_pe_price_for_min_profit_after_sl_deviation = \
        min_ce_pe_price_for_min_profit + sl_deviation_point

    if LiveInfo.tot_ce_pe_ltp >= min_ce_pe_price_for_min_profit_after_sl_deviation:
        LiveInfo.sl = min_ce_pe_price_for_min_profit
        LiveInfo.trading_state = TradingState.SL_UPDATION_IN_PROGRESS

        return True

    return False


def manage_stoploss():
    while LiveInfo.sl is None:
        is_initial_sl_created: bool = try_setting_initial_Stoploss()
        if is_initial_sl_created:
            break

        time.sleep(1)

    while LiveInfo.trading_state != TradingState.EXITED:
        new_sl = calculate_new_possible_stoploss()
        LiveInfo.sl = max(LiveInfo.sl, new_sl)

        time.sleep(1)


