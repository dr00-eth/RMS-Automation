from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement
import time
import re
from includes.logging_config import setup_logging
from includes.constants import DEFAULT_TIMEOUT, RMS_CATEGORY_URL, RMS_XPaths
from includes.BaseAutomation import BaseAutomation
from includes.argument_parser_utility import create_base_parser

class SiteOrderManager(BaseAutomation):
    def __init__(self, username: str, password: str, debug: bool = False):
        super().__init__(username, password, debug)

    def perform_automation(self):
        self.navigate_to_page(RMS_CATEGORY_URL)
        self.logger.info("Navigated to Setup/Category page")

        self.selenium_helper.wait_for_element(By.XPATH, RMS_XPaths.MAIN_WINDOW, timeout=DEFAULT_TIMEOUT)
        self.logger.info("Main window loaded")

        self.open_display_order_panel()
        if self.order_sites():
            self.logger.info("Sites ordered successfully")
        else:
            self.logger.error("Failed to order sites")

    def open_display_order_panel(self):
        if self.selenium_helper.wait_and_click(By.XPATH, RMS_XPaths.DISPLAY_ORDER_BUTTON, timeout=DEFAULT_TIMEOUT):
            self.logger.info("Display Order panel opened")
            time.sleep(2)  # Short wait for panel to load
        else:
            self.logger.error("Failed to open Display Order panel")

    def get_site_rows(self):
        container = self.selenium_helper.wait_for_element(By.XPATH, RMS_XPaths.CATEGORY_DISPLAY_ORDER, timeout=DEFAULT_TIMEOUT)
        if container:
            return container.find_elements(By.XPATH, './/div[contains(@class, "GridLiteRow")]')
        else:
            self.logger.error("Failed to find site rows container")
            return []

    def get_site_number(self, row: WebElement):
        try:
            cell_content = row.find_element(By.XPATH, './/div[contains(@class, "GridLiteCellContents")]').text
            match = re.search(r'\d+', cell_content)
            return int(match.group()) if match else None
        except Exception as e:
            self.logger.error(f"Error extracting site number: {str(e)}")
            return None

    def move_row_to_position(self, row, current_position, target_position):
        ActionChains(self.driver).move_to_element(row).click().perform()
        
        moves = abs(target_position - current_position)
        direction = "up" if target_position < current_position else "down"
        button_xpath = RMS_XPaths.MOVE_UP_BUTTON if direction == "up" else RMS_XPaths.MOVE_DOWN_BUTTON
        
        for i in range(moves):
            if not self.selenium_helper.wait_and_click(By.XPATH, button_xpath, timeout=DEFAULT_TIMEOUT):
                self.logger.error(f"Failed to click {direction} button")
                return False
        
        self.logger.info(f"Moved site from position {current_position} to {target_position}")
        return True

    def order_sites(self):
        while True:
            rows = self.get_site_rows()
            current_order = [self.get_site_number(row) for row in rows]
            self.logger.info(f"Current order: {current_order}")
            
            numbered_sites = [(num, i) for i, num in enumerate(current_order) if num is not None]
            sorted_sites = sorted(numbered_sites, key=lambda x: x[0])
            
            if [site[0] for site in numbered_sites] == [site[0] for site in sorted_sites]:
                self.logger.info("Sites are in correct order.")
                break
            
            for target_position, (site_number, current_position) in enumerate(sorted_sites):
                if current_position != target_position:
                    positions_to_move = current_position - target_position
                    direction = "up" if positions_to_move > 0 else "down"
                    
                    self.logger.info(f"Moving site {site_number} from position {current_position} to {target_position} ({direction} {abs(positions_to_move)} positions)")
                    
                    if not self.move_row_to_position(rows[current_position], current_position, target_position):
                        self.logger.error(f"Failed to move site {site_number}")
                        return False
                    break  # Only move one site per iteration
            
            time.sleep(0.5)  # Short wait before next iteration
        
        return True

def main():
    parser = create_base_parser("RMS Cloud Display Order Automation Script")
    args = parser.parse_args()

    setup_logging("site_order_by_numeric")

    site_order_manager = SiteOrderManager(args.username, args.password, args.debug)
    site_order_manager.run()

if __name__ == "__main__":
    main()