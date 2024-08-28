import threading


def async_spawn_make_entry_process():
    print('[ASYNC SPAWN] - async_spawn_make_entry_process ...')

    thread = threading.Thread(target=make_entry_and_set_initial_stoploss)
    thread.start()


def make_entry_and_set_initial_stoploss():
    pass
