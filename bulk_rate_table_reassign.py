import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webelement import WebElement
import time
from includes.SeleniumHelper import SeleniumHelper
from includes.PropertyManager import PropertyManager
from includes import globals

class BulkRateTableReassign:
    def __init__(self, driver):
        self.driver = driver
        self.selenium_helper = SeleniumHelper(driver)
        self.property_manager = PropertyManager(self.selenium_helper)

    def get_grid_rows(self):
        try:
            container = self.selenium_helper.wait_for_element(
                By.XPATH, "/html/body/div[16]/div/div/div/div/div[2]/div/div/div[2]/div"
            )
            return container.find_elements(By.XPATH, './/div[contains(@class, "GridLiteRow")]')
        except TimeoutException:
            print("Timeout waiting for grid rows to load.")
            return []

    def is_row_selected(self, row: WebElement):
        try:
            checkbox = row.find_element(By.XPATH, './/div[contains(@class, "GridLiteColumn")][1]//input[@type="checkbox"]')
            return checkbox.is_selected()
        except:
            return False

    def click_first_row_with_retry(self, max_attempts=5, wait_time=10):
        edit_button_xpath = "/html/body/div[16]/div/div/div/div/div[1]/div[4]/div[4]"
        for attempt in range(max_attempts):
            try:
                rows = self.get_grid_rows()
                if not rows:
                    print("No rows found.")
                    return False
                
                first_row = rows[0]
                
                if not self.is_row_selected(first_row):
                    first_row.click()
                    print(f"Selected first row (Attempt {attempt + 1})")
                else:
                    print(f"First row already selected (Attempt {attempt + 1})")
                
                if self.selenium_helper.wait_and_click(By.XPATH, edit_button_xpath, timeout=wait_time, max_attempts=10, retry_interval=2.0):
                    print(f"Clicked Edit button (Attempt {attempt + 1})")
                    
                    if self.selenium_helper.wait_for_modal_to_be_visible("RateTableSetup", timeout=5):
                        print("RateTableSetup modal is visible and interactable")
                        return True
                    else:
                        print(f"RateTableSetup modal is not visible or interactable (Attempt {attempt + 1})")
                else:
                    print(f"Failed to click Edit button (Attempt {attempt + 1})")
            
            except Exception as e:
                print(f"Error selecting row and clicking Edit (Attempt {attempt + 1}): {str(e)}")
            
            if attempt < max_attempts - 1:
                print("Retrying...")
                time.sleep(2)
        
        print("Failed to open RateTableSetup modal after all attempts")
        return False

    def click_properties_button_with_retry(self, max_attempts=3):
        properties_button_xpath = "//*[@id='RateTableTopSection']/div/div/div[1]/div[2]/a"
        for attempt in range(max_attempts):
            try:
                self.selenium_helper.wait_and_click(By.XPATH, properties_button_xpath)
                print(f"Clicked properties button (Attempt {attempt + 1})")
                
                if self.selenium_helper.is_modal_visible("AdvancedPropertySelectionModal"):
                    print("AdvancedPropertySelectionModal is immediately visible and interactable")
                    return True
                
                if self.selenium_helper.wait_for_modal_to_be_visible("AdvancedPropertySelectionModal", timeout=5):
                    print("AdvancedPropertySelectionModal became visible and interactable")
                    return True
                else:
                    print(f"AdvancedPropertySelectionModal is not visible or interactable (Attempt {attempt + 1})")
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {str(e)}")
            
            if attempt < max_attempts - 1:
                time.sleep(1)
        
        print("Failed to open AdvancedPropertySelectionModal after all attempts")
        return False

    def check_and_dismiss_error_modal(self, timeout=5):
        try:
            if self.selenium_helper.is_modal_visible("ResStatusWarnings"):
                print("Server error modal detected.")
                
                ok_button = self.selenium_helper.wait_for_element_state(
                    "clickable",
                    By.XPATH,
                    '//*[@id="ResWarningsWrapper"]/div[4]/div/div[1]',
                    timeout
                )
                ok_button.click()
                print("Dismissed server error modal.")
                return True
            else:
                return False
        except TimeoutException:
            print("Timeout occurred while trying to dismiss error modal.")
            return False
        except Exception as e:
            print(f"Error handling server error modal: {str(e)}")
            return False

    def update_all_rows(self, max_retries=3):
        retry_count = 0
        while retry_count < max_retries:
            try:
                if self.check_and_dismiss_error_modal():
                    print("Dismissed error modal, retrying from the beginning.")
                    retry_count += 1
                    continue

                if not self.click_first_row_with_retry():
                    print("Failed to select and edit a row. Retrying from the beginning.")
                    retry_count += 1
                    continue

                if self.check_and_dismiss_error_modal():
                    print("Dismissed error modal after row selection, retrying from the beginning.")
                    retry_count += 1
                    continue

                if not self.click_properties_button_with_retry():
                    print("Failed to open AdvancedPropertySelectionModal. Retrying from the beginning.")
                    retry_count += 1
                    continue

                available_xpath = "/html/body/div[20]/div/div/div/div/div[2]/div/div/div[2]/div/div/div[1]/div/div[2]/div[2]/div/div[2]/div"
                selected_xpath = "/html/body/div[20]/div/div/div/div/div[2]/div/div/div[2]/div/div/div[2]/div/div[2]/div/div/div[2]/div"

                self.property_manager.select_property(property_to_select, available_xpath, selected_xpath)
                self.property_manager.remove_property(property_to_remove, selected_xpath)

                self.selenium_helper.wait_and_click(By.XPATH, "/html/body/div[20]/div/div/div/div/div[1]/div/div[1]")
                print("Closed properties modal.")

                self.selenium_helper.wait_and_click(By.XPATH, "/html/body/div[17]/div/div/div/div/div[1]/div[2]/div[4]")
                print("Saved changes and exited to main window.")

                time.sleep(1)

                if self.check_and_dismiss_error_modal():
                    print("Dismissed error modal after saving, retrying from the beginning.")
                    retry_count += 1
                    continue

                print("Successfully processed a row.")
                retry_count = 0  # Reset the retry count on success

            except Exception as e:
                print(f"An error occurred while processing a row: {str(e)}")
                retry_count += 1
                print(f"Retrying from the beginning. Attempt {retry_count} of {max_retries}")

            time.sleep(1)

        if retry_count >= max_retries:
            print(f"Maximum retries ({max_retries}) reached. Exiting the process.")

def automate_process(username, password):
    driver = webdriver.Chrome()
    try:
        driver.maximize_window()
        globals.login_with_2fa_and_wait(driver, username, password)
        
        bulk_reassign = BulkRateTableReassign(driver)
        bulk_reassign.update_all_rows(max_retries=10)

        print("Process completed successfully")
        print("Please verify the results.")
        input("Press Enter when you're done verifying...")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        driver.quit()
        print("Script execution completed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RMS Cloud Delete Rows Automation Script")
    parser.add_argument("username", help="Your RMS Cloud username")
    parser.add_argument("password", help="Your RMS Cloud password")
    args = parser.parse_args()

    property_to_select="FireflyResort- Coastal Bend"
    property_to_remove="Firefly RV Resort Fredericksburg"

    automate_process(args.username, args.password)