from common import constants as common_constants
from strategies.long_straddle import config as strategy_config


def get_stock_lot_size() -> int:
    if strategy_config.STOCK_NAME == 'BANKNIFTY':
        return common_constants.BANK_NIFTY_LOT_SIZE
    elif strategy_config.STOCK_NAME == 'NIFTY':
        return common_constants.NIFTY_LOT_SIZE

    raise Exception(f'Can not get lot size for invalid stock name: '
                    f'{strategy_config.STOCK_NAME}')
