from logging import getLogger
from client.base import Base
import time
import ta

logger = getLogger(__name__)

class Buy(Base):
    
    def __init__(self):
        super().__init__()

    def __init(self):
        try:
            df = self.graph.get_kline_dataframe()
            actual_rsi = ta.momentum.rsi(df.close).iloc[-1]
            logger.debug('init success')
        except:
            actual_rsi = self.RSI + 1
            logger.debug('init success w incorrect data')
        return actual_rsi

    def __orders_and_lines_control(self, last_order: float, balance: dict, actual_rsi: float) -> None:
        self.orders.add(last_order)
        self.lines.write(last_order)

    def __first_buy_notify(self, last_order: float, balance: dict) -> None:
        with open('src/.sell_lines', 'r') as sell:
            min_for_sell = sell.readline()
            with open('src/.buy_lines', 'r') as buy:
                min_for_buy = buy.readline()
                logger.info(f'First buy for ${last_order}\nBalance: {balance["USDT"]}\nClosest sell line: ${min_for_sell}\nClosest buy line: ${min_for_buy}')
                self.notify.bought(f'First buy for ${last_order}\nBalance: {balance["USDT"]}\nClosest sell line: ${min_for_sell}\nClosest buy line: ${min_for_buy}')

    def activate(self) -> None:
        actual_rsi = self.__init()
        if actual_rsi < self.RSI:
            logger.debug('RSI > actual rsi')
            if self.lines.read('buy') == '':
                logger.debug('lines clear: success')
                self.market.place_buy_order()
                logger.debug('buy order placed')
                time.sleep(1)
                balance = self.account.get_balance()
                last_order = self.orders.get_last_order()
                self.__orders_and_lines_control(last_order=last_order, balance=balance, actual_rsi=actual_rsi)
                self.__first_buy_notify(last_order=last_order, balance=balance)
    
    