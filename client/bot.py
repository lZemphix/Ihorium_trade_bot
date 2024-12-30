from client.base import Base
from logging import getLogger
from modules.profit_manager import ProfitEdit
import ta.momentum
import time
import ta

logger = getLogger(__name__)

nem_notify_status = False

class Bot(Base):
    def __init__(self) -> None:
        super().__init__()
        self.profit_edit = ProfitEdit()
        self.notifies_edit = NotifiesEdit()

    def first_buy(self) -> None:
        df = self.graph.get_kline_dataframe()
        actual_rsi = ta.momentum.rsi(df.close).iloc[-1]
        if actual_rsi < self.RSI:
            if self.lines.read('buy') == '':
                self.market.place_buy_order()
                time.sleep(1)
                balance = self.account.get_balance()
                logger.info('Actual rsi= %s, balance= %s', actual_rsi, balance['USDT'])
                last_order = self.orders.get_last_order()
                self.orders.add(last_order)
                self.lines.write(last_order)
                with open('src/.sell_lines', 'r') as f:
                    min_for_sell = f.readline()
                    logger.info(f'First buy for ${last_order}.\nBalance: {balance["USDT"]}.\nMinimal price for sell: ${min_for_sell}')
                    self.notify.bought(f'First buy for ${last_order}.\nBalance: {balance["USDT"]}.\nMinimal price for sell: ${min_for_sell}')

    def averaging(self) -> None:
        df = self.graph.get_kline_dataframe()
        actual_rsi = ta.momentum.rsi(df.close).iloc[-1] if not df.empty else self.RSI + 1
        balance = self.account.get_balance()
        price_now = self.market.get_actual_coin_price()

        if actual_rsi <= self.RSI:
            if float(balance['USDT']) > self.amount_buy:
                if self.lines.cross_dtu():
                    price_diff = (self.orders.get_last_order()- price_now)
                    if price_diff > self.stepBuy:
                        self.market.place_buy_order()
                        time.sleep(1)
                        balance = self.account.get_balance()
                        logger.info('Аctual rsi= %s, balance= %s', actual_rsi, balance['USDT'])
                        last_order = self.orders.get_last_order()
                        self.orders.add(last_order)
                        self.lines.write(self.orders.avg_order(), 'sell')
                        self.lines.write(last_order)
                        time.sleep(1)
                        with open('src/.sell_lines', 'r') as f:
                            min_for_sell = f.readline()
                        logger.info(f'Averating for ${last_order}. Balance: {balance["USDT"]}. Minimal price for sell: {min_for_sell}')
                        self.notify.bought(f'Averating for ${last_order}. Balance: {balance["USDT"]}. Minimal price for sell: {min_for_sell}')
                    

    def selling(self):
        df = self.graph.get_kline_dataframe()
        global nem_notify_status
        actual_rsi: float = ta.momentum.rsi(df.close).iloc[-1]
        if actual_rsi > self.RSI + 2:
            if self.lines.cross_utd():
                if (self.orders.avg_order() + self.stepSell) < self.market.get_actual_coin_price():
                    self.market.place_sell_order()
                    self.lines.clear()
                    self.orders.clear()
                    self.notifies_edit.sell_notify()
                    nem_notify_status = False
            else:
                pass

    def start(self):
        self.notify.bot_status(f'Bot activated. Pair: {self.symbol}, balance: {self.account.get_balance()["USDT"]}')
        logger.info(f'Bot activated. Pair: {self.symbol}, balance: {self.account.get_balance()["USDT"]}')
        while True:
                time.sleep(3)
                df = self.graph.get_kline_dataframe()
                self.profit_edit.add_profit()
                balance = self.account.get_balance()

                #Первая покупка
                if self.orders.qty() == 0:
                    if float(balance.get('USDT')) > self.amount_buy:
                        self.first_buy()

                #Усреднение
                if self.orders.qty() != 0:
                    if float(balance.get('USDT')) > self.amount_buy:                    
                        self.averaging()

                if self.lines.sell_lines_qty() > 0:
                    self.selling()

                if self.orders.qty() != 0:
                    global nem_notify_status
                    if nem_notify_status == False:
                        if(float(balance.get('USDT')) < self.amount_buy):
                            self.notifies_edit.not_enough_money_notify()

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
            logger.info('Sold for %s', last_order)
            self.notify.sold(f'Sold for {last_order}')
            self.laps.add(self.laps.calculate_profit())

bot = Bot()