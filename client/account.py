from client.client import Client

class Account(Client):

    def __init__(self) -> None:
        super().__init__()

    def get_orders(self) -> tuple:
        try:
            orders = self.client.get_order_history(category='spot')
            return orders
        except:
            return ()

    def get_balance(self) -> dict:   
        try:
            coin_values: dict[str, dict[float]] = {}
            get_balance = self.client.get_wallet_balance(accountType=self.accountType)['result']['list'][0]['coin']
            for n in range(len(get_balance)):
                coin_values[get_balance[n].get('coin')] = (get_balance[n].get('walletBalance'))
            if coin_values != {}:
                return coin_values
        except Exception as e:
            print(e)
            return {}
