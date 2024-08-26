import json
from datetime import date, datetime
from kiteconnect import KiteConnect, KiteTicker
from common import configs
from typing import TypedDict


MONTH_NUMBER_TO_OPTION_MONTH_SYMBOL_MAP = {
    1: 'JAN',
    2: 'FEB',
    3: 'MAR',
    4: 'APR',
    5: 'MAY',
    6: 'JUN',
    7: 'JLU',
    8: 'AUG',
    9: 'SEP',
    10: 'OCT',
    11: 'NOV',
    12: 'DEC',
}


def get_kite_connect_client() -> KiteConnect:
    kc: KiteConnect = KiteConnect(
        api_key=configs.API_KEY,
        debug=configs.DEBUG,
    )

    print("Please login with here and fetch the 'request_token' from redirected "
          "url after successful login : ", kc.login_url())

    request_token: str = input("enter 'request_token': ")

    session_data: dict = kc.generate_session(
        request_token=request_token,
        api_secret=configs.API_SECRETE,
    )

    configs.ACCESS_TOKEN = session_data['access_token']
    kc.set_access_token(configs.ACCESS_TOKEN)

    print('\nkite connect client creation successful !!! ')

    return kc


def get_kite_websocket_client() -> KiteTicker:
    if configs.ACCESS_TOKEN is None:
        err_msg = ('access_token is not initialised. Please connect to kite connect first with'
                   ' "get_kite_connect_client()" function, and then try to create websocket client')

        raise Exception(err_msg)

    kws: KiteTicker = KiteTicker(
        api_key=configs.API_KEY,
        access_token=configs.ACCESS_TOKEN,
        debug=configs.DEBUG,
    )

    print('\nkite websocket client creation successful !!! ')

    return kws


def place_order(
        kc: KiteConnect,
        order_variety: str,
        trading_symbol: str,
        exchange: str,
        transaction_type: str,
        qty: int,
        order_type: str,
        product: str,
        validity: str,
) -> str:
    try:
        order_id = kc.place_order(
            variety=order_variety,
            tradingsymbol=trading_symbol,
            exchange=exchange,
            transaction_type=transaction_type,
            quantity=qty,
            order_type=order_type,
            product=product,
            validity=validity,
        )

        return order_id
    except Exception as e:
        print("Order placement failed: {}".format(e))


def update_nse_instruments(kc: KiteConnect):
    all_nse_instruments = kc.instruments(kc.EXCHANGE_NSE)

    all_data = {}
    for data in all_nse_instruments:
        all_data[f'{data['tradingsymbol']}'] = data

    with open('./.rough/NSE_instruments.json', 'w') as json_file:
        json.dump(all_data, json_file, indent=4)


def update_nfo_instruments(kc: KiteConnect):
    all_nfo_instruments = kc.instruments(kc.EXCHANGE_NFO)

    trading_symbol_to_data_map = {}
    for data in all_nfo_instruments:
        trading_symbol_to_data_map[f'{data["tradingsymbol"]}'] = data

    with open('./.rough/NFO_instruments.json', 'w') as json_file:
        json.dump(trading_symbol_to_data_map, json_file, cls=CustomJSONEncoder, indent=4)


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()  # Convert date and datetime to string
        return super().default(obj)


class OptionsData(TypedDict):
    instrument_token: int
    tradingsymbol: str
    name: str
    expiry: str
    strike: float
    lot_size: int
    instrument_type: str


def load_nfo_instruments_data() -> dict:
    json_file_path = './.rough/NFO_instruments.json'
    with open(json_file_path, 'r') as file:
        data_dict = json.load(file)

    return data_dict


def load_nse_instruments_data() -> dict:
    json_file_path = './.rough/NSE_instruments.json'
    with open(json_file_path, 'r') as file:
        data_dict = json.load(file)

    return data_dict
