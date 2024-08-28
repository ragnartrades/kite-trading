import threading
import time
from kiteconnect import KiteTicker

from common.utils import new_kite_websocket_client
from strategies.long_straddle.classes import TickerData
from strategies.long_straddle.live_info import LiveInfo, TradingState


def async_spawn_option_price_fetcher():
    thread = threading.Thread(target=start_fetching_and_updating_CE_PE_prices)
    thread.start()


def start_fetching_and_updating_CE_PE_prices():
    print('[ASYNC SPAWN] - start_fetching_and_updating_CE_PE_prices ...')

    while LiveInfo.ce_instrument_token is None or \
            LiveInfo.pe_instrument_token is None:
        time.sleep(1)

    kws: KiteTicker = new_kite_websocket_client()

    kws.on_connect = subscribe_to_CE_PE_instruments
    kws.on_ticks = update_CE_PE_ltp
    kws.on_close = close_websocket_connection

    kws.connect(threaded=True)

    while LiveInfo.trading_state != TradingState.EXITED:
        time.sleep(1)

    kws.close()


def subscribe_to_CE_PE_instruments(ws, response):
    ws.subscribe([LiveInfo.ce_instrument_token, LiveInfo.pe_instrument_token])
    ws.set_mode(ws.MODE_LTP, [LiveInfo.ce_instrument_token, LiveInfo.pe_instrument_token])


def close_websocket_connection(ws, code, reason):
    ws.stop()


def update_CE_PE_ltp(ws, ticks):
    option_1_ticker_data: TickerData = ticks[0]
    option_2_ticker_data: TickerData = ticks[1]

    if option_1_ticker_data['instrument_token'] == LiveInfo.ce_instrument_token:
        LiveInfo.ce_ltp = option_1_ticker_data['last_price']
        LiveInfo.pe_ltp = option_2_ticker_data['last_price']
    else:
        LiveInfo.ce_ltp = option_2_ticker_data['last_price']
        LiveInfo.pe_ltp = option_1_ticker_data['last_price']

    LiveInfo.tot_ce_pe_ltp = LiveInfo.ce_ltp + LiveInfo.pe_ltp
