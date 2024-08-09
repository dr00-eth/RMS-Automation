from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import time
import includes.constants as constants

def wait_for_dropdown_and_select(driver, option_text, max_attempts=5, wait_time=2):
    for attempt in range(max_attempts):
        try:
            time.sleep(1)
            dropdown = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//select[contains(@class, 'ng-valid')]"))
            )
            select = Select(dropdown)
            select.select_by_visible_text(option_text)
            print(f"Selected '{option_text}' from dropdown.")
            time.sleep(3)  # Wait for page to update after selection
            return
        except (NoSuchElementException, StaleElementReferenceException) as e:
            if attempt < max_attempts - 1:
                print(f"Dropdown not ready, waiting and retrying... (Attempt {attempt + 1})")
                time.sleep(wait_time)
            else:
                print(f"Failed to select from dropdown after multiple attempts. Error: {str(e)}")
                raise

def wait_and_click(driver, by, value, timeout=10):
    element = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, value))
    )
    element.click()
    return element

def login_with_2fa(driver, username, password):
    driver.get(constants.LOGIN_URL)
    
    driver.find_element(By.CSS_SELECTOR, ".clientId").send_keys(constants.CLIENT_ID)
    driver.find_element(By.CSS_SELECTOR, ".username").send_keys(username)
    driver.find_element(By.CSS_SELECTOR, ".pw-field").send_keys(password)
    
    wait_and_click(driver, By.ID, "Login")

    print("2FA may be required. Please complete the 2FA process if prompted.")
    print("Navigate to the correct page and press Enter when you're ready to start the deletion process.")
    input()
    print("Starting row deletion process...")