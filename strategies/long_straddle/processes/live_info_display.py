import json
import threading
import time

from strategies.long_straddle.live_info import LiveInfo


def async_spawn_live_info_viewer():
    print('[ASYNC SPAWN] - async_spawn_live_info_viewer ...')

    thread = threading.Thread(target=continue_showing_live_info)
    thread.start()


def continue_showing_live_info():
    while True:
        print('LiveInfo ------> \n ')
        print(json.dumps(LiveInfo.to_dict(), indent=4))
        print('-----------------')

        time.sleep(1.5)
