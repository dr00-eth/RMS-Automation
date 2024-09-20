from includes.BaseManager import BaseManager
from includes.SeleniumHelper import SeleniumHelper
from typing import List

class AttributeManager(BaseManager):
    def __init__(self, selenium_helper: SeleniumHelper):
        super().__init__(selenium_helper)

    def select_attribute(self, attribute: str, base_xpath: str) -> None:
        self.select_item(attribute, base_xpath)

    def remove_attribute(self, attribute: str, base_xpath: str) -> None:
        self.remove_item(attribute, base_xpath)

    def get_selected_attributes(self, base_xpath: str) -> List[str]:
        return self.get_selected_items(base_xpath)

    def process_attributes(self, attributes_to_add: List[str], attributes_to_remove: List[str], add_base_xpath: str, remove_base_xpath: str) -> None:
        self.process_items(attributes_to_add, attributes_to_remove, add_base_xpath, remove_base_xpath)