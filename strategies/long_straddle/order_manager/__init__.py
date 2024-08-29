from strategies.long_straddle.config import *
from strategies.long_straddle.order_manager.interface import IOrderManager
from .real_order_manager import new_real_order_manager
from .fake_order_manager import new_fake_order_manager


def get_new_order_manager() -> IOrderManager:
    if SIMULATION_TYPE == 'FAKE':
        return new_fake_order_manager()
    elif SIMULATION_TYPE == 'REAL':
        return new_real_order_manager()

    raise Exception('invalid SIMULATION_TYPE, It should be either "FAKE" or "REAL"')
