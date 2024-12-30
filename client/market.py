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
            amount = float(Account().get_balance().get('SOL')[:5])
            self.client.place_order(
                category='spot',
                symbol=self.symbol,
                side='Sell',
                orderType='Market',
                qty=amount
            )
        except:
            self._purchase()
            time.sleep(2)
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
