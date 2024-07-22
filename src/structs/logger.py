import logging
import logging.config

# Define the logging configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s %(levelname)s %(message)s',
        },
    },
    'handlers': {
        'file_search': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'log/search.log',
            'mode': 'w',  # Overwrite the log file each time
            'formatter': 'default',
        },
        'file_tree': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'log/tree.log',
            'mode': 'w',  # Overwrite the log file each time
            'formatter': 'default',
        },
        'file_kernels': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'log/kernels.log',
            'mode': 'w',  # Overwrite the log file each time
            'formatter': 'default',
        },
        'file_main': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'log/main.log',
            'mode': 'w',  # Overwrite the log file each time
            'formatter': 'default',
        },
        'file_structs': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'log/dataset.log',
            'mode': 'w',  # Overwrite the log file each time
            'formatter': 'default',
        },
        'file_pruner': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'log/pruner.log',
            'mode': 'w',  # Overwrite the log file each time
            'formatter': 'default',
        },
    },
    'loggers': {
        'src.search': {
            'handlers': ['file_search'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'src.tree': {
            'handlers': ['file_tree'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'src.kernels': {
            'handlers': ['file_kernels'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'main': {
            'handlers': ['file_main'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'src.structs': {
            'handlers': ['file_structs'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'src.pruner': {
            'handlers': ['file_pruner'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

def setup_logging(disable_logging=False):
    if disable_logging:
        logging.disable(logging.CRITICAL)
    else:
        logging.config.dictConfig(LOGGING_CONFIG)
