from client.base import Base
from logging import getLogger
from modules.profit_manager import ProfitEdit
from scripts.averating import Averating
from scripts.first_buy import Buy
from scripts.sell import Sell
import time


logger = getLogger(__name__)


class Bot(Base):
    def __init__(self) -> None:
        super().__init__()
        self.profit_edit = ProfitEdit()
        self.averating_script = Averating()
        self.buy_script = Buy()
        self.sell_script = Sell()
        self.nem_notify_status = True

    def sell_notify(self) -> None:
        self.lines.clear()
        self.orders.clear()
        logger.debug('lines and orders clear. nem status: %s', self.nem_notify_status)
        time.sleep(2)
        last_order = self.orders.get_last_order()
        logger.info('Sold for %s', last_order)
        self.notify.sold(f'Sold for {last_order}')
        self.laps.add(self.laps.calculate_profit())
        self.nem_notify_status = False
        
    def not_enough_money_notify(self) -> None:
        logger.info('Not enough money')
        self.notify.warning('Not enough money!')
        self.nem_notify_status = False

    def start(self) -> None:
        self.notify.bot_status(f'Bot activated. Pair: {self.symbol}, balance: {self.account.get_balance()["USDT"]}')
        logger.info(f'Bot activated. Pair: {self.symbol}, balance: {self.account.get_balance()["USDT"]}')
        while True:
                time.sleep(3)
                self.profit_edit.add_profit()
                balance = self.account.get_balance()

                #Первая покупка
                if self.orders.qty() == 0:
                    logger.debug('trying "first buy"')
                    if float(balance.get('USDT')) > self.amount_buy:
                        logger.debug('activating first buy script')
                        self.buy_script.activate()

                #Усреднение
                if self.orders.qty() != 0:
                    logger.debug('trying "averaging"')
                    if float(balance.get('USDT')) > self.amount_buy: 
                        logger.debug('activating averaging script')
                        self.averating_script.activate()

                if self.lines.sell_lines_qty() > 0:
                    logger.debug('sell lines qty > 0. Activating sell script')
                    if self.sell_script.activate():
                        self.sell_notify()

                if self.orders.qty() != 0:
                    if self.nem_notify_status == False:
                        if(float(balance.get('USDT')) < self.amount_buy):
                            self.notifies_edit.not_enough_money_notify()


bot = Bot()