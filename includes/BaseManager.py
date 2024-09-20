from selenium.webdriver.common.by import By
from typing import List, Dict, Union
from includes.SeleniumHelper import SeleniumHelper
from includes.logging_config import get_logger

class BaseManager:
    def __init__(self, selenium_helper: SeleniumHelper):
        self.selenium_helper = selenium_helper
        self.logger = get_logger(self.__class__.__name__)

    def select_item(self, item: str, base_xpath: str) -> None:
        item_xpath = f"{base_xpath}//div[contains(@class, 'GridLiteCell') and normalize-space(text())='{item}']"
        success = self.selenium_helper.wait_and_click(By.XPATH, item_xpath, double_click=True, timeout=1, max_attempts=3)
        if success:
            self.logger.info(f"Added item: {item}")
        else:
            self.logger.warning(f"Failed to add item: {item}")

    def remove_item(self, item: str, base_xpath: str) -> None:
        item_xpath = f"{base_xpath}//div[contains(@class, 'GridLiteCell') and normalize-space(text())='{item}']"
        success = self.selenium_helper.wait_and_click(By.XPATH, item_xpath, double_click=True, timeout=1, max_attempts=3)
        if success:
            self.logger.info(f"Removed item: {item}")
        else:
            self.logger.warning(f"Failed to remove item: {item}")

    def get_selected_items(self, base_xpath: str) -> List[str]:
        elements = self.selenium_helper.driver.find_elements(By.XPATH, f"{base_xpath}//div[contains(@class, 'GridLiteCell')]")
        return [element.text.strip() for element in elements]

    def process_items(self, items_to_add: List[Union[str, Dict[str, Union[str, List[str]]]]], 
                      items_to_remove: List[Union[str, Dict[str, Union[str, List[str]]]]], 
                      add_base_xpath: str, remove_base_xpath: str, context: str = "") -> None:
        for item_info in items_to_add:
            if isinstance(item_info, str):
                self.select_item(item_info, add_base_xpath)
            elif self.should_apply_item(item_info, context):
                self.select_item(item_info['item'], add_base_xpath)
        
        for item_info in items_to_remove:
            if isinstance(item_info, str):
                self.remove_item(item_info, remove_base_xpath)
            elif self.should_apply_item(item_info, context):
                self.remove_item(item_info['item'], remove_base_xpath)

    def should_apply_item(self, item_info: Dict[str, Union[str, List[str]]], context: str) -> bool:
        if 'include' in item_info and any(keyword in context for keyword in item_info['include']):
            return True
        if 'exclude' in item_info and not any(keyword in context for keyword in item_info['exclude']):
            return True
        return False