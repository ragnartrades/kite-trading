import json
import threading
import time
from enum import Enum
from common.constants import *
from kiteconnect import KiteConnect, KiteTicker
from common import utils, configs
from typing import TypedDict


class TradeState(Enum):
    NOT_STARTED = 'NOT_STARTED'
    LOOKING_FOP_ENTRY = 'LOOKING_FOP_ENTRY'
    POSITION_CREATED = 'POSITION_CREATED'
    WAITING_FOR_INITIAL_STOPLOSS = 'WAITING_FOR_INITIAL_STOPLOSS'
    INITIAL_STOPLOSS_PLACED = 'INITIAL_STOPLOSS_PLACED'
    STOPLOSS_TRAILING_IN_PROGRESS = 'STOPLOSS_TRAILING_IN_PROGRESS'
    EXITED = 'EXITED'


# global variables -----------------------------------------

# Following will be loaded once 'load_necessary_data()' function is called
nse_instruments_data = None
nfo_instruments_data = None


current_trade_state: TradeState = TradeState.NOT_STARTED
kc: KiteConnect

# option quantity
opt_qty: int = configs.BANK_NIFTY_LOT_SIZE * configs.LONG_STRADDLE_LOT_QTY

# following will be set once bank nifty point fetching is started
cur_bank_nifty_point = None

# Following would be set once position entry is created
# ****
ce_instrument_token = None
entry_ce_price = None
cur_ce_price = None
ce_instrument_trading_symbol = None
ce_buy_order_id = None
# ****
pe_instrument_token = None
entry_pe_price = None
cur_pe_price = None
pe_instrument_trading_symbol = None
pe_buy_order_id = None
# ****


# Following would be set once initial stoploss is created
current_stoploss = None

# Following will be set once the long straddle position is exit
ce_sell_order_id = None
pe_sell_order_id = None
# ----------------------------------------------------------


class TickerData(TypedDict):
    tradable: bool
    mode: str
    instrument_token: int
    last_price: float


def START_LONG_STRADDLE():
    """Root function where the strategy starts"""

    global kc
    global current_trade_state

    kc = utils.new_kite_connect_client()

    fetch_and_load_necessary_data(kc)

    async_fetch_bank_nifty_ltp()

    make_position_entry()

    async_fetch_ATM_PE_CE_ltp()

    place_initial_stoploss()

    async_position_exit()
    async_manage_stoploss()

    # Keep on waiting until order is existed
    while current_trade_state != TradeState.EXITED:
        time.sleep(5)

    print('Long straddle completed !!!')


def fetch_and_load_necessary_data(kc: KiteConnect):
    global nse_instruments_data, nfo_instruments_data

    utils.update_nse_instruments(kc)
    utils.update_nfo_instruments(kc)

    nse_instruments_data = utils.load_nse_instruments_data()
    nfo_instruments_data = utils.load_nfo_instruments_data()

    configs.NIFTY_BANK_INSTRUMENT_TOKEN = \
        nse_instruments_data[BANK_NIFTY_TRADING_SYMBOL]['instrument_token']


def async_fetch_bank_nifty_ltp():
    thread = threading.Thread(target=fetch_bank_nifty_ltp)
    thread.start()


def fetch_bank_nifty_ltp():
    kws: KiteTicker = utils.new_kite_websocket_client()

    kws.on_connect = set_bank_nifty_instrument_for_ltp_fetch
    kws.on_ticks = update_bank_nifty_ltp
    kws.on_close = on_close

    # start on a different thread
    print('started fetching bank nifty real time ltp . . . ')
    kws.connect(threaded=True)

    # keep on fetching bank nifty point until you made a position entry or trade exits
    while True:
        if current_trade_state == TradeState.POSITION_CREATED or \
                current_trade_state == TradeState.EXITED:
            kws.close()
            print('Stopped fetching bank nifty real time ltp ! ! !')
            break

        time.sleep(1)


def async_fetch_ATM_PE_CE_ltp():
    if ce_instrument_token is None or pe_instrument_token is None:
        raise Exception('ce_instrument_token is None or pe_instrument_token is None. '
                        'The position is not created yet')

    thread = threading.Thread(target=fetch_ATM_PE_CE_ltp)
    thread.start()


def fetch_ATM_PE_CE_ltp():
    kws: KiteTicker = utils.new_kite_websocket_client()
    kws.on_connect = set_ATM_CE_PE_instruments_for_price_fetch
    kws.on_ticks = update_ce_pe_ltp
    kws.on_close = on_close

    kws.connect(threaded=True)

    # keep on fetching CE and PE LTP until trade is exit
    while True:
        if current_trade_state == TradeState.EXITED:
            kws.close()
            break

        time.sleep(1)


