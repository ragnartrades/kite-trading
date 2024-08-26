import os
from typing import List, TypedDict
from datetime import datetime, date, timedelta, time
import pandas as pd
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl import Workbook
from enum import Enum

from common.utils import MONTH_NUMBER_TO_OPTION_MONTH_SYMBOL_MAP
from strategies.long_straddle import get_lower_and_upper_bound_strike_prices

# global variables -----------------------
backtesting_directory = os.path.join(os.getcwd(), 'backtesting')
report_file_path = f'{backtesting_directory}/long_straddle_report.xlsx'
max_time_for_entry = time(hour=12, minute=0, second=0)
max_exit_time = time(hour=15, minute=10, second=0)
current_stoploss = None


# -----------------------------------------


class CandleStick(TypedDict):
    instrument_symbol: str
    date: str
    open: float
    high: float
    low: float
    close: float


class BackTestInput:
    START_DATE = datetime.strptime("2024-08-12", "%Y-%m-%d").date()
    END_DATE = datetime.strptime("2024-08-12", "%Y-%m-%d").date()
    LOT_SIZE = 15
    LOT_QTY = 1
    ENTRY_DEVIATION = 5
    MIN_PROFIT_PERCENTAGE = 3
    SL_DEVIATION = 10


class ExitReason(Enum):
    SL_HIT = 'SL_HIT'
    TIME_ELAPSED_NO_ENTRY_CONDITION = 'TIME_ELAPSED_NO_ENTRY_CONDITION'
    TIME_ELAPSED_NO_INITIAL_SL_CREATED = 'TIME_ELAPSED_NO_INITIAL_SL_CREATED'
    DAY_END_FORCE_EXIT = 'DAY_END_FORCE_EXIT'


class Report(TypedDict):
    # basic info
    date: str
    lot_size: int
    lot_qty: int
    market_opening_banknifty_point: float

    # entry info
    entry_time: str
    entry_bank_nifty_point: float
    entry_ce_price: float
    entry_pe_price: float
    entry_tot_price: float
    entry_tot_value: float

    # exit info
    exit_time: str
    exit_bank_nifty_point: float
    exit_ce_price: float
    exit_pe_price: float
    exit_tot_price: float
    exit_tot_value: float
    exit_reason: str

    # profit and outcome metrics info
    tot_price_difference_made: float
    basic_profit_percentage: float
    tot_charges: float
    net_profit_percentage: float  # considering all lots and all charges


def GENERATE_LONG_STRADDLE_BACKTEST_REPORT():
    all_days_report: List[Report] = generate_backtest_report_for_all_days()
    write_result_to_report_file(all_days_report)


def generate_backtest_report_for_all_days() -> List[Report]:
    report = []

    current_day = BackTestInput.START_DATE

    print(f'Started generating long straddle backtest data for all days from'
          f' {BackTestInput.START_DATE} to {BackTestInput.END_DATE} . . . ')

    while current_day <= BackTestInput.END_DATE:
        current_day_report: Report = generate_backtest_report_for_specific_day(current_day)
        report.append(current_day_report)

        current_day += timedelta(days=1)

    print(f'Successfully generated long straddle backtest data for all days !!!')

    return report


def generate_backtest_report_for_specific_day(day: date) -> Report:
    print(f'Started generating report for {day} . . . ')

    report: Report = get_long_straddle_dry_run_result_on_specific_date(day)

    print(f'Report generated for {day} !!!')

    return report


def write_result_to_report_file(report: List[Report]):
    print(f'Started writing report to target file: {report_file_path} . . . ')

    # 1. delete target file if exists
    delete_target_file_if_exists()

    # 2. create a new one
    wb = Workbook()
    ws = wb.active
    ws.title = 'report'  # Rename the default sheet to 'report'

    # 3. write data to this file
    df = pd.DataFrame(report)
    df.columns = [col.replace('_', ' ') for col in df.columns]
    for row in dataframe_to_rows(df, index=False, header=True):
        ws.append(row)

    # 4. Save the workbook to the specified path ands close
    wb.save(report_file_path)
    wb.close()

    print(f'Successfully created report  for all days !!!')


