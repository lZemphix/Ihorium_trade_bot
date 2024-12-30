from logging import getLogger
from dotenv import load_dotenv
from client.account import Account
from client.graph import Graph
from client.market import Market
from modules.laps_config import LapsEdit
from modules.lines_control import Lines
from modules.orders_config import OrdersEdit
from modules.telenotify import SendNotify
import json

load_dotenv()

logger = getLogger(__name__)

class Base:
    def __init__(self) -> None:

        bot_config = self.get_config()

        self.symbol: str = bot_config.get('symbol')
        self.coin_name = self.symbol[:-4]
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