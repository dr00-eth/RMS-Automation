import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
import traceback
import time
from includes.SeleniumHelper import SeleniumHelper
from includes.AttributeManager import AttributeManager
from includes.SiteProcessor import SiteProcessor
from includes import globals
from includes.logging_config import setup_logging, get_logger
from includes.constants import DEFAULT_TIMEOUT, CATEGORY_URL, XPaths

def automate_process(username: str, password: str, property_name: str, start_number: int = 1, debug: bool = False):
    logger = get_logger(__name__)
    driver = None
    try:
        driver = webdriver.Chrome()
        driver.maximize_window()
        selenium_helper = SeleniumHelper(driver)
        attribute_manager = AttributeManager(selenium_helper)
        site_processor = SiteProcessor(selenium_helper, attribute_manager, None)  # Passing None for tax_manager as it's not used here

        if debug:
            globals.login_training_with_2fa_and_wait(driver, username, password)
        else:
            globals.login_with_2fa_and_wait(driver, username, password)

        selenium_helper.driver.get(CATEGORY_URL)
        logger.info("Navigated to Setup/Category page")

        selenium_helper.wait_for_element(By.XPATH, XPaths.MAIN_WINDOW, timeout=DEFAULT_TIMEOUT)
        logger.info("Main window loaded")

        globals.wait_for_dropdown_and_select(driver, property_name)
        time.sleep(2)
        current_number = start_number - 1
        container_xpath = XPaths.CONTAINER

        while True:
            next_row, next_number, _ = site_processor.find_next_site(current_number, container_xpath)
            if not next_row:
                logger.info(f"No more sites found after number {current_number}. Ending process.")
                break

            site_processor.process_site_attrs(next_row, next_number, attributes_to_add, attributes_to_remove)
            current_number = next_number

        logger.info("Process completed successfully")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        logger.error("Traceback:")
        logger.error(traceback.format_exc())
    finally:
        if driver:
            driver.quit()
        logger.info("Script execution completed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RMS Cloud Automation Script")
    parser.add_argument("username", help="Your RMS Cloud username")
    parser.add_argument("password", help="Your RMS Cloud password")
    parser.add_argument("property", help="The property to automate, must match dropdown exactly")
    parser.add_argument("--start", type=int, default=1, help="Starting site number (default: 1)")
    parser.add_argument("--debug", action="store_true", help="Runs in training")
    args = parser.parse_args()

    attributes_to_add = [
        "Pet Friendly",
        # Add other attributes as needed
    ]

    attributes_to_remove = [
        # Add attributes to remove as needed
    ]

    setup_logging(f"attributes_processor_{args.property}")
    automate_process(args.username, args.password, args.property, args.start, args.debug)