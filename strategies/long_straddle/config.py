from datetime import time


SIMULATION_TYPE = 'FAKE'  # (FAKE, REAL)
# fake is for paper trading and real is for real order in broker

STOCK_NAME = 'BANKNIFTY'  # it can be NIFTY also
LOT_QTY = 1
TRADING_MONTH = "SEP"  # todo; important, make use of this while buying and selling options

MAX_ENTRY_TIME = time(12, 00)
MAX_TRADE_TIME = time(15, 25)

# SL_DEVIATION_TYPE = 'ABSOLUTE'  # (ABSOLUTE, PERCENTAGE)
MAX_ENTRY_ATM_PRICE_DEVIATION = 40
SL_DEVIATION = 10  # "point" . currently this is in ABSOLUTE point, Will see in future of PERCENTAGE
# based calculation seems good
MIN_PROFIT_PERCENTAGE = 2
MAX_LOSS_PERCENTAGE = 1
