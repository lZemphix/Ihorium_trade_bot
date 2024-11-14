from datetime import datetime
import json
from bot import bot
import traceback
from logging import DEBUG, INFO, getLogger, basicConfig, FileHandler, StreamHandler

DATE_FMT = '%Y-%m-%d %H:%M:%S'
FORMAT = '%(asctime)s : %(module)-10s : %(lineno)-4s : %(levelname)-8s : %(message)s'
logger = getLogger()
file = FileHandler('logs/logs.log', mode='a')
console = StreamHandler()
basicConfig(level=INFO, format=FORMAT, datefmt=DATE_FMT, handlers=[file, console])


if __name__ == '__main__':    
    try:   
        logger.info('trying to start...')
        bot.start()
    except Exception as e:
        print('err', traceback.format_exc())
        logger.info('bot was stopped!')
        with open('config/bot_config.json', 'r') as f:
            config = json.load(f)
            if config.get('send_notify'):
                bot.notify.warning('Bot was stoped!')
                bot.notify.error(f'Time: {datetime.now()}')

   
        
