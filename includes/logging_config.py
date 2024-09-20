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

    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename=log_file,
        filemode='w'
    )

    # Create console handler
    console = logging.StreamHandler()
    console.setLevel(log_level)
    formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)

    # Add console handler to the root logger
    logging.getLogger('').addHandler(console)

    return logging.getLogger(log_name)

def get_logger(name):
    return logging.getLogger(name)