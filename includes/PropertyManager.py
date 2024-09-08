from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from includes.SeleniumHelper import SeleniumHelper

class PropertyManager:
    def __init__(self, selenium_helper: SeleniumHelper):
        self.selenium_helper = selenium_helper

    def select_property(self, property_name: str, available_xpath: str, selected_xpath: str) -> bool:
        try:
            property_xpath = f"{available_xpath}//div[contains(@class, 'GridLiteCell_PropertyName') and normalize-space(text())='{property_name}']"
            if not self.selenium_helper.wait_and_click(By.XPATH, property_xpath):
                print(f"Failed to click on property: {property_name}")
                return False

            add_button_xpath = "/html/body/div[20]/div/div/div/div/div[2]/div/div/div[2]/div/div/div[1]/div/div[1]/div[2]/a[2]"
            if not self.selenium_helper.wait_and_click(By.XPATH, add_button_xpath):
                print("Failed to click Add button")
                return False

            selected_property_xpath = f"{selected_xpath}//div[contains(@class, 'GridLiteCell_PropertyName') and normalize-space(text())='{property_name}']"
            if self.selenium_helper.wait_for_visibility(By.XPATH, selected_property_xpath):
                print(f"Successfully selected property: {property_name}")
                return True
            else:
                print(f"Property {property_name} did not appear in the selected list")
                return False
        except Exception as e:
            print(f"Error selecting property {property_name}: {str(e)}")
            return False

    def remove_property(self, property_name: str, selected_xpath: str) -> bool:
        try:
            property_xpath = f"{selected_xpath}//div[contains(@class, 'GridLiteCell_PropertyName') and normalize-space(text())='{property_name}']"
            if not self.selenium_helper.wait_and_click(By.XPATH, property_xpath):
                print(f"Failed to click on property to remove: {property_name}")
                return False

            remove_button_xpath = "/html/body/div[20]/div/div/div/div/div[2]/div/div/div[2]/div/div/div[2]/div/div[1]/div[1]/a[1]"
            if not self.selenium_helper.wait_and_click(By.XPATH, remove_button_xpath):
                print("Failed to click Remove button")
                return False

            try:
                self.selenium_helper.wait_for_invisibility(By.XPATH, property_xpath, timeout=5)
                print(f"Successfully removed property: {property_name}")
                return True
            except TimeoutException:
                print(f"Property {property_name} did not disappear from the selected list")
                return False
        except Exception as e:
            print(f"Error removing property {property_name}: {str(e)}")
            return False