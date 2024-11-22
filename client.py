import json
from pybit.unified_trading import HTTP
from pybit._http_manager import FailedRequestError
from logging import getLogger
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()

logger = getLogger(__name__)

class Client:
    def __init__(self) -> None:
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

    def get_kline(self, limit: int = 200) -> dict:
        try:
            kline = self.client.get_kline(symbol=self.symbol, interval=self.interval, limit=limit, category='spot')
            return kline
        except FailedRequestError as e:
            logger.error(e)
            return f"ErrorCode: {e.status_code}"

    def get_kline_dataframe(self) -> pd.DataFrame:
        dataframe = pd.DataFrame(self.get_kline()['result']['list'])
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

    def get_balance(self) -> dict:   
        try:
            coin_values: dict[str, dict[float]] = {}
            get_balance = self.client.get_wallet_balance(accountType=self.accountType)['result']['list'][0]['coin']
            for n in range(len(get_balance)):
                coin_values[get_balance[n].get('coin')] = (get_balance[n].get('walletBalance'))
            if coin_values != {}:
                return coin_values
        except FailedRequestError as e:
            logger.error(e)
            return f"RequestError!"


class Market(Client):

    def __init__(self) -> None:
        super().__init__()

    def place_buy_order(self) -> int:
        try:
            if self.amount_buy >= 3.6:
                order = self.client.place_order(
                    category='spot',
                    symbol=self.symbol,
                    side='Buy',
                    orderType='Market',
                    qty=self.amount_buy,
                )
        except FailedRequestError as e:
            logger.error(e)
            return f"ErrorCode: {e.status_code}"

    def place_sell_order(self) -> None:
        try:
            amount = float(Account().get_balance().get('SOL')[:5])
            order = self.client.place_order(
                category='spot',
                symbol=self.symbol,
                side='Sell',
                orderType='Market',
                qty=amount
            )
        except:
            self._purchase()
            self.place_sell_order()

    def _purchase(self) -> None:
        amount = float(Account().get_balance().get('SOL')[:7])
        if amount < 0.0231:
            self.client.place_order(
                    category='spot',
                    symbol=self.symbol,
                    side='Buy',
                    orderType='Market',
                    qty=1,
                )


    def get_actual_coin_price(self) -> float:
        orderbook = self.client.get_orderbook(symbol=self.symbol, category='spot')
        actual_price = float(orderbook.get('result').get('a')[0][0])
        return actual_price
    
    def cancel_order(self) -> None:
        try:
            order = self.client.cancel_order(
                category='spot',
                symbol=self.symbol,
                orderLinkId = Account().get_open_positions().get('orderLinkId')
            )
        except FailedRequestError as e:
            logger.error(e)
            return f"ErrorCode: {e.status_code}"

if __name__ == '__main__':
    try:
        Market()._purchase()
        # Market().place_buy_order()
    except Exception as e:
        print(e)
