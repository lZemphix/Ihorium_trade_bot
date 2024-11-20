from logging import DEBUG, INFO, FileHandler, StreamHandler, basicConfig, getLogger

DATE_FMT = '%Y-%m-%d %H:%M:%S'
FORMAT = '%(asctime)s : %(module)-10s : %(lineno)-4s : %(levelname)-8s : %(message)s'
logger = getLogger(__name__)
file = FileHandler('logs/logs.log', mode='a')
console = StreamHandler()
basicConfig(level=INFO, format=FORMAT, datefmt=DATE_FMT, handlers=[file, console])