def make_position_entry():
    """To create position entry
    Steps:
    1. Continuously check NIFTY BANK's ltp and check if this is within 10 pt
    deviation from any strike prices which are multiple of 100. If so buy
    PE and CE option for that strike price"""

    global current_trade_state

    current_trade_state = TradeState.LOOKING_FOP_ENTRY

    while True:
        if cur_bank_nifty_point is None:
            time.sleep(1)
            continue
        else:
            lower_bound_strike_price, upper_bound_strike_price = \
                get_lower_and_upper_bound_strike_prices(cur_bank_nifty_point)

            strike_price = None

            if is_ltp_near_to_strike_price(cur_bank_nifty_point, lower_bound_strike_price):
                strike_price = lower_bound_strike_price
            elif is_ltp_near_to_strike_price(cur_bank_nifty_point, upper_bound_strike_price):
                strike_price = upper_bound_strike_price

            make_entry_at_strike_price(strike_price)


def set_bank_nifty_instrument_for_ltp_fetch(ws, response):
    ws.subscribe([configs.NIFTY_BANK_INSTRUMENT_TOKEN])
    ws.set_mode(ws.MODE_LTP, [configs.NIFTY_BANK_INSTRUMENT_TOKEN])


def update_bank_nifty_ltp(ws, ticks):
    global cur_bank_nifty_point

    bank_nifty_data: TickerData = ticks[0]
    cur_bank_nifty_point = bank_nifty_data['last_price']


def is_ltp_near_to_strike_price(cur_price: float, strike_price: float) -> bool:
    return cur_price >= strike_price - configs.LONG_STRADDLE_SL_TRAILING_POINT_DIFF or\
        cur_price <= strike_price + configs.LONG_STRADDLE_SL_TRAILING_POINT_DIFF


def make_entry_at_strike_price(strike_price: int):
    """But both CE and PE @ATM at strike price 'strike_price'.
     IMPORTANT - update the current_trade_state """

    global ce_instrument_trading_symbol, pe_instrument_trading_symbol
    global current_trade_state, ce_buy_order_id, pe_buy_order_id

    trading_symbol_prefix =\
        f'{configs.BANKNIFTY_2024_PREFIX}{configs.TRADING_MONTH}{strike_price}'

    ce_instrument_trading_symbol = f'{trading_symbol_prefix}CE'
    pe_instrument_trading_symbol = f'{trading_symbol_prefix}PE'

    ce_buy_order_id = buy_ce()
    pe_buy_order_id = buy_pe()

    print(f'INFO: CE and PE orders are created, {ce_instrument_trading_symbol}'
          f' and {pe_instrument_trading_symbol}')

    current_trade_state = TradeState.POSITION_CREATED


def buy_ce() -> str:
    order_id = utils.place_order(
        kc,
        order_variety=kc.VARIETY_REGULAR,
        trading_symbol=ce_instrument_trading_symbol,
        exchange=kc.EXCHANGE_NFO,
        transaction_type=kc.TRANSACTION_TYPE_BUY,
        qty=opt_qty,
        order_type=kc.ORDER_TYPE_MARKET,
        product=kc.PRODUCT_MIS,
        validity=kc.VALIDITY_IOC,
    )

    return order_id


def buy_pe() -> str:
    order_id = utils.place_order(
        kc,
        order_variety=kc.VARIETY_REGULAR,
        trading_symbol=pe_instrument_trading_symbol,
        exchange=kc.EXCHANGE_NFO,
        transaction_type=kc.TRANSACTION_TYPE_BUY,
        qty=opt_qty,
        order_type=kc.ORDER_TYPE_MARKET,
        product=kc.PRODUCT_MIS,
        validity=kc.VALIDITY_IOC,
    )

    return order_id


