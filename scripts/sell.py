from logging import getLogger
import ta
from client.base import Base
from modules.notifies_manager import NotifiesEdit

logger = getLogger(__name__)

class Sell(NotifiesEdit, Base):
     
    def __init__(self) -> None:
        super().__init__()
        self.nem_notify_status = True

    def __init(self) -> None:
        try:
            df = self.graph.get_kline_dataframe()
            actual_rsi = ta.momentum.rsi(df.close).iloc[-1]
            actual_price = self.market.get_actual_coin_price()
            sell_price = self.orders.avg_order() + self.stepSell
            rsi_diff = actual_rsi > self.RSI + 1
            actual_price_higher = sell_price < actual_price
            logger.debug('init success')
            return rsi_diff, actual_price_higher
        except:
            logger.debug('init succes with incorrect data')
            return False, False

    def order_line_notify_config(self) -> None:
        self.lines.clear()
        self.orders.clear()
        self.notifies_edit.sell_notify()
        self.nem_notify_status = False
        logger.debug('lines and orders clear. nem status: %s', self.nem_notify_status)

    def activate(self) -> None:
        rsi_diff, actual_price_higher = self.__init()
        if rsi_diff:
            logger.debug('rsi diff: success')
            if self.lines.cross_utd():
                logger.debug('cross up to down: success')
                # if actual_price_higher:
                logger.debug('actual price higher than avg buy price')
                self.market.place_sell_order()
                        
                