import os 
import time
import logging
from logging import handlers

from lib import make_parents

def get_logger(filename):
    base, name_ext = os.path.split(filename)
    name, ext = os.path.splitext(name_ext)
    sign = time.strftime('%Y-%m-%d')
    filename = os.path.join(base, f"{name}_{sign}{ext}")

    class WrappedLogger(logging.Logger):
        def __init__(self, name, level=logging.INFO):
            self._error_count = 0
            super(WrappedLogger, self).__init__(name, level)

        @property
        def error_count(self):
            return self._error_count

        def error(self, msg, *args, **kwargs):
            self._error_count += 1
            return super(WrappedLogger, self).error(msg, *args, **kwargs)

    logging.setLoggerClass(WrappedLogger)

    make_parents(filename)

    # log_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s')
    log_formatter = logging.Formatter('[%(levelname)s] %(message)s')

    logger = logging.getLogger("r2d2")

    fileHandler = handlers.TimedRotatingFileHandler(filename, when='D')
    fileHandler.setFormatter(log_formatter)
    logger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(log_formatter)
    logger.addHandler(consoleHandler)

    return logger
