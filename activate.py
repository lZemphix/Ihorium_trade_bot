from requests import Session
from datetime import datetime
from bot import bot, config
import traceback
import logging
from requests.adapters import Retry, HTTPAdapter

if __name__ == '__main__':
    session = Session()
    retries = Retry(total=9999)
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    try:
        
        bot.start()
        
    except Exception as e:
        print('err', traceback.format_exc())
        print('bot was stoped!')

        logging.info(traceback.format_exc())
        if config.get('send_notify'):
            bot.notify.warning('Bot was stoped!')
            bot.notify.error(f'Time: {datetime.now()}')

   
        
