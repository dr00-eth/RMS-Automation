from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from typing import List, Dict, Union
from includes.BaseManager import BaseManager
from includes.SeleniumHelper import SeleniumHelper
from includes.constants import DEFAULT_TIMEOUT, XPaths

class PropertyManager(BaseManager):
    def __init__(self, selenium_helper: SeleniumHelper):
        super().__init__(selenium_helper)

    def select_property(self, property_name: str, available_xpath: str, selected_xpath: str) -> bool:
        property_xpath = f"{available_xpath}//div[contains(@class, 'GridLiteCell_PropertyName') and normalize-space(text())='{property_name}']"
        if not self.selenium_helper.wait_and_click(By.XPATH, property_xpath, timeout=DEFAULT_TIMEOUT):
            self.logger.warning(f"Failed to click on property: {property_name}")
            return False

        if not self.selenium_helper.wait_and_click(By.XPATH, XPaths.PROPERTY_ADD_BUTTON, timeout=DEFAULT_TIMEOUT):
            self.logger.warning("Failed to click Add button")
            return False

        selected_property_xpath = f"{selected_xpath}//div[contains(@class, 'GridLiteCell_PropertyName') and normalize-space(text())='{property_name}']"
        if self.selenium_helper.wait_for_visibility(By.XPATH, selected_property_xpath, timeout=DEFAULT_TIMEOUT):
            self.logger.info(f"Successfully selected property: {property_name}")
            return True
        else:
            self.logger.warning(f"Property {property_name} did not appear in the selected list")
            return False

    def remove_property(self, property_name: str, selected_xpath: str) -> bool:
        property_xpath = f"{selected_xpath}//div[contains(@class, 'GridLiteCell_PropertyName') and normalize-space(text())='{property_name}']"
        if not self.selenium_helper.wait_and_click(By.XPATH, property_xpath, timeout=DEFAULT_TIMEOUT):
            self.logger.warning(f"Failed to click on property to remove: {property_name}")
            return False

        if not self.selenium_helper.wait_and_click(By.XPATH, XPaths.PROPERTY_REMOVE_BUTTON, timeout=DEFAULT_TIMEOUT):
            self.logger.warning("Failed to click Remove button")
            return False

        try:
            self.selenium_helper.wait_for_invisibility(By.XPATH, property_xpath, timeout=DEFAULT_TIMEOUT)
            self.logger.info(f"Successfully removed property: {property_name}")
            return True
        except TimeoutException:
            self.logger.warning(f"Property {property_name} did not disappear from the selected list")
            return False

    def get_selected_properties(self, base_xpath: str) -> List[str]:
        return self.get_selected_items(base_xpath)

    def process_properties(self, properties_to_add: List[Union[str, Dict[str, Union[str, List[str]]]]], 
                           properties_to_remove: List[Union[str, Dict[str, Union[str, List[str]]]]], 
                           available_xpath: str, selected_xpath: str, context: str = "") -> None:
        for property_info in properties_to_add:
            if isinstance(property_info, str):
                property_name = property_info
            else:
                property_name = property_info['property']
            
            if self.should_apply_item(property_info, context):
                self.logger.info(f"Attempting to add property: '{property_name}'")
                self.select_property(property_name, available_xpath, selected_xpath)
            else:
                self.logger.info(f"Skipped adding property: '{property_name}' for context: '{context}'")

        for property_info in properties_to_remove:
            if isinstance(property_info, str):
                property_name = property_info
            else:
                property_name = property_info['property']
            
            if self.should_apply_item(property_info, context):
                self.logger.info(f"Attempting to remove property: '{property_name}'")
                self.remove_property(property_name, selected_xpath)
            else:
                self.logger.info(f"Skipped removing property: '{property_name}' for context: '{context}'")