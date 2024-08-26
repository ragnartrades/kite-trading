import time

from kiteconnect import KiteConnect, KiteTicker
from common import utils
from common.utils import place_order


def basics():

    kc: KiteConnect = utils.get_kite_connect_client()

    utils.update_nse_instruments(kc)
    utils.update_nfo_instruments(kc)

    # kws: KiteTicker = utils.get_kite_websocket_client()
    # kws.on_ticks = on_ticks
    # kws.on_connect = on_connect
    # kws.on_close = on_close
    #
    # print('starting web socket ...')
    #
    # kws.connect(threaded=False)  # run the websocket client on async thread
    #
    # print('ended web socket !!!')


def on_ticks(ws, ticks):
    # if tick_cnt > 5:
    #     print('stopping ws object')
    #     ws.stop()
    # # else:
    # #     tick_cnt = tick_cnt + 1

    print("Ticks: {}".format(ticks))


def on_connect(ws, response):
    # Callback on successful connect.
    # Subscribe to a list of instrument_tokens (RELIANCE and NIFTY BANK here).
    ws.subscribe([260105])

    # Set NIFTY BANK to tick in `full` mode.
    ws.set_mode(ws.MODE_LTP, [260105])


def on_close(ws, code, reason):
    # On connection close stop the event loop.
    # Reconnection will not happen after executing `ws.stop()`
    ws.stop()


if __name__ == '__main__':
    basics()
