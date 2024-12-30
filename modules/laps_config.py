from client.account import Account
from client.market import Market
from typing import Any

class LapsEdit:

    def __init__(self, path: str = 'src/.laps') -> None:
       self.path = path
       self.account = Account()
       self.market = Market()

    def clear(self) -> int:
        with open(self.path, 'w') as f:
            pass
        return 200
    
    def get(self) -> list[float]:
        with open(self.path, 'r') as f:
            file = f.readlines()
            return [float(el.replace('\n', '')) for el in file if el != '']
        
    def qty(self) -> int:
        orders = self.get()
        return len(orders)
        
    def avg_lap_profit(self) -> float:
        avg = sum(self.get()) / self.qty()
        return round(avg,3)
    
    def calculate_profit(self) -> float:
        orders = self.account.get_orders()['result']['list']
        sell_price = 0
        values = []
        for order in orders:
            if order.get('side') == 'Sell' and sell_price == 0:
                sell_price = float(order.get('cumExecValue'))
            elif order.get('side') == 'Buy':
                values.append(float(order.get('cumExecValue')))
            else:
                break
        profit = round(sell_price - sum(values), 3)
        return profit

    def add(self, data: Any) -> int:
        with open(self.path, 'a') as f:
            f.write(f'{data}\n')
        return 200