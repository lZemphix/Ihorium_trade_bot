from datetime import datetime
from logging import getLogger
from modules.laps_config import LapsEdit
import json

logger = getLogger(__name__)

class ProfitEdit:
    # DONT WORK!!!
    def __init__(self) -> None:
        with open('config/bot_config.json', 'r') as f:
            config = json.load(f)
        self.symbol = config.get('symbol')
        self.path = 'src/profit.json'
        self.laps = LapsEdit()
    
    def _make_profit(self, balance: int, date: str, laps_: int = 0, profit: float = 0.0) -> dict:
        new_entry = {
            'date': date,
            'balance': balance,
            'laps': laps_,
            'profit': profit}
        
        return new_entry
        
    def write_first_profit(self, balance: int, date: str) -> None:
        entry = self._make_profit(balance, date, 0, 0)
        with open(self.path, 'w') as file: 
            json.dump({self.symbol: [entry]}, file, indent=4)

    def write_profit(self, balance: int, date: str, laps_: int, profit: float) -> None:
            with open(self.path, 'r') as f:
                existing_data = json.load(f)
                new_entry = self._make_profit(balance, date, laps_, profit)
                existing_data[self.symbol].append(new_entry)
            with open(self.path, 'w') as f:
                json.dump(existing_data, f, indent=4)
                self.laps.clear()

    def add_profit(self):
        try:
            get_balance = self.account.get_balance()
            balance_usdt =float(get_balance.get('USDT'))
            balance_coin = float(get_balance.get(self.coin_name)) * self.market.get_actual_coin_price()
        except:
            balance_usdt = 0
            balance_coin = 0
        balance = round(balance_coin + balance_usdt, 2)
        try:
            with open(self.path, 'r') as f:
                data = json.load(f)
                last_date = data.get(self.symbol)[-1].get('date')
                last_date = datetime.strptime(last_date ,'%Y-%m-%d %H:%M:%S')
                time_diff = (datetime.now() - last_date).total_seconds()
                if time_diff > 86399:
                    actual_date = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    profit = sum(self.laps.get())
                    self.write_profit(balance, actual_date, self.laps.qty(), profit)

        except:
            logger.warning('exception add profit')
            actual_date = f"{datetime.now().strftime('%Y-%m-%d')} 23:59:59"
            self.write_first_profit(balance, actual_date)
