from selenium.webdriver.common.by import By
import time
from includes.AttributeManager import AttributeManager
from includes.SiteProcessor import SiteProcessor
from includes.TaxManager import TaxManager
from includes import globals
from includes.logging_config import setup_logging
from includes.constants import DEFAULT_TIMEOUT, CATEGORY_URL, XPaths
from includes.BaseAutomation import BaseAutomation
from includes.argument_parser_utility import create_base_parser, add_property_arguments

class TaxProcessor(BaseAutomation):
    def __init__(self, username: str, password: str, property_name: str, start_number: int = 1, debug: bool = False):
        super().__init__(username, password, debug)
        self.property_name = property_name
        self.start_number = start_number
        self.attribute_manager = None
        self.tax_manager = None
        self.site_processor = None

    def setup(self):
        super().setup()
        self.attribute_manager = AttributeManager(self.selenium_helper)
        self.tax_manager = TaxManager(self.selenium_helper)
        self.site_processor = SiteProcessor(self.selenium_helper, self.attribute_manager, self.tax_manager)

    def perform_automation(self):
        self.navigate_to_page(CATEGORY_URL)
        self.logger.info("Navigated to Setup/Category page")

        self.selenium_helper.wait_for_element(By.XPATH, XPaths.MAIN_WINDOW, timeout=DEFAULT_TIMEOUT)
        self.logger.info("Main window loaded")

        globals.wait_for_dropdown_and_select(self.driver, self.property_name)
        time.sleep(2)
        current_number = self.start_number - 1
        container_xpath = XPaths.CONTAINER

        while True:
            next_row, next_number, site_name = self.site_processor.find_next_site(current_number, container_xpath)
            if not next_row:
                self.logger.info(f"No more sites found after number {current_number}. Ending process.")
                break

            self.site_processor.process_site_taxes(next_row, next_number, site_name, taxes_to_add, taxes_to_remove)
            current_number = next_number

def main():
    parser = create_base_parser("RMS Cloud Tax Processor Automation Script")
    parser = add_property_arguments(parser)
    args = parser.parse_args()

    setup_logging(f"tax_processor_{args.property}")

    processor = TaxProcessor(args.username, args.password, args.property, args.start, args.debug)
    processor.run()

if __name__ == "__main__":
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

    main()