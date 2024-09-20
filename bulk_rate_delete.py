import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
import time
from includes.SeleniumHelper import SeleniumHelper
from includes import globals
from includes.logging_config import setup_logging, get_logger
from includes.constants import DEFAULT_TIMEOUT, XPaths

class BulkRateDelete:
    def __init__(self, driver):
        self.driver = driver
        self.selenium_helper = SeleniumHelper(driver)
        self.logger = get_logger(__name__)

    def get_grid_rows(self):
        try:
            container = self.selenium_helper.wait_for_element(By.XPATH, XPaths.BULK_RATE_GRID_CONTAINER, timeout=DEFAULT_TIMEOUT)
            return container.find_elements(By.XPATH, './/div[contains(@class, "GridLiteRow")]')
        except TimeoutException:
            self.logger.error("Timeout waiting for grid rows to load.")
            return []

    def select_first_row(self):
        try:
            rows = self.get_grid_rows()
            if rows:
                first_column = rows[0].find_element(By.XPATH, './/div[contains(@class, "GridLiteColumn")][1]')
                first_column.click()
                self.logger.info("First row selected.")
                time.sleep(1)  # Wait for any potential UI updates
            else:
                self.logger.warning("No rows found to select.")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error selecting first row: {str(e)}")
            return False

    def delete_row(self):
        try:
            if not self.select_first_row():
                return False

            if not self.selenium_helper.wait_and_click(By.XPATH, XPaths.BULK_RATE_DELETE_BUTTON, timeout=DEFAULT_TIMEOUT):
                self.logger.error("Failed to click delete button")
                return False
            
            if not self.selenium_helper.wait_and_click(By.XPATH, XPaths.BULK_RATE_CONFIRM_DELETE, timeout=DEFAULT_TIMEOUT):
                self.logger.error("Failed to confirm deletion")
                return False
            
            self.logger.info("Row deleted successfully.")
            time.sleep(2)  # Wait for the grid to refresh
            return True
        except ElementClickInterceptedException:
            self.logger.warning("Delete button is intercepted. Trying to remove overlays...")
            try:
                self.driver.execute_script("""
                    var elements = document.getElementsByClassName('modal-backdrop');
                    for(var i=0; i<elements.length; i++){
                        elements[i].parentNode.removeChild(elements[i]);
                    }
                """)
                time.sleep(1)
                return self.delete_row()  # Retry deletion
            except Exception as e:
                self.logger.error(f"Error removing overlay: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error deleting row: {str(e)}")
        return False

    def delete_all_rows(self):
        while True:
            rows = self.get_grid_rows()
            if not rows:
                self.logger.info("No more rows to delete. Process complete.")
                break
            
            self.logger.info(f"Rows remaining: {len(rows)}")
            if not self.delete_row():
                self.logger.warning("Failed to delete row. Retrying...")
                time.sleep(2)

def automate_process(username, password):
    logger = get_logger(__name__)
    driver = webdriver.Chrome()
    try:
        driver.maximize_window()
        globals.login_with_2fa_and_wait(driver, username, password)
        
        bulk_delete = BulkRateDelete(driver)
        bulk_delete.delete_all_rows()

        logger.info("Process completed successfully")
        logger.info("Please verify the results.")
        input("Press Enter when you're done verifying...")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
    finally:
        driver.quit()
        logger.info("Script execution completed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RMS Cloud Delete Rows Automation Script")
    parser.add_argument("username", help="Your RMS Cloud username")
    parser.add_argument("password", help="Your RMS Cloud password")
    args = parser.parse_args()

    setup_logging("bulk_rate_delete")
    automate_process(args.username, args.password)