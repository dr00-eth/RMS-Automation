from selenium.webdriver.common.by import By
import time
from includes.AttributeManager import AttributeManager
from includes.SiteProcessor import SiteProcessor
from includes import globals
from includes.logging_config import setup_logging
from includes.constants import DEFAULT_TIMEOUT, CATEGORY_URL, XPaths
from includes.BaseAutomation import BaseAutomation
from includes.argument_parser_utility import create_base_parser, add_property_arguments

class AttributesProcessor(BaseAutomation):
    def __init__(self, username: str, password: str, property_name: str, start_number: int = 1, debug: bool = False):
        super().__init__(username, password, debug)
        self.property_name = property_name
        self.start_number = start_number
        self.attribute_manager = None
        self.site_processor = None

    def setup(self):
        super().setup()
        self.attribute_manager = AttributeManager(self.selenium_helper)
        self.site_processor = SiteProcessor(self.selenium_helper, self.attribute_manager, None)

    def perform_automation(self):
        self.navigate_to_page(CATEGORY_URL)
        self.selenium_helper.wait_for_element(By.XPATH, XPaths.MAIN_WINDOW, timeout=DEFAULT_TIMEOUT)
        self.logger.info("Main window loaded")

        globals.wait_for_dropdown_and_select(self.driver, self.property_name)
        time.sleep(2)
        current_number = self.start_number - 1
        container_xpath = XPaths.CONTAINER

        while True:
            next_row, next_number, _ = self.site_processor.find_next_site(current_number, container_xpath)
            if not next_row:
                self.logger.info(f"No more sites found after number {current_number}. Ending process.")
                break

            self.site_processor.process_site_attrs(next_row, next_number, attributes_to_add, attributes_to_remove)
            current_number = next_number

def main():
    parser = create_base_parser("RMS Cloud Attributes Processor Automation Script")
    parser = add_property_arguments(parser)
    args = parser.parse_args()

    setup_logging(f"attributes_processor_{args.property}")

    processor = AttributesProcessor(args.username, args.password, args.property, args.start, args.debug)
    processor.run()

if __name__ == "__main__":
    attributes_to_add = [
        "Pet Friendly",
        # Add other attributes as needed
    ]

    attributes_to_remove = [
        # Add attributes to remove as needed
    ]

    main()