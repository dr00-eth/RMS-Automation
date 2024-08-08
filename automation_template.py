import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import re

def wait_and_click(driver, by, value, timeout=10):
    element = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, value))
    )
    element.click()
    return element

def login_with_2fa(driver, username, password):
    driver.get("https://app13.rmscloud.com/Login")
    
    driver.find_element(By.CSS_SELECTOR, ".clientId").send_keys("19681")
    driver.find_element(By.CSS_SELECTOR, ".username").send_keys(username)
    driver.find_element(By.CSS_SELECTOR, ".pw-field").send_keys(password)
    
    wait_and_click(driver, By.ID, "Login")

    print("2FA may be required. Please complete the 2FA process if prompted.")
    print("Press Enter when you have completed the 2FA process and are logged in.")
    input()
    print("Continuing after 2FA...")

def automate_process(username, password):
    driver = webdriver.Chrome()
    try:
        driver.maximize_window()
        login_with_2fa(driver, username, password)

        #LOGIC GOES HERE

        print("Process completed successfully")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        driver.quit()
        print("Script execution completed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RMS Cloud Display Order Automation Script")
    parser.add_argument("username", help="Your RMS Cloud username")
    parser.add_argument("password", help="Your RMS Cloud password")
    args = parser.parse_args()

    automate_process(args.username, args.password)