from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
import time
from includes.logging_config import setup_logging
from includes.constants import DEFAULT_TIMEOUT, XPaths
from includes.BaseAutomation import BaseAutomation
from includes.argument_parser_utility import create_base_parser

class BulkRateDelete(BaseAutomation):
    def __init__(self, username: str, password: str, debug: bool = False):
        super().__init__(username, password, debug)

    def perform_automation(self):
        self.delete_all_rows()

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

def main():
    parser = create_base_parser("RMS Cloud Delete Rows Automation Script")
    args = parser.parse_args()

    setup_logging("bulk_rate_delete")

    bulk_delete = BulkRateDelete(args.username, args.password, args.debug)
    bulk_delete.run()

if __name__ == "__main__":
    main()