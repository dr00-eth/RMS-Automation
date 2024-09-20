from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import time
from includes.constants import LOGIN_URL, CLIENT_ID, XPaths, DEFAULT_TIMEOUT
from includes.logging_config import get_logger

logger = get_logger(__name__)

def wait_for_dropdown_and_select(driver, option_text, max_attempts=5, wait_time=2):
    for attempt in range(max_attempts):
        try:
            time.sleep(1)
            dropdown = WebDriverWait(driver, DEFAULT_TIMEOUT).until(
                EC.presence_of_element_located((By.XPATH, "//select[contains(@class, 'ng-valid')]"))
            )
            select = Select(dropdown)
            select.select_by_visible_text(option_text)
            logger.info(f"Selected '{option_text}' from dropdown.")
            time.sleep(3)  # Wait for page to update after selection
            return
        except (NoSuchElementException, StaleElementReferenceException) as e:
            if attempt < max_attempts - 1:
                logger.warning(f"Dropdown not ready, waiting and retrying... (Attempt {attempt + 1})")
                time.sleep(wait_time)
            else:
                logger.error(f"Failed to select from dropdown after multiple attempts. Error: {str(e)}")
                raise

def wait_and_click(driver, by, value, timeout=DEFAULT_TIMEOUT):
    element = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, value))
    )
    element.click()
    return element

def login_with_2fa_and_wait(driver: webdriver.Chrome, username, password):
    driver.get(LOGIN_URL)
    
    driver.find_element(By.CSS_SELECTOR, XPaths.CLIENT_ID_INPUT).send_keys(CLIENT_ID)
    driver.find_element(By.CSS_SELECTOR, XPaths.USERNAME_INPUT).send_keys(username)
    driver.find_element(By.CSS_SELECTOR, XPaths.PASSWORD_INPUT).send_keys(password)
    
    wait_and_click(driver, By.ID, "Login")

    logger.info("2FA may be required. Please complete the 2FA process if prompted.")
    logger.info("Navigate to the correct page and press Enter when you're ready to start the automation process.")
    input()
    logger.info("Starting automation process...")

def login_training_with_2fa_and_wait(driver: webdriver.Chrome, username, password):
    driver.get(LOGIN_URL)
    
    driver.find_element(By.CSS_SELECTOR, XPaths.CLIENT_ID_INPUT).send_keys(CLIENT_ID)
    driver.find_element(By.CSS_SELECTOR, XPaths.USERNAME_INPUT).send_keys(username)
    driver.find_element(By.CSS_SELECTOR, XPaths.PASSWORD_INPUT).send_keys(password)
    
    wait_and_click(driver, By.ID, "LoginTraining")
    wait_and_click(driver, By.XPATH, "/html/body/div[8]/div[2]/div/a[1]")

    logger.info("2FA may be required. Please complete the 2FA process if prompted.")
    logger.info("Navigate to the correct page and press Enter when you're ready to start the automation process.")
    input()
    logger.info("Starting automation process...")