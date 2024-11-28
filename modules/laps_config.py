import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
from client import Account, Market
from typing import Any

class LapsEdit:

    def __init__(self, path: str = 'config/.laps') -> None:
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
    
    

if __name__ == '__main__':
    try:
        LapsEdit().test()
    except Exception as e:
        print(e)
