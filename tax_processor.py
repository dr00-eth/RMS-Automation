import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
import traceback
import logging
import time
from includes.SeleniumHelper import SeleniumHelper
from includes.AttributeManager import AttributeManager
from includes.SiteProcessor import SiteProcessor
from includes.TaxManager import TaxManager
from includes import globals, helpers

def automate_process(username: str, password: str, property_name: str, attr_logger: logging.Logger, start_number: int = 1):
    driver = None
    try:
        driver = webdriver.Chrome()
        driver.maximize_window()
        selenium_helper = SeleniumHelper(driver)
        attribute_manager = AttributeManager(selenium_helper)
        tax_manager = TaxManager(selenium_helper)
        site_processor = SiteProcessor(selenium_helper, attribute_manager, tax_manager, attr_logger)

        globals.login_with_2fa_and_wait(driver, username, password)

        selenium_helper.driver.get("https://app13.rmscloud.com/#!/Setup/Category")
        print("Navigated to Setup/Category page")

        selenium_helper.wait_for_element(By.XPATH, '//*[@id="MainWindow"]/div/div[2]/div/div/div[2]')
        print("Main window loaded")

        globals.wait_for_dropdown_and_select(driver, property_name)
        time.sleep(2)
        current_number = start_number - 1
        container_xpath = '//*[@id="MainWindow"]/div/div[2]/div/div/div[2]/div'

        while True:
            next_row, next_number, site_name = site_processor.find_next_site(current_number, container_xpath)
            if not next_row:
                print(f"No more sites found after number {current_number}. Ending process.")
                break

            site_processor.process_site_taxes(next_row, next_number, site_name, taxes_to_add, taxes_to_remove)
            current_number = next_number

        print("Process completed successfully")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("Traceback:")
        print(traceback.format_exc())
    finally:
        if driver:
            driver.quit()
        print("Script execution completed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RMS Cloud Automation Script")
    parser.add_argument("username", help="Your RMS Cloud username")
    parser.add_argument("password", help="Your RMS Cloud password")
    parser.add_argument("property", help="The property to automate, must match dropdown exactly")
    parser.add_argument("--start", type=int, default=1, help="Starting site number (default: 1)")
    args = parser.parse_args()

    taxes_to_add = [
        "Sales Tax - 8.25%",  # Applies to all sites
        {"tax": "Resort Fee - Vessel Home - 129.00", "include": ["Vessel"]},
        {"tax": "Resort Fee - RV - 29.00", "exclude": ["Vessel"]},
        # Add other taxes as needed
    ]

    taxes_to_remove = [
        "Occupancy Tax - 13%",
        {"tax": "Resort Fee - Vessel Home - 129.00", "exclude": ["Vessel"]},
        {"tax": "Resort Fee - RV - 29.00", "include": ["Vessel"]},
    ]

    attr_logger, _ = helpers.setup_logging(args.property)
    automate_process(args.username, args.password, args.property, attr_logger, args.start)