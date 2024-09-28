import logging
import os
from datetime import datetime

def setup_logging(log_name, log_level=logging.INFO):
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Generate a timestamp for the log file name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"logs/{log_name}_{timestamp}.log"

    # Configure the root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Check if the root logger already has handlers
    if not logger.handlers:
        # Create file handler which logs even debug messages
        fh = logging.FileHandler(log_file)
        fh.setLevel(log_level)
        fh_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(fh_formatter)
        logger.addHandler(fh)

        # Create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(log_level)
        ch_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(ch_formatter)
        logger.addHandler(ch)

    # Return a logger with the specified name
    return logging.getLogger(log_name)

def get_logger(name):
    return logging.getLogger(name)
