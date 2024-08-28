import threading
import time as time
from datetime import datetime
from strategies.long_straddle import config as strategy_config
from strategies.long_straddle.classes import TradeExitReason
from strategies.long_straddle.live_info import LiveInfo, TradingState
from strategies.long_straddle.order_manager.straddle_position_manager import straddle_position_manager


def async_spawn_take_exit_process():
    print('[ASYNC SPAWN] - async_spawn_take_exit_process ...')

    thread = threading.Thread(target=keep_on_checking_for_exit_and_if_possible_do_it)
    thread.start()


def keep_on_checking_for_exit_and_if_possible_do_it():
    while True:
        cur_time = datetime.now().time()

        if LiveInfo.trading_state == TradingState.NOT_STARTED:
            time.sleep(1)
            continue

        elif cur_time > strategy_config.MAX_TRADE_TIME:
            straddle_position_manager.TakeExit(TradeExitReason.MAX_TRADE_TIME_CROSSED)

        elif LiveInfo.trading_state == TradingState.LOOKING_FOR_ENTRY:
            if cur_time <= strategy_config.MAX_ENTRY_TIME:
                time.sleep(1)
                continue

            straddle_position_manager.TakeExit(TradeExitReason.TIME_ELAPSED_NO_ENTRY)

        elif LiveInfo.trading_state == TradingState.LOOKING_FOR_INITIAL_SL:
            if more_than_max_loss_capping():
                straddle_position_manager.TakeExit(TradeExitReason.MAX_LOSS_WHILE_LOOKING_FOR_INITIAL_SL)

            if cur_time <= strategy_config.MAX_ENTRY_TIME:
                time.sleep(1)
                continue

            straddle_position_manager.TakeExit(TradeExitReason.TIME_ELAPSED_WHILE_LOOKING_FOR_INITIAL_SL)

        elif LiveInfo.trading_state == TradingState.SL_UPDATION_IN_PROGRESS:
            if more_than_max_loss_capping():
                straddle_position_manager.TakeExit(TradeExitReason.MAX_LOSS_WHILE_TRAILING_SL)

            if LiveInfo.tot_ce_pe_ltp <= LiveInfo.sl:
                straddle_position_manager.TakeExit(TradeExitReason.SL_HIT)


def more_than_max_loss_capping() -> bool:
    current_profit: float = LiveInfo.current_net_profit()

    if current_profit <= 0 and abs(current_profit) >= strategy_config.MAX_LOSS_PERCENTAGE:
        return True

    return False

