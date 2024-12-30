import pandas as pd
from client.client import Client

class Graph(Client):

    def __init__(self) -> None:
            super().__init__()

    def get_kline(self, limit: int = 200) -> dict:
        try:
            kline = self.client.get_kline(symbol=self.symbol, interval=self.interval, limit=limit, category='spot')
            return kline
        except:
            return 200

    def get_kline_dataframe(self) -> pd.DataFrame:
        try:
            dataframe = pd.DataFrame(self.get_kline()['result']['list'])
            dataframe.columns = ['time', 'open', 'high', 'low', 'close', 'volume', 'turnover']
            dataframe.set_index('time', inplace=True)
            dataframe.index = pd.to_numeric(dataframe.index, downcast='integer').astype('datetime64[ms]')    
            dataframe = dataframe[::-1]
            dataframe['close'] = pd.to_numeric(dataframe['close'])
            return dataframe
        except:
            return 200
