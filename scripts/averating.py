from logging import getLogger
import time
import ta
from client.base import Base

logger = getLogger(__name__)

class Averating(Base):

    def __init__(self) -> None:
        super().__init__()

    def __init(self) -> tuple:
        df = self.graph.get_kline_dataframe()
        try:
            actual_rsi = ta.momentum.rsi(df.close).iloc[-1] if not df.empty else self.RSI + 1
            balance = self.account.get_balance()
            price_now = self.market.get_actual_coin_price()
            price_diff = (self.orders.get_last_order() - price_now)
            logger.debug('init success')
        except:
            actual_rsi = self.RSI + 1
            balance = {"USDT": (self.amount_buy - 1)}
            price_diff = -1
            logger.debug('init success with incorrect data')

        rsi_diff = actual_rsi <= self.RSI
        enough_money = float(balance['USDT']) > self.amount_buy
        return balance, price_diff, rsi_diff, enough_money

    def __orders_and_lines_control(self, last_order: float) -> None:
        self.orders.add(last_order)
        self.lines.write(self.orders.avg_order(), 'sell')
        self.lines.write(last_order)

    def __notify_control(self, last_order: float, balance: dict):
        with open('src/.sell_lines', 'r') as sell:
            min_for_sell = sell.readline()
            with open('src/.buy_lines', 'r') as buy:
                min_for_buy = buy.readline()
                logger.info(f'Averating for ${last_order}.\nBalance: {balance["USDT"]}\nClosest sell line: ${min_for_sell}\nClosest buy line: ${min_for_buy}')
                self.notify.bought(f'Averating for ${last_order}. Balance: {balance["USDT"]}\nClosest sell line: ${min_for_sell}\nClosest buy line: ${min_for_buy}')

    def activate(self) -> None:
        balance, price_diff, rsi_diff, enough_money = self.__init()
        if rsi_diff:
            logger.debug('rsi diff: success')
            if enough_money:
                logger.debug('enough money: success')
                if self.lines.cross_dtu():
                    logger.debug('cross down to up: success')
                    if price_diff > self.stepBuy:
                        logger.debug('price diff > buy step\'s')
                        self.market.place_buy_order()
                        logger.debug('buy order placed')
                        balance = self.account.get_balance()
                        time.sleep(1)
                        last_order = self.orders.get_last_order()
                        self.__orders_and_lines_control(last_order)
                        time.sleep(1)
                        self.__notify_control(last_order, balance)
                        