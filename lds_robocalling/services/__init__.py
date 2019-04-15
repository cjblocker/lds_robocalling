
import importlib
from .. import _config
from . import facebook
from . import lds_scraper

def __getattr__(name):
    if name == 'db':
        database = importlib.import_module('.database', __name__)
        return database.Database(_config['database'])
    elif name in ['email', 'phone', 'facebook', 'lds_scraper']:
        return importlib.import_module("." + name, __name__)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

import sys
if float(sys.version[:2]) < 3.7:
    from . import phone
    from . import email
    from . import database
    db = database.Database(_config['database'])