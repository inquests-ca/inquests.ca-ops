import datetime
import logging


def _init_logger():
    log_debug_file = './logs/{}.txt'.format(datetime.datetime.now().strftime('%Y-%m-%d'))
    log_warning_file = './logs/warnings.txt'

    log_format = "[%(levelname)s] %(message)s"

    debug_handler = logging.FileHandler(log_debug_file, mode='w')
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(logging.Formatter(log_format))

    info_handler = logging.StreamHandler()
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(logging.Formatter(log_format))

    warning_handler = logging.FileHandler(log_warning_file, mode='w')
    warning_handler.setLevel(logging.WARNING)

    migration_logger = logging.getLogger('migration')
    migration_logger.setLevel(logging.DEBUG)
    migration_logger.addHandler(debug_handler)
    migration_logger.addHandler(info_handler)
    migration_logger.addHandler(warning_handler)

    return migration_logger

logger = _init_logger()
