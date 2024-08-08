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

def open_display_order_panel(driver):
    wait_and_click(driver, By.XPATH, '//*[@id="MainWindow"]/div/div[1]/div[2]/a[1]')
    print("Display Order panel opened")
    time.sleep(2)  # Short wait for panel to load

def get_site_rows(driver):
    container = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="CategoryDisplayOrder"]/div[2]/div/div[1]/div/div[2]/div/div/div[2]/div'))
    )
    return container.find_elements(By.XPATH, './/div[contains(@class, "GridLiteRow")]')

def get_site_number(row):
    try:
        cell_content = row.find_element(By.XPATH, './/div[contains(@class, "GridLiteCellContents")]').text
        match = re.search(r'\d+', cell_content)
        return int(match.group()) if match else None
    except:
        return None

def move_row_to_position(driver, row, current_position, target_position):
    ActionChains(driver).move_to_element(row).click().perform()
    
    moves = abs(target_position - current_position)
    direction = "up" if target_position < current_position else "down"
    button_xpath = f'//*[@id="CategoryDisplayOrder"]/div[2]/div/div[1]/div/div[1]/div[2]/a[{1 if direction == "up" else 2}]'
    
    for i in range(moves):
        wait_and_click(driver, By.XPATH, button_xpath)
        #print(f"  Click {direction} button ({i+1}/{moves})")
    
    print(f"Moved site from position {current_position} to {target_position}")

def order_sites(driver):
    while True:
        rows = get_site_rows(driver)
        current_order = [get_site_number(row) for row in rows]
        print(f"Current order: {current_order}")
        
        # Create a list of tuples (site_number, current_index), excluding None values
        numbered_sites = [(num, i) for i, num in enumerate(current_order) if num is not None]
        
        # Sort the list based on site numbers
        sorted_sites = sorted(numbered_sites, key=lambda x: x[0])
        
        if [site[0] for site in numbered_sites] == [site[0] for site in sorted_sites]:
            print("Sites are in correct order.")
            break
        
        # Find the first out-of-order site
        for target_position, (site_number, current_position) in enumerate(sorted_sites):
            if current_position != target_position:
                # Calculate how many positions to move
                positions_to_move = current_position - target_position
                direction = "up" if positions_to_move > 0 else "down"
                
                print(f"Moving site {site_number} from position {current_position} to {target_position} ({direction} {abs(positions_to_move)} positions)")
                
                move_row_to_position(driver, rows[current_position], current_position, target_position)
                break  # Only move one site per iteration
        
        #time.sleep(0.5)  # Short wait before next iteration

def automate_process(username, password):
    driver = webdriver.Chrome()
    try:
        driver.maximize_window()
        login_with_2fa(driver, username, password)
        
        driver.get("https://app13.rmscloud.com/#!/Setup/Category")
        print("Navigated to Setup/Category page")
        
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='MainWindow']/div/div[2]/div/div/div[2]/div"))
        )
        print("Main window loaded")

        open_display_order_panel(driver)
        order_sites(driver)

        print("Process completed successfully")
        print("Please verify the results and save if correct.")
        input("Press Enter when you're done verifying and saving...")
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