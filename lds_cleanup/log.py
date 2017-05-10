import logging
from functools import wraps

# create logger with 'spam_application'
logger = logging.getLogger('lds_cleanup')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('log.log')
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