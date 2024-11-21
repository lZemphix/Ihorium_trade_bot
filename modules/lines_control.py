import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
from modules import lines_control
import client
from logging import getLogger

logger = getLogger(__name__)


class Lines:
    def __init__(self) -> None: 
        self.sell_lines_path = 'config/.sell_lines'
        self.buy_lines_path = 'config/.buy_lines'

    def _create(self, buy_price: float) -> None:
        with open('config/bot_config.json' , 'r') as f:
            config = json.load(f)
            sell_lines, buy_lines = [], []
            lines_amount = config.get('lines')
            step_buy = config.get('stepBuy')
            step_sell = config.get('stepSell')
            for i in range(lines_amount):
                sell_lines.append(round(buy_price+step_sell*(i+1), 2))
                buy_lines.append(round(buy_price-step_buy*(i+1),2))
            return sell_lines, buy_lines
        
    def write(self, buy_price: float, mode: str = 'both'):
        sell_lines, buy_lines = self._create(buy_price)
        if mode == 'both':
            with open(self.buy_lines_path, 'w') as buy:
                with open(self.sell_lines_path, 'w') as sell:
                    for sells, buys in zip(sell_lines, buy_lines):
                        buy.write(f'{buys}\n')
                        sell.write(f'{sells}\n')

        elif mode == 'sell':
            with open(self.sell_lines_path, 'w') as sell:
                for sells in sell_lines:
                    sell.write(f'{sells}\n')

        elif mode == 'buy':
            with open(self.buy_lines_path, 'w') as buy:
                for buys in buy_lines:
                    buy.write(f'{buys}\n')

    def sell_lines_qty(self):
        with open(self.sell_lines_path, 'r') as file:
            sell = file.read()
            qty = len(sell.split('\n')) - 1
            return qty if sell != '' else 0

    def buy_lines_qty(self):
        with open(self.buy_lines_path, 'r') as file:
            buy = file.read()
            qty = len(buy.split('\n')) - 1
            return qty if buy != '' else 0

    def read(self, mode: str = 'both'):
        """
        both: sell, buy
        """
        if mode == 'both':
            with open(self.buy_lines_path, 'r') as buy:
                with open(self.sell_lines_path, 'r') as sell:
                    sells = sell.read()
                    buys = buy.read()
                    return sells, buys

        elif mode == 'sell':
            with open(self.sell_lines_path, 'r') as sell:
                return sell.read().rstrip()

        elif mode == 'buy':
            with open(self.buy_lines_path, 'r') as buy:
                return buy.read()
        else:
            logger.error('Modes: both, sell or buy')
    
    def clear(self, mode: str = 'both'):
        if mode == 'both':
            with open(self.buy_lines_path, 'w'):
                pass
            with open(self.sell_lines_path, 'w'):
                pass

        elif mode == 'sell':
            with open(self.sell_lines_path, 'w'):
                pass

        elif mode == 'buy':
            with open(self.buy_lines_path, 'w'):
                pass


    def check_uper_line(self):
        lines = lines_control.Lines()
        market = client.Market()
        actual_price = market.get_actual_coin_price()
        sell_lines = lines.read('sell')
        count = 0
        f_sell_lines = [item for item in sell_lines.split('\n') if item != '']
        for line in f_sell_lines:
            if actual_price > float(line):
                count += 1
        return count
        
    def cross_utd(self):
        lines = lines_control.Lines()
        market = client.Market()
        graph = client.Graph()
        sell_lines = lines.read('sell')
        last_two_klines = graph.get_kline(2)['result'].get('list')
        last_kline = float(last_two_klines[1][4])
        actual_price = market.get_actual_coin_price()

        for sell_line in sell_lines.split('\n')[::-1]:
            if last_kline > float(sell_line):
                if actual_price < float(sell_line) and actual_price < last_kline:
                    logger.info('last_knile= %s, sell_line= %s, actual_price= %s', last_kline, sell_line, actual_price)
                    return True
                        
    def cross_dtu(self):
        lines = lines_control.Lines()
        market = client.Market()
        graph = client.Graph()
        buy_lines = lines.read('buy')
        last_two_klines = graph.get_kline(2)['result'].get('list')
        last_kline = float(last_two_klines[1][4])
        actual_price = market.get_actual_coin_price()

        for buy_line in buy_lines.split('\n')[::-1]:
            if last_kline < float(buy_line):
                if actual_price > float(buy_line) and actual_price > last_kline:
                    logger.info('last_knile= %s, buy_line= %s, actual_price= %s', last_kline, buy_line, actual_price)
                    return True
                
if __name__ == '__main__':
    print(Lines().cross_utd())
