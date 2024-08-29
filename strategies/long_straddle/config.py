from datetime import time


SIMULATION_TYPE = 'FAKE'  # (FAKE, REAL)
# fake is for paper trading and real is for real order in broker

STOCK_NAME = 'NIFTY'  # it can be NIFTY also
LOT_QTY = 1
TRADING_MONTH = "SEP"  # todo; important, make use of this while buying and selling options

SL_DEVIATION_TYPE = 'ABSOLUTE'  # (ABSOLUTE, PERCENTAGE)
SL_DEVIATION = 10

MAX_ENTRY_ATM_PRICE_DEVIATION = 48

MAX_ENTRY_TIME = time(14, 00)
MAX_TRADE_TIME = time(15, 15)
MAX_LOSS_PERCENTAGE = 1
