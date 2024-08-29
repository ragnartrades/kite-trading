import threading
import time
from strategies.long_straddle import config as strategy_config
from strategies.long_straddle.live_info import LiveInfo, TradingState
from strategies.long_straddle.order_manager.straddle_position_manager import straddle_position_manager


def async_spawn_make_entry_process():
    print('[ASYNC SPAWN] - async_spawn_make_entry_process ...')

    thread = threading.Thread(target=try_making_entry_and_try_setting_initial_stoploss)
    thread.start()


def try_making_entry_and_try_setting_initial_stoploss():
    print('[ENTRY] - Waiting for making entry ...')

    while LiveInfo.stock_ltp is None:
        time.sleep(1)

    LiveInfo.trading_state = TradingState.LOOKING_FOR_ENTRY

    while LiveInfo.trading_state != TradingState.EXITED:
        should_make_entry, strike_price = entry_condition_met(LiveInfo.stock_ltp)
        if should_make_entry:
            print(f'[ENTRY] - Got suitable strike price {strike_price} for entry. '
                  f'Now make an entry ... ')

            straddle_position_manager.MakeEntry(strike_price)

            print(f'[ENTRY] - successful entry made at strike price {strike_price} !!!')

            break
        else:
            time.sleep(1)


def entry_condition_met(stock_ltp: float) -> (bool, int):
    if stock_ltp is None:
        return False, None

    return is_near_to_100_multiple_ATM(stock_ltp)


def is_near_to_100_multiple_ATM(stock_ltp: float) -> (bool, int):
    lower_strike_price = (stock_ltp // 100) * 100
    upper_strike_price = lower_strike_price + 100

    if stock_ltp <= lower_strike_price + strategy_config.MAX_ENTRY_ATM_PRICE_DEVIATION:
        return True, int(lower_strike_price)
    elif stock_ltp >= upper_strike_price - strategy_config.MAX_ENTRY_ATM_PRICE_DEVIATION:
        return True, int(upper_strike_price)

    return False, None

