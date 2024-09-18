from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException
from selenium.webdriver.remote.webelement import WebElement
from typing import Optional
import time

class SeleniumHelper:
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver

    def wait_for_element(self, by: By, value: str, timeout: int = 20) -> Optional[WebElement]:
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
        except TimeoutException:
            print(f"Timeout waiting for element to be present: {value}")
            return None

    def wait_for_clickable_element(self, by: By, value: str, timeout: int = 10) -> Optional[WebElement]:
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
        except TimeoutException:
            print(f"Timeout waiting for element to be clickable: {value}")
            return None

    def wait_and_click(self, by: By, value: str, double_click: bool = False, timeout: int = 10, max_attempts: int = 10, retry_interval: float = 1.0) -> bool:
        for attempt in range(max_attempts):
            try:
                element = self.wait_for_clickable_element(by, value, timeout)
                if element and element.is_enabled():
                    if double_click:
                        ActionChains(self.driver).double_click(element).perform()
                        print(f"Successfully double-clicked element: {value}")
                    else:
                        element.click()
                        time.sleep(0.5)
                        print(f"Successfully clicked element: {value}")
                    return True
                else:
                    print(f"Element not clickable (Attempt {attempt + 1}/{max_attempts}): {value}")
            except ElementClickInterceptedException:
                print(f"Element click intercepted (Attempt {attempt + 1}/{max_attempts}): {value}")
            except Exception as e:
                print(f"Error clicking element (Attempt {attempt + 1}/{max_attempts}): {value}. Error: {str(e)}")
            
            if attempt < max_attempts - 1:
                time.sleep(retry_interval)
        
        print(f"Failed to {'double-click' if double_click else 'click'} element after {max_attempts} attempts: {value}")
        return False
    
    def is_element_visible(self, by: By, value: str, timeout: int = 0) -> bool:
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((by, value))
            )
            return element.is_displayed()
        except TimeoutException:
            return False
        except NoSuchElementException:
            return False

    def wait_for_visibility(self, by: By, value: str, timeout: int = 20) -> Optional[WebElement]:
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((by, value))
            )
        except TimeoutException:
            print(f"Timeout waiting for element to be visible: {value}")
            return None

    def wait_for_invisibility(self, by: By, value: str, timeout: int = 20) -> bool:
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.invisibility_of_element_located((by, value))
            )
        except TimeoutException:
            print(f"Timeout waiting for element to be invisible: {value}")
            return False
        
    def wait_until_stable(self, by: By, value: str, timeout: float = 10, poll_frequency: float = 0.5) -> Optional[WebElement]:
        end_time = time.time() + timeout
        last_exception = None
        while time.time() < end_time:
            try:
                element = self.driver.find_element(by, value)
                return element
            except StaleElementReferenceException as e:
                last_exception = e
            time.sleep(poll_frequency)
        
        if last_exception:
            raise last_exception
        raise TimeoutException(f"Element {value} not stable after {timeout} seconds")

    def is_element_visible_by_dimensions(self, by: By, value: str, timeout: int = 5) -> bool:
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            size = element.size
            print(f"Size: {element.size}")
            return size['height'] > 0 and size['width'] > 0 and size['height'] != 100 and size['width'] != 100
        except (TimeoutException, NoSuchElementException):
            return False

    def select_from_dropdown(self, by, value, option_text, max_attempts=5, wait_time=2):
        for attempt in range(max_attempts):
            try:
                dropdown = self.wait_for_element(by, value)
                select = Select(dropdown)
                select.select_by_visible_text(option_text)
                time.sleep(3)  # Wait for page to update after selection
                return
            except (NoSuchElementException, StaleElementReferenceException) as e:
                if attempt < max_attempts - 1:
                    print(f"Dropdown not ready, waiting and retrying... (Attempt {attempt + 1})")
                    time.sleep(wait_time)
                else:
                    raise e

    def wait_for_element_state(self, state: str, by: By, value: str, timeout: int = 10) -> Optional[WebElement]:
        try:
            if state == "clickable":
                return WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((by, value))
                )
            elif state == "visible":
                return WebDriverWait(self.driver, timeout).until(
                    EC.visibility_of_element_located((by, value))
                )
            elif state == "invisible":
                return WebDriverWait(self.driver, timeout).until(
                    EC.invisibility_of_element_located((by, value))
                )
            elif state == "present":
                return WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((by, value))
                )
            else:
                raise ValueError(f"Unsupported state: {state}")
        except TimeoutException:
            print(f"Timeout waiting for element to be {state}: {value}")
            return None

    def is_element_present(self, by: By, value: str) -> bool:
        try:
            self.driver.find_element(by, value)
            return True
        except NoSuchElementException:
            return False

    def scroll_element(self, element: WebElement, amount: int, at_end: bool):
        if at_end:
            # Scroll up a bit and then back down
            self.driver.execute_script("""
                arguments[0].scrollBy(0, -arguments[0].clientHeight / 2);
            """, element)
            time.sleep(0.5)

        self.driver.execute_script("arguments[0].scrollTop += arguments[1];", element, amount)

    def is_at_bottom(self, element: WebElement):
        return self.driver.execute_script(
            "return arguments[0].scrollHeight - arguments[0].scrollTop === arguments[0].clientHeight;",
            element
        )

    def is_modal_visible(self, class_name):
        return self.is_element_present(By.CLASS_NAME, class_name)

    def wait_for_modal_to_be_visible(self, class_name, timeout=5):
        return self.wait_for_element_state("visible", By.CLASS_NAME, class_name, timeout)