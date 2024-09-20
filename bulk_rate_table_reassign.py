import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webelement import WebElement
import time
from includes.SeleniumHelper import SeleniumHelper
from includes.PropertyManager import PropertyManager
from includes import globals
from includes.logging_config import setup_logging, get_logger
from includes.constants import DEFAULT_TIMEOUT, XPaths

class BulkRateTableReassign:
    def __init__(self, driver):
        self.driver = driver
        self.selenium_helper = SeleniumHelper(driver)
        self.property_manager = PropertyManager(self.selenium_helper)
        self.logger = get_logger(__name__)

    def get_grid_rows(self):
        try:
            container = self.selenium_helper.wait_for_element(
                By.XPATH, XPaths.RATE_TABLE_GRID_CONTAINER, timeout=DEFAULT_TIMEOUT
            )
            return container.find_elements(By.XPATH, './/div[contains(@class, "GridLiteRow")]')
        except TimeoutException:
            self.logger.error("Timeout waiting for grid rows to load.")
            return []

    def is_row_selected(self, row: WebElement):
        try:
            checkbox = row.find_element(By.XPATH, './/div[contains(@class, "GridLiteColumn")][1]//input[@type="checkbox"]')
            return checkbox.is_selected()
        except:
            return False

    def click_first_row_with_retry(self, max_attempts=5, wait_time=10):
        for attempt in range(max_attempts):
            try:
                rows = self.get_grid_rows()
                if not rows:
                    self.logger.warning("No rows found.")
                    return False
                
                first_row = rows[0]
                
                if not self.is_row_selected(first_row):
                    first_row.click()
                    self.logger.info(f"Selected first row (Attempt {attempt + 1})")
                else:
                    self.logger.info(f"First row already selected (Attempt {attempt + 1})")
                
                if self.selenium_helper.wait_and_click(By.XPATH, XPaths.EDIT_BUTTON, timeout=wait_time, max_attempts=10, retry_interval=2.0):
                    self.logger.info(f"Clicked Edit button (Attempt {attempt + 1})")
                    
                    if self.selenium_helper.wait_for_modal_to_be_visible("RateTableSetup", timeout=5):
                        self.logger.info("RateTableSetup modal is visible and interactable")
                        return True
                    else:
                        self.logger.warning(f"RateTableSetup modal is not visible or interactable (Attempt {attempt + 1})")
                else:
                    self.logger.warning(f"Failed to click Edit button (Attempt {attempt + 1})")
            
            except Exception as e:
                self.logger.error(f"Error selecting row and clicking Edit (Attempt {attempt + 1}): {str(e)}")
            
            if attempt < max_attempts - 1:
                self.logger.info("Retrying...")
                time.sleep(2)
        
        self.logger.error("Failed to open RateTableSetup modal after all attempts")
        return False

    def click_properties_button_with_retry(self, max_attempts=3):
        for attempt in range(max_attempts):
            try:
                if self.selenium_helper.wait_and_click(By.XPATH, XPaths.PROPERTIES_BUTTON, timeout=DEFAULT_TIMEOUT):
                    self.logger.info(f"Clicked properties button (Attempt {attempt + 1})")
                    
                    if self.selenium_helper.is_modal_visible("AdvancedPropertySelectionModal"):
                        self.logger.info("AdvancedPropertySelectionModal is immediately visible and interactable")
                        return True
                    
                    if self.selenium_helper.wait_for_modal_to_be_visible("AdvancedPropertySelectionModal", timeout=5):
                        self.logger.info("AdvancedPropertySelectionModal became visible and interactable")
                        return True
                    else:
                        self.logger.warning(f"AdvancedPropertySelectionModal is not visible or interactable (Attempt {attempt + 1})")
                else:
                    self.logger.warning(f"Failed to click properties button (Attempt {attempt + 1})")
            except Exception as e:
                self.logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
            
            if attempt < max_attempts - 1:
                time.sleep(1)
        
        self.logger.error("Failed to open AdvancedPropertySelectionModal after all attempts")
        return False

    def check_and_dismiss_error_modal(self, timeout=5):
        try:
            if self.selenium_helper.is_modal_visible("ResStatusWarnings"):
                self.logger.warning("Server error modal detected.")
                
                if self.selenium_helper.wait_and_click(By.XPATH, XPaths.ERROR_MODAL_OK_BUTTON, timeout=timeout):
                    self.logger.info("Dismissed server error modal.")
                    return True
                else:
                    self.logger.warning("Failed to dismiss server error modal.")
                    return False
            else:
                return False
        except Exception as e:
            self.logger.error(f"Error handling server error modal: {str(e)}")
            return False

    def update_all_rows(self, property_to_select: str, property_to_remove: str, max_retries=3):
        retry_count = 0
        while retry_count < max_retries:
            try:
                if self.check_and_dismiss_error_modal():
                    self.logger.info("Dismissed error modal, retrying from the beginning.")
                    retry_count += 1
                    continue

                if not self.click_first_row_with_retry():
                    self.logger.warning("Failed to select and edit a row. Retrying from the beginning.")
                    retry_count += 1
                    continue

                if self.check_and_dismiss_error_modal():
                    self.logger.info("Dismissed error modal after row selection, retrying from the beginning.")
                    retry_count += 1
                    continue

                if not self.click_properties_button_with_retry():
                    self.logger.warning("Failed to open AdvancedPropertySelectionModal. Retrying from the beginning.")
                    retry_count += 1
                    continue

                available_xpath = XPaths.AVAILABLE_PROPERTIES
                selected_xpath = XPaths.SELECTED_PROPERTIES

                self.property_manager.select_property(property_to_select, available_xpath, selected_xpath)
                self.property_manager.remove_property(property_to_remove, selected_xpath)

                if not self.selenium_helper.wait_and_click(By.XPATH, XPaths.CLOSE_PROPERTIES_MODAL, timeout=DEFAULT_TIMEOUT):
                    self.logger.warning("Failed to close properties modal.")
                    retry_count += 1
                    continue

                if not self.selenium_helper.wait_and_click(By.XPATH, XPaths.SAVE_CHANGES, timeout=DEFAULT_TIMEOUT):
                    self.logger.warning("Failed to save changes and exit to main window.")
                    retry_count += 1
                    continue

                time.sleep(1)

                if self.check_and_dismiss_error_modal():
                    self.logger.info("Dismissed error modal after saving, retrying from the beginning.")
                    retry_count += 1
                    continue

                self.logger.info("Successfully processed a row.")
                retry_count = 0  # Reset the retry count on success

            except Exception as e:
                self.logger.error(f"An error occurred while processing a row: {str(e)}")
                retry_count += 1
                self.logger.info(f"Retrying from the beginning. Attempt {retry_count} of {max_retries}")

            time.sleep(1)

        if retry_count >= max_retries:
            self.logger.error(f"Maximum retries ({max_retries}) reached. Exiting the process.")

def automate_process(username, password, property_to_select, property_to_remove, debug):
    logger = get_logger(__name__)
    driver = None
    try:
        driver = webdriver.Chrome()
        driver.maximize_window()

        if debug:
            globals.login_training_with_2fa_and_wait(driver, username, password)
        else:
            globals.login_with_2fa_and_wait(driver, username, password)
        
        bulk_reassign = BulkRateTableReassign(driver)
        bulk_reassign.update_all_rows(property_to_select, property_to_remove, max_retries=10)

        logger.info("Process completed successfully")
        logger.info("Please verify the results.")
        input("Press Enter when you're done verifying...")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
    finally:
        if driver:
            driver.quit()
        logger.info("Script execution completed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RMS Cloud Bulk Rate Table Reassign Automation Script")
    parser.add_argument("username", help="Your RMS Cloud username")
    parser.add_argument("password", help="Your RMS Cloud password")
    parser.add_argument("property_to_select", help="Property to select")
    parser.add_argument("property_to_remove", help="Property to remove")
    parser.add_argument("--debug", action="store_true", help="Runs in training")
    args = parser.parse_args()

    setup_logging("bulk_rate_table_reassign")
    automate_process(args.username, args.password, args.property_to_select, args.property_to_remove, args.debug)