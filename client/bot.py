from client.base import Base
from logging import getLogger
from modules.notifies_manager import NotifiesEdit
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
        self.notifies_edit = NotifiesEdit()
        self.averating_script = Averating()
        self.buy_script = Buy()
        self.sell_script = Sell()
        

    def start(self):
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
                    self.sell_script.activate()

                if self.orders.qty() != 0:
                    if self.sell_script.nem_notify_status == False:
                        if(float(balance.get('USDT')) < self.amount_buy):
                            self.notifies_edit.not_enough_money_notify()


bot = Bot()