import datetime
import logging


def _init_logger():
    log_debug_file = './logs/{}.txt'.format(datetime.datetime.now().strftime('%Y-%m-%d'))
    log_warning_file = './logs/{}-warnings.txt'.format(datetime.datetime.now().strftime('%Y-%m-%d'))

    log_format = "[%(levelname)s] %(message)s"

    debug_file_handler = logging.FileHandler(log_debug_file, mode='w')
    debug_file_handler.setLevel(logging.DEBUG)
    debug_file_handler.setFormatter(logging.Formatter(log_format))

    debug_stream_handler = logging.StreamHandler()
    debug_stream_handler.setLevel(logging.DEBUG)
    debug_stream_handler.setFormatter(logging.Formatter(log_format))

    warning_file_handler = logging.FileHandler(log_warning_file, mode='w')
    warning_file_handler.setLevel(logging.WARNING)

    migration_logger = logging.getLogger('migration')
    migration_logger.setLevel(logging.DEBUG)
    migration_logger.addHandler(debug_file_handler)
    migration_logger.addHandler(debug_stream_handler)
    migration_logger.addHandler(warning_file_handler)

    return migration_logger

logger = _init_logger()
