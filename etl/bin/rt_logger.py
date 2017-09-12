# rt_logger.py
import os
import os.path
import logging
from logging.handlers import RotatingFileHandler

def make_a_logger(app_name):
    #Configure logger
    # create logger with app_name
    logger = logging.getLogger(app_name)
    logger.setLevel(logging.DEBUG)
    # create file handler which logs things like debug messages
    dir = os.path.dirname(__file__)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    # create rotating file handler
    ROTATING_LOG_FILENAME = os.path.join(dir, '..', '..', 'log/r_{}.log'.format(app_name))
    rfh = RotatingFileHandler(ROTATING_LOG_FILENAME,
                              maxBytes=4451,
                              backupCount=6,
                             )
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    rfh.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(ch)
    logger.addHandler(rfh)

    return logger