def delete_target_file_if_exists():
    if os.path.exists(report_file_path):
        os.remove(report_file_path)


def get_long_straddle_dry_run_result_on_specific_date(day: date) -> Report:
    report: Report = Report(
        date=day.strftime("%Y-%m-%d"),
        lot_size=BackTestInput.LOT_SIZE,
        lot_qty=BackTestInput.LOT_QTY,
    )

    source_data_file_path: str = get_source_data_file_path_from_date(day)

    # ------ simulate the long straddle entry and exit conditions ------

    # populate basic info
    df = pd.read_excel(source_data_file_path, sheet_name='BANKNIFTY')
    for row_num, data in df.iterrows():
        open: float = data['open']
        if 'market_opening_banknifty_point' not in report:
            report['market_opening_banknifty_point'] = open
            break

    # get two nearest strike prices
    cur_bank_nifty_point = report['market_opening_banknifty_point']
    lower_bound_strike_price, upper_bound_strike_price = \
        get_lower_and_upper_bound_strike_prices(cur_bank_nifty_point)

    # try to make an entry and if possible create initial stoploss
    entry_time: time = None
    entry_ce_instrument_name = None
    entry_pe_instrument_name = None
    df = pd.read_excel(source_data_file_path, sheet_name='BANKNIFTY')
    for row_num, data in df.iterrows():
        date_time_str: str = data['date']
        open: float = data['open']
        high: float = data['high']
        low: float = data['low']
        close: float = data['close']

        date_time = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")
        tm = date_time.time()

        if tm > max_time_for_entry:
            report['exit_reason'] = ExitReason.TIME_ELAPSED_NO_ENTRY_CONDITION.value
            report['tot_price_difference_made'] = 0
            report['basic_profit_percentage'] = 0
            report['tot_charges'] = 0
            report['net_profit_percentage'] = 0

            return report

        is_possible, strike_price, bank_nifty_entry_point = entry_possible(
            high,
            low,
            lower_bound_strike_price,
            upper_bound_strike_price,
        )

        if is_possible:
            entry_time = tm
            report['entry_time'] = entry_time.strftime("%H:%M:%S")
            report['entry_bank_nifty_point'] = bank_nifty_entry_point  # APPROXIMATION

            entry_ce_instrument_name, entry_pe_instrument_name, tot_entry_price = \
                make_entry(date_time.date(), entry_time, report, strike_price)

            initial_sl_creation_time, is_exited = set_initial_stoploss(
                report,
                day,
                entry_time,
                entry_ce_instrument_name,
                entry_pe_instrument_name,
                tot_entry_price,
            )

            if is_exited:
                calculate_profit_metrics_report(report)
                return report

            break
        else:
            continue

    # after making successful entry, try to find when to exit, either
    # 1. SL hits while trailing OR
    # 2. time crosses 'max_exit_time' and SL did nto hit yet. But have to exit

    make_exit(
        report,
        day,
        initial_sl_creation_time,
        entry_ce_instrument_name,
        entry_pe_instrument_name
    )

    calculate_profit_metrics_report(report)

    return report


def calculate_profit_metrics_report(report: Report):
    report['tot_price_difference_made'] = \
        report['exit_tot_price'] - report['entry_tot_price']

    report['basic_profit_percentage'] = \
        (report['tot_price_difference_made'] / report['entry_tot_price']) * 100

    # https://docs.google.com/spreadsheets/d/1bCBxrJdEFFy6hx--zdVww4OmV13hS4C9jTj74z43PSY/edit?gid=1935620396#gid=1935620396
    tot_opt_qty = BackTestInput.LOT_SIZE * BackTestInput.LOT_QTY
    profit_per_unit_option = report['tot_price_difference_made']
    report['tot_charges'] = 2 * 42.550717 + \
                            2 * (0.234258 * tot_opt_qty) + \
                            (0.109864 * profit_per_unit_option)  # APPROXIMATION

    tot_basic_profit = tot_opt_qty * report['tot_price_difference_made']
    net_profit = tot_basic_profit - report['tot_charges']
    net_buying_value = tot_opt_qty * report['entry_tot_price']
    report['net_profit_percentage'] = (net_profit / net_buying_value) * 100


