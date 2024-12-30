import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
import pandas as pd

class Profit:
    def __init__(self) -> None:
        with open('src/bot_config.json' , 'r') as f:
            config = json.load(f)
        self.symbol = config.get('symbol')

    def profit_read(self) -> dict:
        with open('src/profit.json', 'r') as f:
            return json.load(f)
        
    def print_df(self) -> None:
        data = []
        for one_day in self.profit_read().get(self.symbol):
            data.append(one_day)
        df = pd.DataFrame(data)
        df.set_index('date', inplace=True)
        print(df)

profit = Profit()

if __name__ == '__main__':
    profit.print_df()
