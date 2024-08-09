import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
import time
import includes.globals as globals

def get_grid_rows(driver):
    try:
        container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[16]/div/div/div/div/div[2]/div/div/div[2]/div"))
        )
        return container.find_elements(By.XPATH, './/div[contains(@class, "GridLiteRow")]')
    except TimeoutException:
        print("Timeout waiting for grid rows to load.")
        return []

def select_first_row(driver):
    try:
        rows = get_grid_rows(driver)
        if rows:
            # Click on the first column of the first row
            first_column = rows[0].find_element(By.XPATH, './/div[contains(@class, "GridLiteColumn")][1]')
            first_column.click()
            print("First row selected.")
            time.sleep(1)  # Wait for any potential UI updates
        else:
            print("No rows found to select.")
            return False
        return True
    except Exception as e:
        print(f"Error selecting first row: {str(e)}")
        return False

def delete_row(driver):
    try:
        if not select_first_row(driver):
            return False

        # Wait for the delete button to be clickable
        delete_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[16]/div/div/div/div/div[1]/div[4]/div[4]"))
        )
        delete_button.click()
        
        # Confirm deletion in the modal
        confirm_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="ResWarningsWrapper"]/div[4]/div/div[2]'))
        )
        confirm_button.click()
        
        print("Row deleted successfully.")
        time.sleep(2)  # Wait for the grid to refresh
        return True
    except ElementClickInterceptedException:
        print("Delete button is intercepted. Trying to remove overlays...")
        try:
            driver.execute_script("""
                var elements = document.getElementsByClassName('modal-backdrop');
                for(var i=0; i<elements.length; i++){
                    elements[i].parentNode.removeChild(elements[i]);
                }
            """)
            time.sleep(1)
            return delete_row(driver)  # Retry deletion
        except Exception as e:
            print(f"Error removing overlay: {str(e)}")
    except Exception as e:
        print(f"Error deleting row: {str(e)}")
    return False

def delete_all_rows(driver):
    while True:
        rows = get_grid_rows(driver)
        if not rows:
            print("No more rows to delete. Process complete.")
            break
        
        print(f"Rows remaining: {len(rows)}")
        if not delete_row(driver):
            print("Failed to delete row. Retrying...")
            time.sleep(2)

def automate_process(username, password):
    driver = webdriver.Chrome()
    try:
        driver.maximize_window()
        globals.login_with_2fa(driver, username, password)
        delete_all_rows(driver)

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

    automate_process(args.username, args.password)