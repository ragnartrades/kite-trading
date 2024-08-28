import threading
import time

from common.constants import NIFTY_BANK_INSTRUMENT_TOKEN
from strategies.long_straddle.classes import *
from kiteconnect import KiteTicker

from common.utils import new_kite_websocket_client
from strategies.long_straddle.live_info import LiveInfo, TradingState


def async_spawn_stock_price_fetcher():
    print('[ASYNC SPAWN] - async_spawn_stock_price_fetcher ...')

    thread = threading.Thread(target=start_fetching_and_updating_stock_price)
    thread.start()


def start_fetching_and_updating_stock_price():
    kws: KiteTicker = new_kite_websocket_client()

    kws.on_connect = subscribe_to_stock_instrument
    kws.on_ticks = update_stock_ltp
    kws.on_close = close_websocket_connection

    kws.connect(threaded=True)

    while LiveInfo.trading_state != TradingState.EXITED:
        time.sleep(1)

    kws.close()


def subscribe_to_stock_instrument(ws, response):
    ws.subscribe([LiveInfo.stock_instrument_token])
    ws.set_mode(ws.MODE_LTP, [LiveInfo.stock_instrument_token])


def close_websocket_connection(ws, code, reason):
    ws.stop()


def update_stock_ltp(ws, ticks):
    stock_data: TickerData = ticks[0]
    LiveInfo.stock_ltp = stock_data['last_price']
