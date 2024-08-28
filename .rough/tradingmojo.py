from algomojo.pyapi import *
import time
import logging

logger = logging.getLogger(__name__)

brcode = "your-broker-code"
sym1 = "IDEA-EQ"
sym2 = "ZOMATO-EQ"
sym3 = "YESBANK-EQ"
sym4 = "BHEL-EQ"

opt_sym = "NIFTY02MAR18000CE"
opt_expiry = "02MAR"

print("#0 Setting API Key and API Secret")

# Set the API Key and API Secret key obtained from Algomojo MyAPI Section

algomojo = api(api_key="your-api-key",
               api_secret="your-api-secret")
print("\n")

try:
    print("#1 Placing MIS Market Order")
    print("symbol :" + sym1)
    # Place Market Order in the trading symbol RELIANCE-EQ
    response = algomojo.PlaceOrder(broker=brcode,
                                   strategy="Python Example",
                                   exchange="NSE",
                                   symbol=sym1,
                                   action="BUY",
                                   product="MIS",
                                   quantity=10)
    print(response)
    print("\n")
except Exception as e:
    logger.error(f"An error occurred: {e}")

try:
    print("#2 Placing MIS Limit Order")
    print("symbol :" + sym2)
    # Place Limit Order in the trading symbol ZOMATO-EQ
    response = algomojo.PlaceOrder(broker=brcode,
                                   strategy="Python Example",
                                   exchange="NSE",
                                   symbol=sym2,
                                   action="BUY",
                                   product="MIS",
                                   quantity=10,
                                   pricetype="LIMIT",
                                   price=54)
    print(response)
    orderid = response['data']['orderid']
    print("order id is :" + orderid)
    print("\n")
except Exception as e:
    logger.error(f"An error occurred: {e}")

try:
    print("#3 #Place Larger Order in options with Split Order mode enabled")
    print("symbol :" + opt_sym)
    # Place Larger Order in options with Split Order mode enabled
    response = algomojo.PlaceOrder(broker=brcode,
                                   strategy="Python Example",
                                   exchange="NFO",
                                   symbol=opt_sym,
                                   action="BUY",
                                   product="NRML",
                                   quantity=10200,
                                   pricetype="MARKET",
                                   splitorder="YES",
                                   split_quantity=1800)
    print(response)
    print("\n")
except Exception as e:
    logger.error(f"An error occurred: {e}")

try:
    # Place Bracket Order
    print("#4Place Bracket Order")
    print("symbol :" + sym3)
    response = algomojo.PlaceBOOrder(broker=brcode,
                                     strategy="Python Example",
                                     exchange="NSE",
                                     symbol=sym3,
                                     action="BUY",
                                     pricetype="LIMIT",
                                     quantity="1",
                                     price="16.5",
                                     squareoff="2",
                                     stoploss="2",
                                     trailing_stoploss="1",
                                     trigger_price="0",
                                     disclosed_quantity="0")
    print(response)
    boorderid = response['data']['orderid']
    print("order id is :" + boorderid)
    print("\n")
except Exception as e:
    logger.error(f"An error occurred: {e}")

try:
    # Place Cover Order
    print("#5Place Cover Order")
    print("symbol :" + sym3)
    response = algomojo.PlaceCOOrder(broker=brcode,
                                     strategy="Python Example",
                                     exchange="NSE",
                                     symbol=sym3,
                                     action="BUY",
                                     pricetype="LIMIT",
                                     quantity="1",
                                     price="16.5",
                                     stop_price="15")
    print(response)
    coorderid = response['data']['orderid']
    print("order id is :" + coorderid)
    print("\n")
except Exception as e:
    logger.error(f"An error occurred: {e}")

try:
    # Place F&O Options Order to place orders in NSE Index Derivatives
    print("#6Place FOOptionsOrder")
    print("Expiry Date :" + opt_expiry)
    response = algomojo.PlaceFOOptionsOrder(broker=brcode,
                                            strategy="Python Example",
                                            spot_symbol="NIFTY",
                                            expiry_date=opt_expiry,
                                            action="BUY",
                                            product="NRML",
                                            pricetype="MARKET",
                                            quantity="50",
                                            price="0",
                                            option_type="CE",
                                            strike_int="50",
                                            offset="-2",
                                            splitorder="NO",
                                            split_quantity="50")
    print(response)
    print("\n")
except Exception as e:
    logger.error(f"An error occurred: {e}")

