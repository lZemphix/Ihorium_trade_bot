import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
import time
import pandas as pd
from modules.telenotify import SendNotify
class Profit:
    def __init__(self) -> None:
        self.notify = SendNotify(True)

    def profit_read(self):
        with open('config/profit.json', 'r') as f:
            return json.load(f)
        
    def create_df(self):
        data = []
        for one_day in self.profit_read().get('SOLUSDT'):
            data.append(one_day)
        df = pd.DataFrame(data)
        df.set_index('date', inplace=True)
        return df
    
    def send_file(self):
        df = self.create_df()
        df.to_excel('report.xlsx')
        time.sleep(3)
        self.notify.bot_status('Generating report...')
        status_code = self.notify.send_file('report.xlsx')
        return status_code
    
profit = Profit()

if __name__ == '__main__':
    # try:
        print(Profit().create_df())
    # except Exception as e:
    #     print(e)