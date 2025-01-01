import time
from client.account import Account
from client.client import Client


class Market(Client):

    def __init__(self) -> None:
        super().__init__()

    def place_buy_order(self) -> None:
        try:
            self.client.place_order(
                category='spot',
                symbol=self.symbol,
                side='Buy',
                orderType='Market',
                qty=self.amount_buy,
            )
        except:
            return None

    def place_sell_order(self) -> None:
        try:
            coin_name = self.symbol[:-4]
            amount = float(Account().get_balance().get(coin_name)[:4])
            self.client.place_order(
                category='spot',
                symbol=self.symbol,
                side='Sell',
                orderType='Market',
                qty=amount
            )
        except Exception as e:
            print(e)

    def get_actual_coin_price(self) -> float:
        try:
            orderbook = self.client.get_orderbook(symbol=self.symbol, category='spot')
            actual_price = float(orderbook.get('result').get('a')[0][0])
            return actual_price
        except:
            time.sleep(2)
            self.get_actual_coin_price()
    
    def cancel_order(self) -> None:
        try:
            self.client.cancel_order(
                category='spot',
                symbol=self.symbol,
                orderLinkId = Account().get_open_positions().get('orderLinkId')
            )
        except:
            pass