try:
    # PlaceSmartOrder to match the open positions
    print("#7PlaceSmartOrder to match the open positions")
    print("symbol :" + sym1)
    response = algomojo.PlaceSmartOrder(broker=brcode,
                                        strategy="Python Example",
                                        exchange="NSE",
                                        symbol=sym1,
                                        action="BUY",
                                        product="MIS",
                                        pricetype="MARKET",
                                        quantity="10",
                                        price="0",
                                        position_size="10",
                                        trigger_price="0",
                                        disclosed_quantity="0",
                                        amo="NO",
                                        splitorder="NO",
                                        split_quantity="1")
    print(response)
    print("\n")
except Exception as e:
    logger.error(f"An error occurred: {e}")

try:
    # PlaceStrategyOrder
    print("#8PlaceStrategyOrder")
    response = algomojo.PlaceStrategyOrder(strategy_id="ALGO", action="BUY")
    print(response)
    print("\n")

    # Place Multiple Orders to various brokers/same brokers
    print("#9 Place Multiple Orders to various brokers/same brokers")
    print("symbol1 :" + sym1)
    print("symbol2 :" + sym2)
    orders = [{"api_key": "your-api-key ", "api_secret": "your-api-secret", "broker": brcode, "symbol": sym1,
               "exchange": "NSE", "product": "MIS", "pricetype": "MARKET", "quantity": 4, "action": "BUY",
               "splitorder": "YES", "split_quantity": 2},
              {"api_key": "your-api-key ", "api_secret": "your-api-secret", "broker": brcode, "symbol": sym2,
               "exchange": "NSE", "product": "MIS", "pricetype": "MARKET", "quantity": 1, "price": "0",
               "action": "BUY"}]

    response = algomojo.PlaceMultiOrder(orders)
    print(response)
    print("\n")
except Exception as e:
    logger.error(f"An error occurred: {e}")

try:
    # Place Multiple Bracket Orders to various brokers/same brokers
    print("#10 Place Multiple Bracket Orders to various brokers/same brokers")
    print("symbol1 :" + sym3)
    print("symbol2 :" + sym4)
    orders = [{"api_key": "your-api-key ", "api_secret": "your-api-secret", "broker": brcode, "symbol": sym3,
               "exchange": "NSE", "pricetype": "MARKET", "quantity": 1, "action": "BUY", "squareoff": "2",
               "stoploss": "2", "trailing_stoploss": "1"},
              {"api_key": "your-api-key ", "api_secret": "your-api-secret", "broker": brcode, "symbol": sym4,
               "exchange": "NSE", "pricetype": "LIMIT", "quantity": 1, "price": "75.5", "action": "BUY",
               "squareoff": "2", "stoploss": "2", "trailing_stoploss": "1"}]
    response = algomojo.PlaceMultiBOOrder(orders)
    print(response)
    print("\n")
except Exception as e:
    logger.error(f"An error occurred: {e}")

try:
    print("#11 Place Multiple Options Orders to various brokers/same brokers")
    # Place Multiple Options Orders to the Same Broker/Different Brokers
    print("Expiry Date :" + opt_expiry)
    orders = [
        {"api_key": "your-api-key ", "api_secret": "your-api-secret", "broker": brcode, "strategy": "Options Spread",
         "spot_symbol": "NIFTY", "expiry_date": opt_expiry, "action": "SELL", "product": "NRML", "pricetype": "MARKET",
         "quantity": "100", "option_type": "CE", "strike_int": "50", "offset": "0", "splitorder": "NO",
         "split_quantity": "50"},
        {"api_key": "your-api-key ", "api_secret": "your-api-secret", "broker": brcode, "strategy": "Options Spread",
         "spot_symbol": "NIFTY", "expiry_date": opt_expiry, "action": "SELL", "product": "NRML", "pricetype": "MARKET",
         "quantity": "100", "option_type": "PE", "strike_int": "50", "offset": "0", "splitorder": "NO",
         "split_quantity": "50"}]

    response = algomojo.PlaceMultiFOOptionsOrder(orders)
    print(response)
    print("\n")
except Exception as e:
    logger.error(f"An error occurred: {e}")

try:
    # Place Modify Order
    print("#12 Place Modify  Orders")
    print("symbol :" + sym2)
    response = algomojo.ModifyOrder(broker=brcode,
                                    exchange="NSE",
                                    symbol=sym2,
                                    order_id=orderid,
                                    action="BUY",
                                    product="MIS",
                                    pricetype="LIMIT",
                                    price="56",
                                    quantity="10",
                                    disclosed_quantity="0",
                                    trigger_price="0")
    print(response)
    print("\n")
