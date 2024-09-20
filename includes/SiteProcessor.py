from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from typing import Tuple, Optional, List
import time
import re
from includes.SeleniumHelper import SeleniumHelper
from includes.AttributeManager import AttributeManager
from includes.TaxManager import TaxManager
from includes.logging_config import get_logger
from includes.constants import DEFAULT_TIMEOUT

class SiteProcessor:
    def __init__(self, selenium_helper: SeleniumHelper, attribute_manager: AttributeManager, tax_manager: TaxManager):
        self.selenium_helper = selenium_helper
        self.attribute_manager = attribute_manager
        self.tax_manager = tax_manager
        self.logger = get_logger(__name__)

    def extract_site_number(self, category_text: str) -> Optional[int]:
        match = re.search(r'\d+', category_text)
        if match:
            number = int(match.group())
            self.logger.info(f"Extracted number: {number}")
            return number
        else:
            self.logger.warning(f"No number found in: {category_text}")
            return None

    def find_next_site(self, current_number: int, container_xpath: str, max_attempts: int = 40, lookahead: int = 30) -> Tuple[Optional[WebElement], Optional[int], Optional[str]]:
        total_records = self.get_total_records()
        self.logger.info(f"Total records: {total_records}")
        processed_rows_count = 0

        for attempt in range(max_attempts):
            self.logger.info(f"Attempt {attempt + 1}/{max_attempts}")
            try:
                rows: List[WebElement] = self.selenium_helper.driver.find_elements(By.XPATH, f"{container_xpath}/div[contains(@class, 'GridLiteRow')]")
                self.logger.info(f"Found {len(rows)} rows in this attempt")

                for index, row in enumerate(rows):
                    try:
                        category_element = row.find_element(By.XPATH, ".//div[contains(@class, 'GridLiteCell_Category')]")
                        category_text = category_element.text
                        self.logger.info(f"Row {index + 1}: Category text: {category_text}")
                        site_number = self.extract_site_number(category_text)
                        self.logger.info(f"Extracted site number: {site_number}")
                        
                        if site_number and site_number > current_number and site_number <= current_number + lookahead:
                            self.logger.info(f"Found next site: {site_number}")
                            return row, site_number, category_text
                    except NoSuchElementException:
                        self.logger.warning(f"Row {index + 1}: No category element found")
                        continue

                processed_rows_count += len(rows)
                self.logger.info(f"Processed rows so far: {processed_rows_count}")

                container = self.selenium_helper.wait_for_element(By.XPATH, container_xpath)
                if not container:
                    self.logger.error("Container element not found. Exiting loop.")
                    break

                at_end = self.selenium_helper.is_at_bottom(container)
                self.logger.info(f"At end of container: {at_end}")
                self.logger.info(f"Next site number {current_number + 1} not found. Attempt {attempt + 1}. Scrolling...")
                self.selenium_helper.scroll_element(container, container.size['height'] // 2, at_end)

                if processed_rows_count >= total_records:
                    self.logger.info(f"Processed {processed_rows_count} rows, which is equal to or exceeds the total records: {total_records}.")
                    break

                time.sleep(0.5)

            except Exception as e:
                self.logger.error(f"Error finding next site: {str(e)}")
                time.sleep(0.5)

        self.logger.warning("No more sites found. Returning None.")
        return None, None, None

    def get_total_records(self) -> int:
        total_records_element = self.selenium_helper.wait_for_element(By.XPATH, "//*[@id='MainWindow']/div/div[1]/div[1]/label/span")
        total_records_text = total_records_element.text if total_records_element else ""
        match = re.search(r'\d+', total_records_text)
        return int(match.group()) if match else 0

    def switch_to_tab(self, tab_name, max_attempts=3):
        for attempt in range(max_attempts):
            try:
                tab_xpath = f"//a[contains(@class, 'kt-widget__item')]/span[text()='{tab_name}']"
                if self.selenium_helper.wait_and_click(By.XPATH, tab_xpath, timeout=5):
                    self.logger.info(f"Switched to {tab_name} tab.")
                    return True
                else:
                    self.logger.warning(f"Attempt {attempt + 1}: Failed to switch to {tab_name} tab. Retrying...")
            except Exception as e:
                self.logger.error(f"Error switching to {tab_name} tab: {str(e)}")
            time.sleep(1)
        self.logger.error(f"Failed to switch to {tab_name} tab after {max_attempts} attempts.")
        return False

    def process_site_attrs(self, row: WebElement, site_number: int, attributes_to_add: List[str], attributes_to_remove: List[str]) -> None:
        ActionChains(self.selenium_helper.driver).double_click(row).perform()
        self.logger.info(f"Processing site number {site_number}")
        
        if not self.switch_to_tab("Attributes"):
            self.logger.warning(f"Skipping site number {site_number} due to failure in switching to Attributes tab.")
            return

        add_base_xpath = "/html/body/div[15]/div/div/div/div/div[2]/div[2]/div[3]/div/div/div/div/div/div/div[1]/div/div[2]/div/div/div[2]/div"
        remove_base_xpath = "/html/body/div[15]/div/div/div/div/div[2]/div[2]/div[3]/div/div/div/div/div/div/div[2]/div/div[2]/div/div/div[2]/div"

        self.attribute_manager.process_attributes(attributes_to_add, attributes_to_remove, add_base_xpath, remove_base_xpath)

        selected_attributes = self.attribute_manager.get_selected_attributes(remove_base_xpath)
        for attr in selected_attributes:
            if attr not in attributes_to_add:
                self.logger.info(f"Site {site_number}: Exception: Attribute '{attr}' is selected but not in target list.")

        self.selenium_helper.wait_and_click(By.CSS_SELECTOR, ".icon > .fa-floppy-disk-circle-xmark")
        try:
            WebDriverWait(self.selenium_helper.driver, DEFAULT_TIMEOUT).until(
                EC.invisibility_of_element_located((By.XPATH, "//div[contains(@class, 'modal-dialog')]"))
            )
            self.logger.info("Modal closed")
        except TimeoutException:
            self.logger.warning(f"Modal did not close for site number {site_number}. Attempting to continue...")

        time.sleep(0.5)

    def process_site_taxes(self, row: WebElement, site_number: int, site_name: str, taxes_to_add: List[str], taxes_to_remove: List[str]) -> None:
        ActionChains(self.selenium_helper.driver).double_click(row).perform()
        self.logger.info(f"Processing site number {site_number}")
        
        if not self.switch_to_tab("Accounting"):
            self.logger.warning(f"Skipping site number {site_number} due to failure in switching to Accounting tab.")
            return

        add_base_xpath = "/html/body/div[15]/div/div/div/div/div[2]/div[2]/div[1]/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div[2]/div"
        remove_base_xpath = "/html/body/div[15]/div/div/div/div/div[2]/div[2]/div[1]/div/div/div[2]/div/div/div[2]/div[1]/div/div[2]/div/div/div/div[2]/div"

        self.tax_manager.process_taxes(taxes_to_add, taxes_to_remove, add_base_xpath, remove_base_xpath, site_name)

        selected_taxes = self.tax_manager.get_selected_taxes(remove_base_xpath)
        for tax in selected_taxes:
            if tax not in taxes_to_add:
                self.logger.info(f"Site {site_number}: Exception: '{tax}' is selected but not in target list.")

        self.selenium_helper.wait_and_click(By.CSS_SELECTOR, ".icon > .fa-floppy-disk-circle-xmark")
        try:
            WebDriverWait(self.selenium_helper.driver, DEFAULT_TIMEOUT).until(
                EC.invisibility_of_element_located((By.XPATH, "//div[contains(@class, 'modal-dialog')]"))
            )
            self.logger.info("Modal closed")
        except TimeoutException:
            self.logger.warning(f"Modal did not close for site number {site_number}. Attempting to continue...")

        time.sleep(0.5)