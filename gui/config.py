import os
import configparser
import logging

from .common import const


config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
config.read(const.CONFIG_FILE)

REQUEST_TIMEOUT = config.getfloat('server', 'request_timeout', fallback=None)


def get_log_file() -> str:
    log_file = config.get('logging', 'log_file', fallback=const.DEFAULT_LOG_FILE)
    logs_dir = os.path.split(log_file)[0]

    if logs_dir and not os.path.isdir(logs_dir):
        os.makedirs(logs_dir, exist_ok=True)

    return log_file


def logging_basic_config() -> dict:
    from logging import FileHandler
    from logging.handlers import RotatingFileHandler

    handler = None
    rotation = config.getboolean('logging', 'log_rotate', fallback=False)
    file_mode = config.get('logging', 'file_mode', fallback='a')
    max_bytes = config.getint('logging', 'rotation.maxBytes', fallback=1024 * 1024 * 5)
    backup_count = config.getint('logging', 'rotation.backupCount', fallback=3)
    log_file = get_log_file()

    if rotation and log_file:
        handler = RotatingFileHandler(log_file, mode=file_mode, maxBytes=max_bytes, backupCount=backup_count)
    elif log_file:
        handler = FileHandler(log_file, mode=file_mode)

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


def logging_dict_config() -> dict:
    from logging import FileHandler
    from logging.handlers import RotatingFileHandler

    rotation = config.getboolean('logging', 'log_rotate', fallback=False)
    file_mode = config.get('logging', 'file_mode', fallback='a')
    max_bytes = config.getint('logging', 'rotation.maxBytes', fallback=1024 * 1024 * 5)
    backup_count = config.getint('logging', 'rotation.backupCount', fallback=3)
    log_file = get_log_file()

    res = {
        'version': 1,
        'loggers': {
            'root': {
                'level': config.getint('logging', 'level', fallback=logging.INFO),
            }
        },
        'formatters': {
            'generic': {
                'format': config.get('logging', 'format', fallback='[%(asctime)s] %(levelname).1s  ::  %(message)s'),
                'datefmt': config.get('logging', 'datefmt', fallback='%Y.%m.%d %H:%M:%S')
            }
        },
        'handlers': {}
    }

    if rotation and log_file:
        res['loggers']['root']['handlers'] = ['rotate']
        res['handlers']['rotate'] = {
            'class': RotatingFileHandler,
            'formatter': 'generic',
            'filename': log_file,
            'mode': file_mode,
            'maxBytes': max_bytes,
            'backupCount': backup_count
        }
    elif log_file:
        res['loggers']['root']['handlers'] = ['file']
        res['handlers']['file'] = {
            'class': FileHandler,
            'formatter': 'generic',
            'filename': log_file,
            'mode': file_mode
        }
    else:
        res['loggers']['root']['filename'] = None

    return res
