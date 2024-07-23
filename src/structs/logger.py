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
            'filename': 'log/structs.log',
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


def log_execution_data(res_db):
    """
    if res_db:
        if conn is not None:
            log_execution_data(conn, execution_time, resources_used, dataset_log, args.sp, num_kernels, num_branches, tree_depth, pruned_branches_count, args.filepath, boundary, optimal_hitting_set, args.shrink_div_conq, args.expand_sw_size, args.alpha, args.ss, optimal_value, args.expand_div_conq, args.shrink_sw_size, optimal_cardinality, args.pruner, lowest_card, best_random, best_incon, best_random_card, best_incon_card,min_val_rand,min_val_incon)
            conn.close()
        else:
            print("Connection to MySQL database failed")
    """
    pass