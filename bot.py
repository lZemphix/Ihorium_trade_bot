from datetime import datetime
import json
import ta, time
from modules.laps_config import LapsEdit
import ta.momentum
from client import Account, Market, Graph
from logging import getLogger
from modules.telenotify import SendNotify
from modules.orders_config import OrdersEdit
from modules.lines_control import Lines

logger = getLogger(__name__)

nem_notify_status = False

class Base:
    def __init__(self) -> None:

        bot_config = self.get_config()

        self.symbol: str = bot_config.get('symbol')
        self.interval: str = bot_config.get('interval')
        self.amount_buy: float = bot_config.get('amountBuy')
        self.stepBuy: float = bot_config.get('stepBuy')
        self.stepSell: float = bot_config.get('stepSell')
        self.send_notify: bool = bot_config.get('send_notify')
        self.RSI: float = bot_config.get('RSI')
        
        self.orders = OrdersEdit()
        self.account = Account()
        self.market = Market()
        self.graph = Graph()
        self.laps = LapsEdit()
        self.lines = Lines()
        self.notify = SendNotify(True if self.send_notify else False)
        

    @staticmethod
    def get_config():
        with open('config/bot_config.json', 'r') as f:
            return json.load(f)

class Bot(Base):
    def __init__(self) -> None:
        super().__init__()
        self.profit_edit = ProfitEdit()
        self.notifies_edit = NotifiesEdit()


    def first_buy(self) -> int:
        df = self.graph.get_kline_dataframe()
        balance = self.account.get_balance()
        actual_rsi = ta.momentum.rsi(df.close).iloc[-1]
        if actual_rsi < self.RSI and \
                self.lines.read('sell') == '':
                    logger.info('if: actual rsi= %s, balance= %s', actual_rsi, balance['USDT'])
                    self.market.place_buy_order()
                    time.sleep(0.1)
                    last_order = self.orders.get_last_order()
                    self.orders.add(last_order)
                    self.lines.write(last_order)
                    logger.info('First bought!')
                    self.notify.bought(f'The bot bought at price {last_order}')

    def averaging(self) -> None:
        df = self.graph.get_kline_dataframe()
        price_now = self.market.get_actual_coin_price()
        actual_rsi = ta.momentum.rsi(df.close).iloc[-1]
        price_diff = (self.orders.get_last_order()- price_now)
        balance = self.account.get_balance()

        if actual_rsi < self.RSI:
            if price_diff > self.stepBuy:
                if float(balance['USDT']) > self.amount_buy:
                    self.market.place_buy_order()
                    time.sleep(3)

                    self.orders.add(self.orders.get_last_order())
                    self.lines.write(self.orders.avg_order())

                    time.sleep(3)

                    last_order = self.orders.get_last_order()
                    logger.info(f'averating {last_order}')
                    self.notify.bought(f'The bot bought again at price {last_order}')

    def selling(self):
        global nem_notify_status
        df = self.graph.get_kline_dataframe()
        actual_rsi: float = ta.momentum.rsi(df.close).iloc[-1]
        if self.lines.cross_utd() and\
            actual_rsi > self.RSI + 2:
                self.market.place_sell_order()
                self.lines.clear()
                self.orders.clear()
                self.notifies_edit.sell_notify()
                nem_notify_status = False


    def start(self):
        self.notify.bot_status(f'Bot started trading on pair {self.symbol}')
        logger.info('Bot started trading on pair %s', self.symbol)
        while True:
                self.profit_edit.add_profit()
                balance = self.account.get_balance()

                #Первая покупка
                if (not self.orders.get_open_orders()) \
                    and float(balance.get('USDT')) > self.amount_buy:
                        self.first_buy()

                #Усреднение
                if self.orders.qty() != 0 \
                    and float(balance.get('USDT')) > self.amount_buy:                    
                        self.averaging()

                if self.lines.sell_lines_qty() > 0 \
                    and (self.orders.avg_order() + self.stepSell) < self.market.get_actual_coin_price():
                        self.selling()

                if self.orders.qty() != 0 \
                    and (float(balance.get('USDT')) < self.amount_buy):
                        global nem_notify_status
                        if nem_notify_status == False:
                            self.notifies_edit.not_enough_money_notify()
        


class ProfitEdit(Base):
    def __init__(self) -> None:
        super().__init__()
    
    def _make_profit(self, balance: int, date: str, laps_: int = 0, profit: float = 0.0) -> dict:
        new_entry = {
            'date': date,
            'balance': balance,
            'laps': laps_,
            'profit': profit}
        
        return new_entry
        
    def write_first_profit(self, balance: int, date: str) -> None:
        entry = self._make_profit(balance, date, 0, 0)
        with open('config/profit.json' , 'w') as file: 
            json.dump({'SOLUSDT': [entry]}, file, indent=4)

    def write_profit(self, balance: int, date: str, laps_: int, profit: float) -> None:
            with open('config/profit.json', 'r') as f:
                existing_data = json.load(f)
                new_entry = self._make_profit(balance, date, laps_, profit)
                existing_data['SOLUSDT'].append(new_entry)
            with open('config/profit.json', 'w') as f:
                json.dump(existing_data, f, indent=4)

    def add_profit(self):
        get_balance = self.account.get_balance()
        balance_usdt =float(get_balance.get('USDT'))
        balance_sol = float(get_balance.get('SOL')) * self.market.get_actual_coin_price()
        balance = round(balance_sol + balance_usdt, 2)
        try:
            with open('config/profit.json', 'r') as f:
                data = json.load(f)
                print(data)
                last_date = data.get('SOLUSDT')[-1].get('date')
                last_date = datetime.strptime(last_date ,'%Y-%m-%d %H:%M:%S')
                print(last_date)
                time_diff = (datetime.now() - last_date).total_seconds()
                if time_diff > 86399:
                    print('times')
                    actual_date = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    profit = round(sum(self.laps.get()), 3)
                    self.write_profit(balance, actual_date, self.laps.qty(), profit)

        except:
            actual_date = f"{datetime.now().strftime('%Y-%m-%d')} 23:59:59"
            self.write_first_profit(balance, actual_date)

class NotifiesEdit(Base):
    def __init__(self) -> None:
        super().__init__()

    def not_enough_money_notify(self) -> None:
        global nem_notify_status
        logger.info('Not enough money')
        self.notify.warning('Not enough money!')
        nem_notify_status = True

    def sell_notify(self) -> None:
            time.sleep(2)
            last_order = self.orders.get_last_order()
            logger.info('sold for %s', last_order)
            self.notify.sold(f'Bot close the position at {last_order}')
            self.laps.add(self.laps.calculate_profit())

bot = Bot()

# config = bot.get_config()
if __name__ == '__main__':
    ProfitEdit().add_profit()
    pass
