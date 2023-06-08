import io
import os
import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

from config.config import logs_dir

# Logging Definitions
log_lvl = logging.DEBUG
console_log_lvl = logging.INFO
logger = logging.getLogger('fastapi')
logger.setLevel(log_lvl)
log_file = os.path.join(logs_dir, f'logs_bt_{datetime.now().strftime("%Y%m%d")}.log')
handler = TimedRotatingFileHandler(log_file, when='D', delay=True)
handler.setLevel(log_lvl)
console = logging.StreamHandler(stream=sys.stdout)
console.setLevel(console_log_lvl)
# formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')  #NOSONAR
# formatter = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(funcName)s %(message)s')
formatter = logging.Formatter('%(asctime)s %(levelname)s <%(funcName)s> %(message)s')
handler.setFormatter(formatter)
console.setFormatter(formatter)
logger.addHandler(handler)
logger.addHandler(console)

debug_logger = logging.getLogger('debugger')
debug_logger.setLevel(logging.DEBUG)
debug_handler = logging.FileHandler(os.path.join(logs_dir, f'debug_{datetime.now().strftime("%Y%m%d")}.log'), delay=True)
debug_handler.setLevel(logging.DEBUG)
debug_handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
debug_logger.addHandler(debug_handler)
