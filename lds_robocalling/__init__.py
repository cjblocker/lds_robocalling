import toml
import os

_config = toml.load(os.path.expanduser('~/.hollyg.toml'))

from . import utils
utils.initialize_logger()