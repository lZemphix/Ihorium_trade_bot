from datetime import datetime
import json
from bot import bot
import traceback
from logging import getLogger
from modules import logger as l

logger = getLogger('root')

def main() -> None:
    try:   
        logger.info('trying to start...')
        bot.start()
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.info('bot was stopped!')
        with open('config/bot_config.json', 'r') as f:
            config = json.load(f)
            if config.get('send_notify'):
                bot.notify.warning('Bot was stoped!')
                bot.notify.error(f'Time: {datetime.now()}')

if __name__ == '__main__':    
    main()

   
        
