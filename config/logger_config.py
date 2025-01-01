from logging import DEBUG, INFO, WARNING, FileHandler, StreamHandler, basicConfig, getLogger
import logging

DATE_FMT = '%Y-%m-%d %H:%M:%S'
FORMAT = '%(asctime)s : %(module)-10s : %(lineno)-4s : %(levelname)-8s : %(message)s'
logger = getLogger(__name__)
file = FileHandler('logs.log', mode='a')
console = StreamHandler()
basicConfig(level=DEBUG, format=FORMAT, datefmt=DATE_FMT, handlers=[file, console])
logging.getLogger('urllib3').setLevel(WARNING)
logging.getLogger('requests').setLevel(WARNING)