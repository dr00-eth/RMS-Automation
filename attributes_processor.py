import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import traceback
import includes.helpers as helpers
from includes import globals

def automate_process(username, password, property, attr_logger, start_number=1):
    driver = None
    try:
        driver = webdriver.Chrome()
        driver.maximize_window()

        globals.login_with_2fa(driver, username, password)

        driver.get("https://app13.rmscloud.com/#!/Setup/Category")
        print("Navigated to Setup/Category page")

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='MainWindow']/div/div[2]/div/div/div[2]/div"))
        )
        print("Main window loaded")

        helpers.wait_for_dropdown_and_select(driver, property)

        helpers.process_properties(driver, attributes_to_add, attributes_to_remove, attr_logger, start_number)

        print("Process completed successfully")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("Traceback:")
        print(traceback.format_exc())
    finally:
        if driver:
            driver.quit()
        print("Script execution completed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RMS Cloud Automation Script")
    parser.add_argument("username", help="Your RMS Cloud username")
    parser.add_argument("password", help="Your RMS Cloud password")
    parser.add_argument("property", help="The property to automate, must match dropdown exactly")
    parser.add_argument("--start", type=int, default=1, help="Starting site number (default: 1)")
    args = parser.parse_args()

    attributes_to_add = [
        "30 amp max electric service",
        "50 amp max electric service",
        "Picnic Table",
        "Pet Friendly",
        "Wifi",
        "Concrete Pad"
    ]

    attributes_to_remove = [
        "BBQ Grill",
        "Outdoor Covered Sitting Area",
        "paved",
        "Fireplace/Firepit"
    ]

    attr_logger, app_logger = helpers.setup_logging(args.property)
    automate_process(args.username, args.password, args.property, attr_logger, args.start)