def get_lower_and_upper_bound_strike_prices(ltp: float) -> (int, int):
    lower_bound = (ltp // 100) * 100
    upper_bound = lower_bound + 100

    return int(lower_bound), int(upper_bound)


def place_initial_stoploss():
    if cur_ce_price is None or cur_pe_price is None:
        raise Exception('cur_ce_price is None or cur_pe_price is None')

    global current_trade_state, current_stoploss

    current_trade_state = TradeState.WAITING_FOR_INITIAL_STOPLOSS

    tot_entry_price: float = get_entry_ce_pe_price()
    initial_stoploss_target: float = tot_entry_price + \
            float(tot_entry_price * configs.LONG_STRADDLE_MIN_PROFIT_PERCENTAGE)/100
    min_tot_price_for_initial_sl: float = initial_stoploss_target + \
                            configs.LONG_STRADDLE_SL_TRAILING_POINT_DIFF

    while True:
        tot_cur_price: float = cur_ce_price + cur_pe_price

        if tot_cur_price >= min_tot_price_for_initial_sl:
            current_stoploss = initial_stoploss_target
            print(f'INFO: initial SL set at {initial_stoploss_target}'
                  f' with current tot price {tot_cur_price}')
            current_trade_state = TradeState.INITIAL_STOPLOSS_PLACED
            break
        else:
            time.sleep(2)


def set_ATM_CE_PE_instruments_for_price_fetch(ws, response):
    ws.subscribe([ce_instrument_token, pe_instrument_token])
    ws.set_mode(ws.MODE_LTP, [ce_instrument_token, pe_instrument_token])


def update_ce_pe_ltp(ws, ticks):
    global cur_ce_price, cur_pe_price

    option_1_ticker_data: TickerData = ticks[0]
    option_2_ticker_data: TickerData = ticks[1]

    if option_1_ticker_data['instrument_token'] == ce_instrument_token:
        cur_ce_price = option_1_ticker_data['last_price']
        cur_pe_price = option_2_ticker_data['last_price']
    else:
        cur_ce_price = option_2_ticker_data['last_price']
        cur_pe_price = option_1_ticker_data['last_price']


def get_entry_ce_pe_price() -> float:
    if entry_pe_price is None or entry_pe_price is None:
        raise Exception('entry_pe_price is None or entry_pe_price is None')

    return float(entry_ce_price + entry_pe_price)


def async_manage_stoploss():
    """Trail the SL as the tot CE+PE price is moving up"""
    global current_stoploss

    while True:
        if current_trade_state == TradeState.EXITED:
            break

        tot_cur_price: float = cur_ce_price + cur_pe_price
        new_possible_stoploss: float = \
            tot_cur_price - configs.LONG_STRADDLE_SL_TRAILING_POINT_DIFF

        current_stoploss = max(current_stoploss, new_possible_stoploss)

        time.sleep(1)


def async_position_exit():
    thread = threading.Thread(target=position_exit)
    thread.start()


def position_exit():
    while True:
        tot_cur_price: float = cur_ce_price + cur_pe_price

        if tot_cur_price <= current_stoploss:
            exit_long_straddle_position()
            break
        else:
            time.sleep(1)


def exit_long_straddle_position():
    global current_trade_state, ce_sell_order_id, pe_sell_order_id

    ce_sell_order_id = exit_ce_order()
    pe_sell_order_id = exit_pe_order()

    print(f'Both CE and PE are sold ! ! !\n . '
          f'ce_sell_order_id: {ce_sell_order_id}, pe_sell_order_id: {pe_sell_order_id}')

    current_trade_state = TradeState.EXITED


def exit_ce_order() -> str:
    # place SELL order for all the CALL options
    if ce_instrument_trading_symbol is None:
        raise Exception('ce_instrument_trading_symbol is None')

    order_id = utils.place_order(
        kc,
        order_variety=kc.VARIETY_REGULAR,
        trading_symbol=ce_instrument_trading_symbol,
        exchange=kc.EXCHANGE_NFO,
        transaction_type=kc.TRANSACTION_TYPE_SELL,
        qty=opt_qty,
        order_type=kc.ORDER_TYPE_MARKET,
        product=kc.PRODUCT_MIS,
        validity=kc.VALIDITY_IOC,
    )

    return order_id


def exit_pe_order() -> str:
    # place SELL order for all the PUT options

    if pe_instrument_trading_symbol is None:
        raise Exception('pe_instrument_trading_symbol is None')

    order_id = utils.place_order(
        kc,
        order_variety=kc.VARIETY_REGULAR,
        trading_symbol=pe_instrument_trading_symbol,
        exchange=kc.EXCHANGE_NFO,
        transaction_type=kc.TRANSACTION_TYPE_SELL,
        qty=opt_qty,
        order_type=kc.ORDER_TYPE_MARKET,
        product=kc.PRODUCT_MIS,
        validity=kc.VALIDITY_IOC,
    )

    return order_id


def on_close(ws, code, reason):
    # On connection close stop the event loop.
    # Reconnection will not happen after executing `ws.stop()`
    ws.stop()


if __name__ == '__main__':
    START_LONG_STRADDLE()
