import os
from typing import TypedDict
from strategies.long_straddle import config as strategy_config
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl import Workbook
import pandas as pd
from strategies.long_straddle.live_info import LiveInfo


class TradeReport(TypedDict):
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
        report_file_path = cls.get_report_file_path()

        print(f'Started writing report to target file: {report_file_path} . . . ')

        # 2. create a new one
        wb = Workbook()
        ws = wb.active
        ws.title = 'report'  # Rename the default sheet to 'report'

        # 3. write data to this file
        df = pd.DataFrame(report)
        df.columns = [col.replace('_', ' ') for col in df.columns]
        for row in dataframe_to_rows(df, index=False):
            ws.append(row)

        # 4. Save the workbook to the specified path ands close
        wb.save(report_file_path)
        wb.close()

        print(f'Successfully saved report')

    @classmethod
    def get_report_file_path(cls) -> str:
        report_dir: str = os.path.join(os.getcwd(), 'strategies/long_straddle/long_straddle')

        if strategy_config.SIMULATION_TYPE == 'REAL':
            return f'{report_dir}/real_report.xlsx'
        if strategy_config.SIMULATION_TYPE == 'FAKE':
            return f'{report_dir}/fake_report.xlsx'

        raise Exception(f'invalid SIMULATION_TYPE: {strategy_config.SIMULATION_TYPE}. \n'
                        f'allowed values are : REAL, FAKE')
