import sys
import logging
from functools import wraps

def export(fn):
    # https://stackoverflow.com/a/35710527
    mod = sys.modules[fn.__module__]
    if hasattr(mod, '__all__'):
        if fn.__name__ not in mod.__all__:
            mod.__all__.append(fn.__name__)
    else:
        mod.__all__ = [fn.__name__]
    return fn

def initialize_logger():
    # create logger with 'spam_application'
    logger = logging.getLogger('hollyg')
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler('hollg.log')
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    logger.debug("""
    **************************************************************************
    ********************** Initializing Logger *******************************
    **************************************************************************
    """)


def log_call(logger):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info("Entering {}".format(func.__name__))            
            return func(*args, **kwargs)
        return wrapper
    return decorator