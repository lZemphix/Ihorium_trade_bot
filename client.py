import json
from pybit.unified_trading import HTTP
from pybit._http_manager import FailedRequestError
import logging
from dotenv import load_dotenv
import os
import pandas as pd
from exceptions import exceptions as e


logging.basicConfig(level=logging.INFO, filename='logs/logs.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%m-%Y %H:%M:%S')

load_dotenv()

class Client:


    def __init__(self) -> None:
        """symbol: 'SOLUSDT' for example
        interval: 1,5,10,15,30,60
        amount_buy: min. 3.6
        """
        with open('config/bot_config.json', 'r') as f:
            config = json.load(f)

        self.API_KEY = os.getenv("API_KEY")
        self.API_KEY_SECRET = os.getenv("API_KEY_SECRET")
        self.accountType = os.getenv("ACCOUNT_TYPE")
        self.symbol = config.get('symbol')
        self.amount_buy = config.get('amountBuy')
        self.interval = config.get('interval')
        self.client = HTTP(testnet = False, api_key=self.API_KEY, api_secret=self.API_KEY_SECRET)

class Graph(Client):

    def __init__(self) -> None:
            super().__init__()

    def get_kline(self) -> dict | FailedRequestError:
        try:
            kline = self.client.get_kline(symbol=self.symbol, interval=self.interval)
            return kline
        except FailedRequestError as e:
            logging.error(e)
            return f"ErrorCode: {e.status_code}"

    def get_kline_dataframe(self) -> pd.DataFrame:
        dataframe = pd.DataFrame(self.get_kline()['result']['list'])
        dataframe.columns = ['time', 'open', 'high', 'low', 'close', 'volume', 'turnover']
        dataframe.set_index('time', inplace=True)
        dataframe.index = pd.to_numeric(dataframe.index, downcast='integer').astype('datetime64[ms]')    
        dataframe = dataframe[::-1]
        dataframe['close'] = pd.to_numeric(dataframe['close'])
        return dataframe
    
    def get_kline_4h(self):
        try:
            kline = self.client.get_kline(symbol=self.symbol, interval='240')
            return kline
        except FailedRequestError as e:
            logging.error(e)
            return f"ErrorCode: {e.status_code}"

    def get_kline_dataframe_4h(self) -> pd.DataFrame:
        dataframe = pd.DataFrame(self.get_kline_4h()['result']['list'])
        dataframe.columns = ['time', 'open', 'high', 'low', 'close', 'volume', 'turnover']
        dataframe.set_index('time', inplace=True)
        dataframe.index = pd.to_numeric(dataframe.index, downcast='integer').astype('datetime64[ms]')    
        dataframe = dataframe[::-1]
        dataframe['close'] = pd.to_numeric(dataframe['close'])
        return dataframe
    
class Account(Client):

    def __init__(self) -> None:
        super().__init__()

    def get_orders(self) -> tuple:
        orders = self.client.get_order_history(category='spot')
        return orders
    
    def get_open_positions(self) -> bool:
        open_orders = self.client.get_open_orders(category='spot')
        return open_orders.get('result').get('list')[0]


    def get_balance(self) -> dict:   
        try:
            coin_values: dict[str, dict[float]] = {}
            get_balance = self.client.get_wallet_balance(accountType=self.accountType)['result']['list'][0]['coin']
            for n in range(len(get_balance)):
                coin_values[get_balance[n].get('coin')] = (get_balance[n].get('walletBalance'))
            if coin_values != {}:
                return coin_values
            else:
                raise e.BalanceException('Balance is empty!')
        except FailedRequestError:
            logging.error(e)
            return f"RequestError!"


class Market(Client):

    def __init__(self) -> None:
        super().__init__()


    def place_buy_order(self) -> None | FailedRequestError:
        try:
            if self.amount_buy >= 3.6:
                order = self.client.place_order(
                    category='spot',
                    symbol=self.symbol,
                    side='Buy',
                    orderType='Market',
                    qty=self.amount_buy,
                )
            else:
                raise e.OrderException('Amount buy less than 3.6!')
        except FailedRequestError as e:
            logging.error(e)
            return f"ErrorCode: {e.status_code}"

    def place_sell_order(self, price: int) -> FailedRequestError | None:
        try:
            amount = float(Account().get_balance().get('SOL')[:5])
            order = self.client.place_order(
                category='spot',
                symbol=self.symbol,
                side='Sell',
                orderType='Limit',
                price=round(price, 2),
                qty=amount
            )
        except FailedRequestError as e:
            logging.error(e)
            return f"ErrorCode: {e.status_code}"

    def get_actual_price(self) -> dict | FailedRequestError:
        orderbook = self.client.get_orderbook(symbol=self.symbol, category='spot')
        return float(orderbook.get('result').get('a')[0][0])
    
    def cancel_order(self) -> FailedRequestError | None:
        try:
            order = self.client.cancel_order(
                category='spot',
                symbol=self.symbol,
                orderLinkId = Account().get_open_positions().get('orderLinkId')
            )
        except FailedRequestError as e:
            logging.error(e)
            return f"ErrorCode: {e.status_code}"
    

if __name__ == '__main__':
    try:
        # print(Account().get_open_positions())
        
        pass
    except Exception as e:
        print(e)
