import os
from typing import TypedDict
from strategies.long_straddle import config as strategy_config
from openpyxl import load_workbook
import pandas as pd
from strategies.long_straddle.live_info import LiveInfo


class TradeReport(TypedDict):
    """ IMPORTANT - DO NOT CHANGE THE SEQUENCE OF KEYS
    They are as per in the report sheet"""
    stock_symbol: str
    date: str
    lot_size: int
    lot_qty: int

    entry_time: str
    entry_stock_point: float
    entry_ce_price: float
    entry_pe_price: float
    entry_tot_price: float
    tot_buying_value: float

    strike_price: int

    exit_time: str
    exit_stock_point: float
    exit_ce_price: float
    exit_pe_price: float
    exit_tot_price: float
    tot_selling_value: float

    per_unit_basic_profit: float
    tot_basic_profit: float
    all_charges: float
    net_profit: float
    net_profit_percentage: float
    exit_reason: str


class TradeReportHandler:
    @classmethod
    def generate_report(cls) -> TradeReport:
        report = TradeReport()

        report['stock_symbol'] = LiveInfo.stock_symbol
        report['date'] = LiveInfo.date.strftime("%Y-%m-%d")
        report['lot_size'] = LiveInfo.lot_size
        report['lot_qty'] = LiveInfo.lot_qty

        report['entry_time'] = LiveInfo.entry_time.strftime("%H:%M:%S")
        report['entry_stock_point'] = LiveInfo.entry_stock_price
        report['entry_ce_price'] = LiveInfo.entry_ce_price
        report['entry_pe_price'] = LiveInfo.entry_pe_price
        report['entry_tot_price'] = LiveInfo.entry_tot_price
        report['tot_buying_value'] = LiveInfo.tot_buying_value

        report['strike_price'] = LiveInfo.strike_price

        report['exit_time'] = LiveInfo.exit_time.strftime("%H:%M:%S")
        report['exit_stock_point'] = LiveInfo.exit_stock_price
        report['exit_ce_price'] = LiveInfo.exit_ce_price
        report['exit_pe_price'] = LiveInfo.exit_pe_price
        report['exit_tot_price'] = LiveInfo.exit_tot_price
        report['tot_selling_value'] = LiveInfo.tot_selling_value

        report['per_unit_basic_profit'] = report['exit_tot_price'] - report['entry_tot_price']
        report['tot_basic_profit'] = report['tot_selling_value'] - report['tot_buying_value']
        report['all_charges'] = LiveInfo.charges()
        report['net_profit'] = report['tot_basic_profit'] - report['all_charges']
        report['net_profit_percentage'] = report['net_profit'] / report['tot_buying_value'] * 100
        report['exit_reason'] = LiveInfo.exit_reason.value

        return report

    @classmethod
    def write_report(cls, report: TradeReport):
        # 1. Fetch the report file path
        report_file_path = cls.get_report_file_path()

        print(f'Started writing report to target file: {report_file_path} . . . ')

        # 2. Check if the file exists, if not raise an exception
        if not os.path.exists(report_file_path):
            raise FileNotFoundError(f'The file at {report_file_path} does not exist.')

        try:
            # 3. Open the file with write permission
            wb = load_workbook(report_file_path)
            ws = wb.active

            # If the workbook is empty or needs initialization, create a new sheet
            if ws.title != 'report':
                ws.title = 'report'

            # 4. Append a single row that is created from report dict
            row = [report[col] for col in pd.DataFrame([report]).columns]
            ws.append(row)

            # 5. Save and close the file
            wb.save(report_file_path)
            wb.close()

            print(f'Successfully saved report')

        except Exception as e:
            print(f'Failed to save report: {e}')

    @classmethod
    def get_report_file_path(cls) -> str:
        report_dir: str = os.path.join(os.getcwd(), 'strategies/long_straddle/reports')

        if strategy_config.SIMULATION_TYPE == 'REAL':
            return f'{report_dir}/real_report.xlsx'
        if strategy_config.SIMULATION_TYPE == 'FAKE':
            return f'{report_dir}/fake_report.xlsx'

        raise Exception(f'invalid SIMULATION_TYPE: {strategy_config.SIMULATION_TYPE}. \n'
                        f'allowed values are : REAL, FAKE')
