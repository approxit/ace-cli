from configparser import ConfigParser, ExtendedInterpolation
from functools import partial
from pathlib import Path


def load_config():
    """Loads config based on default.ini and ace.ini files.

    Returns:
        ConfigParser: Loaded config.

    """
    config = ConfigParser(interpolation=ExtendedInterpolation())

    config.read([Path(__file__).parent / 'default.ini', 'ace.ini'])

    config['dirs']['cwd'] = str(Path(config['dirs']['cwd']).absolute())

    return config


print_flush = partial(print, flush=True)