except Exception as e:
    logger.error(f"An error occurred: {e}")

try:
    # Cancel Order
    print("#13 Cancel Orders")
    print("Order ID :" + orderid)
    response = algomojo.CancelOrder(broker=brcode, order_id=orderid)
    print(response)
    print("\n")
except Exception as e:
    logger.error(f"An error occurred: {e}")

try:
    # Cancel All Order
    print("#14 Cancel All Orders")
    response = algomojo.CancelAllOrder(broker=brcode)
    print(response)
    print("\n")
except Exception as e:
    logger.error(f"An error occurred: {e}")

try:
    # Order History
    print("#15 Order History")
    print("Order ID :" + orderid)
    response = algomojo.OrderHistory(broker=brcode, order_id=orderid)
    print(response)
    print("\n")
except Exception as e:
    logger.error(f"An error occurred: {e}")

try:
    # Orderbook
    print("#16 Orderbook")
    response = algomojo.OrderBook(broker=brcode)
    print(response)
    print("\n")
except Exception as e:
    logger.error(f"An error occurred: {e}")

try:
    # OrderStatus
    print("#17 OrderStatus")
    print("Order ID :" + orderid)
    response = algomojo.OrderStatus(broker=brcode, order_id=orderid)
    print(response)
    print("\n")
except Exception as e:
    logger.error(f"An error occurred: {e}")

try:
    # TradeBook
    print("#18 TradeBook")
    response = algomojo.TradeBook(broker=brcode)
    print(response)
    print("\n")
except Exception as e:
    logger.error(f"An error occurred: {e}")

try:
    # PositionBook
    print("#19 PositionBook")
    response = algomojo.PositionBook(broker=brcode)
    print(response)
    print("\n")
except Exception as e:
    logger.error(f"An error occurred: {e}")

try:
    # OpenPositions
    print("#20 OpenPositions")
    print("Symbol :" + sym3)
    response = algomojo.OpenPositions(broker=brcode, symbol=sym3, product="MIS")
    print(response)
    print("\n")
except Exception as e:
    logger.error(f"An error occurred: {e}")

try:
    # SquareOffPosition
    print("#21 SquareOffPosition")
    print("Symbol :" + sym3)
    response = algomojo.SquareOffPosition(broker=brcode,
                                          exchange="NSE",
                                          product="MIS",
                                          symbol=sym3)
    print(response)
    print("\n")
except Exception as e:
    logger.error(f"An error occurred: {e}")

try:
    # SquareOffAllPosition
    print("#22 SquareOffAllPosition")
    response = algomojo.SquareOffAllPosition(broker=brcode)
    print(response)
    print("\n")
except Exception as e:
    logger.error(f"An error occurred: {e}")

try:
    # Holdings
    print("#23 Holdings")
    response = algomojo.Holdings(broker=brcode)
    print(response)
    print("\n")
except Exception as e:
    logger.error(f"An error occurred: {e}")

try:
    # Funds
    print("#24 Funds")
    response = algomojo.Funds(broker=brcode)
    print(response)
    print("\n")
except Exception as e:
    logger.error(f"An error occurred: {e}")

try:
    # ExitBOOrder
    print("#25 ExitBOOrder")
    print("Order ID :" + boorderid)
    response = algomojo.ExitBOOrder(broker=brcode, order_id=boorderid)
    print(response)
    print("\n")
except Exception as e:
    logger.error(f"An error occurred: {e}")

try:
    # ExitCOOrder
    print("#26 ExitCOOrder")
    print("Order ID :" + coorderid)
    response = algomojo.ExitCOOrder(broker=brcode, order_id=coorderid)
    print(response)
    print("\n")
except Exception as e:
    logger.error(f"An error occurred: {e}")

try:
    # GetQuote
    print("#27 GetQuote")
    response = algomojo.GetQuote(broker=brcode, exchange="NSE", symbol=sym1)
    print(response)
    print("\n")
except Exception as e:
    logger.error(f"An error occurred: {e}")

try:
    # Profile
    print("#28 Profile")
    response = algomojo.Profile(broker=brcode)
    print(response)
    print("\n")
except Exception as e:
    logger.error(f"An error occurred: {e}")
