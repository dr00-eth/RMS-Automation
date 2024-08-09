import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import re
import includes.globals as globals

def automate_process(username, password):
    driver = webdriver.Chrome()
    try:
        driver.maximize_window()
        globals.login_with_2fa(driver, username, password)

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