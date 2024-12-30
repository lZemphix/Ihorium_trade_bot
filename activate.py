from config import logger_config as l
from datetime import datetime
from logging import getLogger
from client.bot import bot
import traceback
import json

logger = getLogger('root')

def main() -> None:
    try:   
        logger.info('trying to start...')
        bot.start()
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.info('bot was stopped! Error: %s', e)
        with open('config/bot_config.json', 'r') as f:
            config = json.load(f)
            if config.get('send_notify'):
                bot.notify.error(f'Bot was stopped! Time: {datetime.now()}')

if __name__ == '__main__':    
    main()

   
        
