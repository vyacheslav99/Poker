import os
import configparser
import logging

from .common import const


config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
config.read(const.CONFIG_FILE)

REQUEST_TIMEOUT = config.getfloat('server', 'request_timeout', fallback=None)

LOGS_DIR = config.get('logging', 'logs_dir', fallback=const.LOGS_DIR)
LOG_FILE = config.get('logging', 'log_file', fallback=const.LOG_FILE)

if LOGS_DIR and not os.path.isdir(LOGS_DIR):
    os.makedirs(LOGS_DIR, exist_ok=True)


def logging_config() -> dict:
    from logging import FileHandler
    from logging.handlers import RotatingFileHandler

    handler = None
    rotation = config.getboolean('logging', 'log_rotate', fallback=False)
    file_mode = config.get('logging', 'file_mode', fallback='a')
    max_bytes = config.getint('logging', 'rotation.maxBytes', fallback=1024 * 1024 * 5)
    backup_count = config.getint('logging', 'rotation.backupCount', fallback=3)

    if rotation:
        handler = RotatingFileHandler(LOG_FILE, mode=file_mode, maxBytes=max_bytes, backupCount=backup_count)
    elif LOG_FILE:
        handler = FileHandler(LOG_FILE, mode=file_mode)

    res = {
        'level': config.getint('logging', 'level', fallback=logging.INFO),
        'format': config.get('logging', 'format', fallback='[%(asctime)s] %(levelname).1s  ::  %(message)s'),
        'datefmt': config.get('logging', 'datefmt', fallback='%Y.%m.%d %H:%M:%S'),
    }

    if handler:
        res['handlers'] = [handler]
    else:
        res['filename'] = None

    return res
