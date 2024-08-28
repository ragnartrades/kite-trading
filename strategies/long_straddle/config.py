from datetime import time


SIMULATION_TYPE = 'FAKE'  # (FAKE, REAL)
# fake is for paper trading and real is for real order in broker

STOCK_NAME = 'BANKNIFTY'  # it can be NIFTY also
LOT_QTY = 1
TRADING_MONTH = "SEP"

SL_DEVIATION_TYPE = 'ABSOLUTE'  # (ABSOLUTE, PERCENTAGE)
SL_DEVIATION = 5

MAX_ENTRY_TIME = time(11, 59)
MAX_TRADE_TIME = time(15, 15)
MAX_LOSS_PERCENTAGE = 1
