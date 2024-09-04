# This is gap opening STBT long straddle backtesting over BANKNIFTY monthly
# expiry for AUGUST month

from datetime import datetime, date, timedelta
from typing import TypedDict, List
from openpyxl import load_workbook
import pandas as pd


class Input:
    start_date = date(2024, 8, 1)
    end_date = date(2024, 8, 24)
    stock = 'BANKNIFTY'


class Report(TypedDict):
    stock: str

    entry_date: date
    entry_stock_point: float
    entry_ce_price: float
    entry_pe_price: float
    entry_tot_price: float

    strike: float

    exit_date: date
    exit_stock_point: float
    exit_ce_price: float
    exit_pe_price: float
    exit_tot_price: float

    summary_stock_point_delta: float
    summary_ce_delta: float
    summary_pe_delta: float
    summary_tot_delta: float
    summary_basic_profit_percentage: float


def report_to_dict(report: Report) -> dict:
    summary_ce_delta = report['exit_ce_price'] - report['entry_ce_price']
    summary_pe_delta = report['exit_pe_price'] - report['entry_pe_price']
    summary_tot_delta = summary_ce_delta + summary_pe_delta
    summary_basic_profit_percentage = (summary_tot_delta / report.entry_tot_price) * 100

    return {
        'stock': report['stock'],

        'entry_date': report['entry_date'].strftime("%Y-%m-%d"),
        'entry_stock_point': report['entry_stock_point'],
        'entry_ce_price': report['entry_ce_price'],
        'entry_pe_price': report['entry_pe_price'],
        'entry_tot_price': report['entry_tot_price'],

        'strike': report['strike'],

        'exit_date': report['exit_date'].strftime("%Y-%m-%d"),
        'exit_stock_point': report['exit_stock_point'],
        'exit_ce_price': report['exit_ce_price'],
        'exit_pe_price': report['exit_pe_price'],
        'exit_tot_price': report['exit_tot_price'],

        'summary_stock_point_delta': report['exit_stock_point'] - report['entry_stock_point'],
        'summary_ce_delta': summary_ce_delta,
        'summary_pe_delta': summary_pe_delta,
        'summary_tot_delta': summary_tot_delta,
        'summary_basic_profit_percentage': summary_basic_profit_percentage,
    }


class AllReports:
    reports: List[Report] = []

    @classmethod
    def append_to_report_sheet(cls):
        report_file_path = ('/Users/Subhram/my-projects/kite-trading/backtesting/'
                            'gap_opening_long_straddle_aug_2024_report.xlsx')

        wb = load_workbook(report_file_path)
        ws = wb.active

        # If the workbook is empty or needs initialization, create a new sheet
        if ws.title != 'report':
            ws.title = 'report'

        # If reports are not empty, append rows to the worksheet
        if cls.reports:
            df = pd.DataFrame([report_to_dict(r) for r in cls.reports])

            # Append each row to the worksheet
            for _, row in df.iterrows():
                ws.append(row.tolist())

        # Save and close the file
        wb.save(report_file_path)
        wb.close()


def back_test_for_cur_date(cur_date: date) -> Report:
    entry_stock_price = get_stock_eod_price(cur_date)
    strike = get_suitable_strike_price_from_stock_price(entry_stock_price)
    ce_symbol = get_option_instrument_symbol_from_strike_and_date(strike, cur_date, 'CE')
    pe_symbol = get_option_instrument_symbol_from_strike_and_date(strike, cur_date, 'PE')

    ce_entry_price = get_option_eod_price(ce_symbol, cur_date)
    pe_entry_price = get_option_eod_price(pe_symbol, cur_date)
    entry_tot_price = ce_entry_price + pe_entry_price

    next_date = cur_date + timedelta(days=1)

    exit_stock_point = get_sod_stock_price(next_date)
    ce_exit_price = get_option_sod_price(ce_symbol, next_date)
    pe_exit_price = get_option_sod_price(pe_symbol, next_date)
    exit_tot_price = ce_exit_price + pe_exit_price

    ce_delta = ce_exit_price - ce_entry_price
    pe_delta = pe_exit_price - pe_entry_price
    tot_delta = ce_delta + pe_delta
    basic_profit_percentage = (tot_delta / entry_tot_price) * 100

    return Report(
        stock=Input.stock,
        entry_date=cur_date,
        entry_stock_point=entry_stock_price,
        entry_ce_price=ce_entry_price,
        entry_pe_price=pe_entry_price,
        entry_tot_price=entry_tot_price,
        strike=strike,
        exit_date=next_date,
        exit_stock_point=exit_stock_point,
        exit_ce_price=ce_exit_price,
        exit_pe_price=pe_exit_price,
        exit_tot_price=exit_tot_price,
        summary_stock_point_delta=exit_stock_point - entry_stock_price,
        summary_ce_delta=ce_delta,
        summary_pe_delta=pe_delta,
        summary_tot_delta=tot_delta,
        summary_basic_profit_percentage=basic_profit_percentage,
    )


def back_test():
    cur_date = Input.start_date
    while cur_date <= Input.end_date:
        AllReports.reports.append(back_test_for_cur_date(cur_date))

    AllReports.append_to_report_sheet()


if __name__ == '__main__':
    back_test()