def make_exit(
        report: Report,
        cur_date: date,
        initial_sl_creation_time: time,
        entry_ce_instrument_name: str,
        entry_pe_instrument_name: str,
):
    """Steps
    1. start from 'initial_sl_creation_time' and iterate through CE, PE candlestick data
    2. on each step do
        a. check if current time exceeds EOD, then exit and update report accordingly and return, else
        b. maximise SL
        c. check if SL hits, if hits update report and return """

    global current_stoploss

    ce_sheet_name = entry_ce_instrument_name
    pe_sheet_name = entry_pe_instrument_name

    source_data_file_path: str = get_source_data_file_path_from_date(cur_date)
    df_ce = pd.read_excel(source_data_file_path, sheet_name=ce_sheet_name)
    df_pe = pd.read_excel(source_data_file_path, sheet_name=pe_sheet_name)
    for row_num in range(len(df_ce)):
        ce_data = df_ce.iloc[row_num]
        pe_data = df_pe.iloc[row_num]

        date_time_str: str = ce_data['date']  # date time should be same for both CE and PE
        date_time = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")
        cur_time = date_time.time()
        if cur_time < initial_sl_creation_time:
            continue

        ce_open: float = ce_data['open']
        ce_high: float = ce_data['high']
        ce_low: float = ce_data['low']
        ce_close: float = ce_data['close']

        pe_open: float = pe_data['open']
        pe_high: float = pe_data['high']
        pe_low: float = pe_data['low']
        pe_close: float = pe_data['close']

        cur_avg_ce_price = (ce_open + ce_high + ce_low + ce_close) / 4
        cur_avg_pe_price = (pe_open + pe_high + pe_low + pe_close) / 4
        cur_tot_price = cur_avg_ce_price + cur_avg_pe_price

        # 1. exit condition 1 - max time exceeds
        if cur_time >= max_exit_time:
            report['exit_reason'] = ExitReason.DAY_END_FORCE_EXIT.value

            report['exit_time'] = cur_time.strftime("%H:%M:%S")
            report['exit_bank_nifty_point'] = 'not calculated :('  # todo
            report['exit_ce_price'] = cur_avg_ce_price
            report['exit_pe_price'] = cur_avg_pe_price
            report['exit_tot_price'] = cur_tot_price
            report['exit_tot_value'] = cur_tot_price * BackTestInput.LOT_SIZE * BackTestInput.LOT_QTY

            break

        # 2. Update SL
        new_possible_sl = cur_tot_price - BackTestInput.SL_DEVIATION
        current_stoploss = max(current_stoploss, new_possible_sl)

        # 3. exit condition 2 - SL hits
        if cur_tot_price <= current_stoploss:
            report['exit_reason'] = ExitReason.SL_HIT.value

            report['exit_time'] = cur_time.strftime("%H:%M:%S")
            report['exit_bank_nifty_point'] = 'not calculated :('  # todo
            report['exit_ce_price'] = cur_avg_ce_price
            report['exit_pe_price'] = cur_avg_pe_price
            report['exit_tot_price'] = cur_tot_price
            report['exit_tot_value'] = cur_tot_price * BackTestInput.LOT_SIZE * BackTestInput.LOT_QTY

            break


