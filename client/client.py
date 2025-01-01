import json
from logging import ERROR, WARNING, getLogger
import os
from dotenv import load_dotenv
from pybit.unified_trading import HTTP

load_dotenv()

logger = getLogger(__name__)

class Client:
    def __init__(self) -> None:
        with open('config/bot_config.json', 'r') as f:
            config = json.load(f)

        self.API_KEY = os.getenv("API_KEY")
        self.API_KEY_SECRET = os.getenv("API_KEY_SECRET")
        self.accountType = os.getenv("ACCOUNT_TYPE")
        self.symbol = config.get('symbol')
        self.amount_buy = config.get('amountBuy')
        self.interval = config.get('interval')
        self.client = HTTP(testnet=False, api_key=self.API_KEY, api_secret=self.API_KEY_SECRET, logging_level=30)
        # print(self.client)
