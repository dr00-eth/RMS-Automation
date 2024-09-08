from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from typing import List, Dict, Union
from includes.SeleniumHelper import SeleniumHelper

class TaxManager:
    def __init__(self, selenium_helper: SeleniumHelper):
        self.selenium_helper = selenium_helper

    def _get_flattened_tax_text(self, element) -> str:
        try:
            return element.text.strip()
        except Exception as e:
            print(f"Error getting text: {str(e)}")
            return ""

    def _find_tax_elements(self, base_xpath: str) -> List:
        print(f"Searching for tax elements using base xpath: '{base_xpath}'")
        try:
            # Wait for any GridLiteCell element to be present
            self.selenium_helper.wait_for_element(By.XPATH, f"{base_xpath}//div[contains(@class, 'GridLiteCell')]", timeout=10)
            print("GridLiteCell elements found")
        except TimeoutException:
            print("GridLiteCell elements not found within timeout period")
            return []

        # Find all GridLiteCell elements
        elements = self.selenium_helper.driver.find_elements(By.XPATH, f"{base_xpath}//div[contains(@class, 'GridLiteCell')]")
        print(f"Found {len(elements)} GridLiteCell elements")
        return elements

    def select_tax(self, tax: str, base_xpath: str) -> None:
        print(f"Attempting to select tax: '{tax}'")
        tax_elements = self._find_tax_elements(base_xpath)
        
        for index, element in enumerate(tax_elements):
            print(f"Checking element {index + 1}:")
            flattened_text = self._get_flattened_tax_text(element)
            print(f"Comparing '{flattened_text}' with '{tax}'")
            if flattened_text == tax:
                print(f"Match found! Clicking element for tax: '{tax}'")
                xpath = f"({base_xpath}//div[contains(@class, 'GridLiteCell')])[{index + 1}]"
                success = self.selenium_helper.wait_and_click(By.XPATH, xpath, double_click=True, timeout=1, max_attempts=3)
                if success:
                    print(f"Added tax: '{tax}'")
                else:
                    print(f"Failed to add tax: '{tax}'")
                return
        print(f"Tax not found: '{tax}'")

    def remove_tax(self, tax: str, base_xpath: str) -> None:
        print(f"Attempting to remove tax: '{tax}'")
        tax_elements = self._find_tax_elements(base_xpath)
        
        for index, element in enumerate(tax_elements):
            print(f"Checking element {index + 1}:")
            flattened_text = self._get_flattened_tax_text(element)
            print(f"Comparing '{flattened_text}' with '{tax}'")
            if flattened_text == tax:
                print(f"Match found! Clicking element to remove tax: '{tax}'")
                xpath = f"({base_xpath}//div[contains(@class, 'GridLiteCell')])[{index + 1}]"
                success = self.selenium_helper.wait_and_click(By.XPATH, xpath, double_click=True, timeout=1, max_attempts=3)
                if success:
                    print(f"Removed tax: '{tax}'")
                else:
                    print(f"Failed to remove tax: '{tax}'")
                return
        print(f"Tax not found: '{tax}'")

    def get_selected_taxes(self, base_xpath: str) -> List[str]:
        print(f"Getting selected taxes using base xpath: '{base_xpath}'")
        elements = self._find_tax_elements(base_xpath)
        selected_taxes = [self._get_flattened_tax_text(element) for element in elements]
        print(f"Selected taxes: {selected_taxes}")
        return selected_taxes

    def should_apply_tax(self, tax_info: Union[str, Dict[str, Union[str, List[str]]]], site_name: str) -> bool:
        if isinstance(tax_info, str):
            return True
        if 'include' in tax_info and any(keyword in site_name for keyword in tax_info['include']):
            return True
        if 'exclude' in tax_info and not any(keyword in site_name for keyword in tax_info['exclude']):
            return True
        return False

    def process_taxes(self, taxes_to_add: List[Union[str, Dict[str, Union[str, List[str]]]]], 
                      taxes_to_remove: List[Union[str, Dict[str, Union[str, List[str]]]]], 
                      add_base_xpath: str, remove_base_xpath: str, site_name: str) -> None:
        print(f"Processing taxes for site: '{site_name}'")
        for tax_info in taxes_to_add:
            if isinstance(tax_info, str):
                tax = tax_info
            else:
                tax = tax_info['tax']
            
            if self.should_apply_tax(tax_info, site_name):
                print(f"Attempting to add tax: '{tax}'")
                self.select_tax(tax, add_base_xpath)
            else:
                print(f"Skipped adding tax: '{tax}' for site: '{site_name}'")

        for tax_info in taxes_to_remove:
            if isinstance(tax_info, str):
                tax = tax_info
            else:
                tax = tax_info['tax']
            
            if self.should_apply_tax(tax_info, site_name):
                print(f"Attempting to remove tax: '{tax}'")
                self.remove_tax(tax, remove_base_xpath)
            else:
                print(f"Skipped removing tax: '{tax}' for site: '{site_name}'")