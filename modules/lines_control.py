import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from logging import getLogger
import client.base as base
import json

logger = getLogger(__name__)


class Lines:
    def __init__(self) -> None: 
        self.sell_lines_path = 'src/.sell_lines'
        self.buy_lines_path = 'src/.buy_lines'

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
        
    def write(self, buy_price: float, mode: str = 'both') -> None:
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

    def sell_lines_qty(self) -> int:
        with open(self.sell_lines_path, 'r') as file:
            sell = file.read()
            qty = len(sell.split('\n')) - 1
            return qty if sell != '' else 0

    def buy_lines_qty(self) -> int:
        with open(self.buy_lines_path, 'r') as file:
            buy = file.read()
            qty = len(buy.split('\n')) - 1
            return qty if buy != '' else 0

    def read(self, mode: str = 'both') -> tuple | str:
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
                return buy.read().rstrip()
        else:
            logger.error('Modes: both, sell or buy')
    
    def clear(self, mode: str = 'both') -> None:
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

    def check_uper_line(self) -> int:
        market = base.Market()
        actual_price = market.get_actual_coin_price()
        sell_lines = self.read('sell')
        count = 0
        f_sell_lines = [item for item in sell_lines.split('\n') if item != '']
        for line in f_sell_lines:
            if actual_price > float(line):
                count += 1
        return count
        
    def cross_utd(self) -> bool:
        try:
            market = base.Market()
            graph = base.Graph()
            sell_lines = self.read('sell')
            last_two_klines = graph.get_kline(2)['result'].get('list')
            last_kline = float(last_two_klines[1][4])
            actual_price = market.get_actual_coin_price()
            if actual_price == None:
                logger.warning('cross utd == None')
                return self.cross_utd()

            for sell_line in sell_lines.split('\n')[::-1]:
                if last_kline > float(sell_line):
                    if actual_price < float(sell_line) and actual_price < last_kline:
                        return True
        except Exception as e:
            logger.warning('utd exception %s', e)
            pass  

    def cross_dtu(self) -> bool:
        try:
            market = base.Market()
            graph = base.Graph()
            buy_lines = self.read('buy')
            last_two_klines = graph.get_kline(2)['result'].get('list')
            last_kline = float(last_two_klines[1][4])
            actual_price = market.get_actual_coin_price()
            if actual_price == None:
                logger.warning('actual price None!')
                return self.cross_dtu

            for buy_line in buy_lines.split('\n')[::-1]:
                if last_kline < float(buy_line):
                    if actual_price > float(buy_line) and actual_price > last_kline:
                        return True
        except Exception as e: 
            logger.warning('dtu exepton! %s', e)
            pass
                
if __name__ == '__main__':
    try:
        Lines().write(sys.argv[0])
        print('ok')
    except:
        print('error')
