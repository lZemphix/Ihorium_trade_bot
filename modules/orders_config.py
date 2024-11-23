import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from typing import Any
from client import Account, Market

class OrdersEdit:

    def __init__(self, path: str = 'config/.orders') -> None:
       self.path = path

       self.account = Account()
       self.market = Market()

    def get_last_order(self) -> float:
        last_order = self.account.get_orders().get('result').get('list')[0].get('avgPrice')
        return float(last_order)
    
    def get_open_orders(self) -> bool:
        open_orders = self.account.client.get_open_orders(category='spot')
        return False if open_orders.get('result').get('list') == [] else True

    def add(self, data: Any) -> int:
        with open(self.path, 'a') as f:
            f.write(f'{str(data)}\n')
        return 200
    
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
        
    
    def avg_order(self) -> float:
        avg = sum(self.get()) / (self.qty() if self.qty() != 0 else 1)
        return avg
    
    def get_sum(self) -> float:
        return sum(self.get())
    

orders = OrdersEdit()

if __name__ == '__main__':
    try:
        print(orders.get())
    except Exception as e:
        print(e)