def set_initial_stoploss(
        report: Report,
        cur_date: date,
        entry_time: time,
        entry_ce_instrument_name: str,
        entry_pe_instrument_name: str,
        tot_entry_price: float,
) -> (time, bool):
    """Steps
    1. Build dataframe for candlestick for CE and PE options
    2. start iterating through these and check for
        1. if min_tim_for_entry exceeds, then exit the trade and update report
        2. else check if, cur_tot_price >= (tot_entry_price + min_profit_percentage + ENTRY_DEVIATION)
        If this happens, initialise the 'current_stoploss' = cur_tot_price - SL_DEVIATION

    """

    global current_stoploss

    ce_sheet_name = entry_ce_instrument_name
    pe_sheet_name = entry_pe_instrument_name

    source_data_file_path: str = get_source_data_file_path_from_date(cur_date)
    df_ce = pd.read_excel(source_data_file_path, sheet_name=ce_sheet_name)
    df_pe = pd.read_excel(source_data_file_path, sheet_name=pe_sheet_name)
    for row_num in range(len(df_ce)):
        ce_data = df_ce.iloc[row_num]
        pe_data = df_pe.iloc[row_num]

        date_time_str: str = ce_data['date']  # date time should be same for both CE and PE
        date_time = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")
        cur_time = date_time.time()
        if cur_time <= entry_time:
            continue

        # populate relevant entry data in report and return
        ce_open: float = ce_data['open']
        ce_high: float = ce_data['high']
        ce_low: float = ce_data['low']
        ce_close: float = ce_data['close']

        pe_open: float = pe_data['open']
        pe_high: float = pe_data['high']
        pe_low: float = pe_data['low']
        pe_close: float = pe_data['close']

        approx_ce_price = (ce_open + ce_high + ce_low + ce_close) / 4  # APPROXIMATION
        approx_pe_price = (pe_open + pe_high + pe_low + pe_close) / 4  # APPROXIMATION
        tot_cur_price = approx_ce_price + approx_pe_price

        # 1. condition check 1
        if cur_time > max_time_for_entry:
            # set exit info and return
            report['exit_reason'] = ExitReason.TIME_ELAPSED_NO_INITIAL_SL_CREATED.value
            report['exit_time'] = cur_time.strftime("%H:%M:%S")
            report['exit_bank_nifty_point'] = 'Not set :('  # todo: need to set it
            report['exit_ce_price'] = approx_ce_price
            report['exit_pe_price'] = approx_pe_price
            report['exit_tot_price'] = tot_cur_price
            report['exit_tot_value'] = tot_cur_price * BackTestInput.LOT_SIZE * BackTestInput.LOT_QTY

            return cur_time, True

        # 2. condition check 2
        if tot_cur_price >= tot_entry_price + \
                (tot_entry_price * BackTestInput.MIN_PROFIT_PERCENTAGE / 100) + \
                BackTestInput.SL_DEVIATION:
            current_stoploss = tot_cur_price - BackTestInput.SL_DEVIATION  # APPROXIMATION propagated

            return cur_time, False

    raise Exception('unreachable condition for : set_initial_stoploss() function')


def entry_possible(
        high: float,
        low: float,
        lower_bound_strike_price: int,
        upper_bound_strike_price: int,
) -> (bool, int, float):  # (is_possible, strike_price, bank_nifty_entry_point)
    if entry_possible_for_lower_bound_strike_price(low, lower_bound_strike_price):
        return True, lower_bound_strike_price, lower_bound_strike_price + BackTestInput.ENTRY_DEVIATION
    elif entry_possible_for_upper_bound_strike_price(high, upper_bound_strike_price):
        return True, upper_bound_strike_price, upper_bound_strike_price - BackTestInput.ENTRY_DEVIATION

    return False, None


def entry_possible_for_lower_bound_strike_price(
        low: float,
        lower_bound_strike_price: int,
) -> bool:
    return low <= lower_bound_strike_price + BackTestInput.ENTRY_DEVIATION


def entry_possible_for_upper_bound_strike_price(
        high: float,
        upper_bound_strike_price: int,
) -> bool:
    return high >= upper_bound_strike_price - BackTestInput.ENTRY_DEVIATION


