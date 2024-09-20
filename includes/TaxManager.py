from includes.BaseManager import BaseManager
from includes.SeleniumHelper import SeleniumHelper
from typing import List, Dict, Union

class TaxManager(BaseManager):
    def __init__(self, selenium_helper: SeleniumHelper):
        super().__init__(selenium_helper)

    def select_tax(self, tax: str, base_xpath: str) -> None:
        self.select_item(tax, base_xpath)

    def remove_tax(self, tax: str, base_xpath: str) -> None:
        self.remove_item(tax, base_xpath)

    def get_selected_taxes(self, base_xpath: str) -> List[str]:
        return self.get_selected_items(base_xpath)

    def should_apply_tax(self, tax_info: Union[str, Dict[str, Union[str, List[str]]]], site_name: str) -> bool:
        if isinstance(tax_info, str):
            return True
        return self.should_apply_item(tax_info, site_name)

    def process_taxes(self, taxes_to_add: List[Union[str, Dict[str, Union[str, List[str]]]]], 
                      taxes_to_remove: List[Union[str, Dict[str, Union[str, List[str]]]]], 
                      add_base_xpath: str, remove_base_xpath: str, site_name: str) -> None:
        for tax_info in taxes_to_add:
            if isinstance(tax_info, str):
                tax = tax_info
            else:
                tax = tax_info['tax']
            
            if self.should_apply_tax(tax_info, site_name):
                self.logger.info(f"Attempting to add tax: '{tax}'")
                self.select_tax(tax, add_base_xpath)
            else:
                self.logger.info(f"Skipped adding tax: '{tax}' for site: '{site_name}'")

        for tax_info in taxes_to_remove:
            if isinstance(tax_info, str):
                tax = tax_info
            else:
                tax = tax_info['tax']
            
            if self.should_apply_tax(tax_info, site_name):
                self.logger.info(f"Attempting to remove tax: '{tax}'")
                self.remove_tax(tax, remove_base_xpath)
            else:
                self.logger.info(f"Skipped removing tax: '{tax}' for site: '{site_name}'")