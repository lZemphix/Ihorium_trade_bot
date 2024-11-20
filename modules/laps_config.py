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
        with open('config/bot_config.json', 'r') as f:
            config = json.load(f)
            step = config.get('stepSell')
            coin_price = float(self.market.get_actual_coin_price())
            amount_buy = config.get('amountBuy')
            approx_profit = round((amount_buy/(0.01*(coin_price - step))*(coin_price*0.01)) - amount_buy, 3)
            return approx_profit

    def add(self, data: Any) -> int:
        with open(self.path, 'a') as f:
            f.write(f'{data}\n')
        return 200
    

if __name__ == '__main__':
    try:
        LapsEdit().test()
    except Exception as e:
        print(e)
