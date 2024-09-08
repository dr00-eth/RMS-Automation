from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import logging

def setup_logging(property):
    # Setup for attributes logger
    attr_logger = logging.getLogger('attributes')
    attr_logger.setLevel(logging.INFO)
    attr_handler = logging.FileHandler(f'attribute_exceptions_{property}.log')
    attr_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    attr_handler.setFormatter(attr_formatter)
    attr_logger.addHandler(attr_handler)

    # Setup for application logger (optional, for other parts of your application)
    app_logger = logging.getLogger('application')
    app_logger.setLevel(logging.WARNING)
    app_handler = logging.FileHandler(f'application_{property}.log')
    app_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    app_handler.setFormatter(app_formatter)
    app_logger.addHandler(app_handler)

    # Prevent loggers from propagating to the root logger
    attr_logger.propagate = False
    app_logger.propagate = False

    return attr_logger, app_logger