# APPROXIMATION: instead of 'entry_date' we should take expiry year in order to build the instrument symbol
# but since it is monthly expiry, hence entry date have same month as expiry month
def make_entry(entry_date: date, entry_time: time, report: Report, strike_price: int) \
        -> (str, str, float):
    """ Update report object with entry CE, PE prices and total value.
    1. build instrument name for CE and PE
    2. load data using dataframe for both of these sheets named with instrument names
    3. Iterate each one and at the entry time take the price profile and set required things in report
    4. return the instrument names / sheet name themselves"""

    ce_instrument_name = get_bank_nifty_option_instrument_name_from_strike_price(
        entry_date,
        strike_price,
        'CE'
    )
    pe_instrument_name = get_bank_nifty_option_instrument_name_from_strike_price(
        entry_date,
        strike_price,
        'PE'
    )

    ce_sheet_name = ce_instrument_name
    pe_sheet_name = pe_instrument_name

    source_data_file_path: str = get_source_data_file_path_from_date(entry_date)
    df_ce = pd.read_excel(source_data_file_path, sheet_name=ce_sheet_name)
    df_pe = pd.read_excel(source_data_file_path, sheet_name=pe_sheet_name)
    for row_num in range(len(df_ce)):
        ce_data = df_ce.iloc[row_num]
        pe_data = df_pe.iloc[row_num]

        date_time_str: str = ce_data['date']  # date time should be same for both CE and PE
        date_time = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")
        cur_time = date_time.time()
        if cur_time < entry_time:
            continue

        # populate relevant entry data in report and return
        ce_open: float = ce_data['open']
        ce_high: float = ce_data['high']
        ce_low: float = ce_data['low']
        ce_close: float = ce_data['close']

        pe_open: float = pe_data['open']
        pe_high: float = pe_data['high']
        pe_low: float = pe_data['low']
        pe_close: float = pe_data['close']

        approx_ce_price = (ce_open + ce_high + ce_low + ce_close) / 4  # --- IMPORTANT --- APPROXIMATION.
        # we should know the exact time when entry is made, which is impossible to know in 1 minute candlestick
        # same approximation is during exit. These are two main approximations that affect profit figure
        approx_pe_price = (pe_open + pe_high + pe_low + pe_close) / 4  # APPROXIMATION
        approx_entry_price = approx_ce_price + approx_pe_price

        report['entry_ce_price'] = approx_ce_price
        report['entry_pe_price'] = approx_pe_price
        report['entry_tot_price'] = approx_entry_price
        report['entry_tot_value'] = approx_entry_price * BackTestInput.LOT_SIZE * BackTestInput.LOT_QTY

        break

    return ce_instrument_name, pe_instrument_name, approx_entry_price


def get_bank_nifty_option_instrument_name_from_strike_price(
        entry_date: date,
        strike_price: int,
        option_type: str,
) -> str:
    year = entry_date.year
    last_two_digit_in_year = year % 2000

    month_num = entry_date.month
    month_str = MONTH_NUMBER_TO_OPTION_MONTH_SYMBOL_MAP[month_num]

    return f'BANKNIFTY{last_two_digit_in_year}{month_str}{int(strike_price)}{option_type}'


def get_source_data_file_path_from_date(day: date) -> str:
    backtest_dir = os.path.join(os.getcwd(), 'backtesting')
    data_folder_path = os.path.join(backtest_dir, 'data')

    year = day.year
    month = day.month
    day = day.day

    source_file_path = f'{data_folder_path}/{year}/{month}/{day}.xlsx'

    return source_file_path


if __name__ == '__main__':
    # IMPORTANT ---> before running this script, make sure that data are generated for the above days
    # hence oyu need to run "backtesting/generate_data.py" script first by providing
    # the same date ranges
    GENERATE_LONG_STRADDLE_BACKTEST_REPORT()
