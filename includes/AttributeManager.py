from selenium.webdriver.common.by import By
from typing import List
from includes.SeleniumHelper import SeleniumHelper

class AttributeManager:
    def __init__(self, selenium_helper: SeleniumHelper):
        self.selenium_helper = selenium_helper

    def select_attribute(self, attribute: str, base_xpath: str) -> None:
        attribute_xpath = f"{base_xpath}//div[contains(@class, 'GridLiteCell_Attribute') and normalize-space(text())='{attribute}']"
        self.selenium_helper.wait_and_click(By.XPATH, attribute_xpath, double_click=True, timeout=1, max_attempts=3)
        print(f"Added attribute: {attribute}")

    def remove_attribute(self, attribute: str, base_xpath: str) -> None:
        attribute_xpath = f"{base_xpath}//div[contains(@class, 'GridLiteCell_Attribute') and normalize-space(text())='{attribute}']"
        self.selenium_helper.wait_and_click(By.XPATH, attribute_xpath, double_click=True, timeout=1, max_attempts=3)
        print(f"Removed attribute: {attribute}")

    def get_selected_attributes(self, base_xpath: str) -> List[str]:
        elements = self.selenium_helper.driver.find_elements(By.XPATH, f"{base_xpath}//div[contains(@class, 'GridLiteCell_Attribute')]")
        return [element.text.strip() for element in elements]

    def process_attributes(self, attributes_to_add: List[str], attributes_to_remove: List[str], add_base_xpath: str, remove_base_xpath: str) -> None:
        for attr in attributes_to_add:
            self.select_attribute(attr, add_base_xpath)
        for attr in attributes_to_remove:
            self.remove_attribute(attr, remove_base_xpath)