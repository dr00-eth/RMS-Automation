from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import re
import logging
import includes.globals as globals

def setup_logging(property):
    # Setup for attributes logger
    attr_logger = logging.getLogger('attributes')
    attr_logger.setLevel(logging.INFO)
    attr_handler = logging.FileHandler(f'attribute_exceptions_{property}.log')
    attr_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    attr_handler.setFormatter(attr_formatter)
    attr_logger.addHandler(attr_handler)

    # Setup for application logger (optional, for other parts of your application)
    app_logger = logging.getLogger('application')
    app_logger.setLevel(logging.WARNING)
    app_handler = logging.FileHandler(f'application_{property}.log')
    app_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    app_handler.setFormatter(app_formatter)
    app_logger.addHandler(app_handler)

    # Prevent loggers from propagating to the root logger
    attr_logger.propagate = False
    app_logger.propagate = False

    return attr_logger, app_logger

def check_and_log_exceptions(driver, remove_base_xpath, target_attributes, site_number, attr_logger):
    selected_attributes = get_selected_attributes(driver, remove_base_xpath)
    for attr in selected_attributes:
        if attr not in target_attributes:
            message = f"Site {site_number}: Exception: Attribute '{attr}' is selected but not in target list."
            attr_logger.info(message)

def switch_to_attributes_tab(driver, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            attributes_tab = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'kt-widget__item')]/span[text()='Attributes']"))
            )
            attributes_tab.click()
            print("Switched to Attributes tab.")
            return True
        except TimeoutException as e:
            print(f"Attempt {attempt + 1}: Failed to switch to Attributes tab. Retrying...")
            time.sleep(1)
    print(f"Failed to switch to Attributes tab after {max_attempts} attempts.")
    return False

def is_attribute_selected(driver, attribute, base_xpath):
    try:
        element = driver.find_element(By.XPATH, f"{base_xpath}//div[contains(@class, 'GridLiteCell_Attribute') and contains(text(), '{attribute}')]")
        return 'selected' in element.get_attribute('class')
    except NoSuchElementException:
        return False

def select_attribute(driver, attribute, add_base_xpath):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, f"{add_base_xpath}//div[contains(@class, 'GridLiteCell_Attribute')]"))
        )
        available_attributes = driver.find_elements(By.XPATH, f"{add_base_xpath}//div[contains(@class, 'GridLiteCell_Attribute')]")
        for attr_element in available_attributes:
            if attr_element.text.strip() == attribute:
                ActionChains(driver).double_click(attr_element).perform()
                print(f"Added attribute: {attribute}")
                return True
        print(f"Attribute '{attribute}' not found in available list.")
        return False
    except Exception as e:
        print(f"Error selecting attribute '{attribute}': {str(e)}")
        return False

def remove_attribute(driver, attribute, remove_base_xpath):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, f"{remove_base_xpath}//div[contains(@class, 'GridLiteCell_Attribute')]"))
        )
        allocated_attributes = driver.find_elements(By.XPATH, f"{remove_base_xpath}//div[contains(@class, 'GridLiteCell_Attribute')]")
        for attr_element in allocated_attributes:
            if attr_element.text.strip() == attribute:
                ActionChains(driver).double_click(attr_element).perform()
                print(f"Removed attribute: {attribute}")
                return True
        print(f"Attribute '{attribute}' not found in allocated list.")
        return False
    except Exception as e:
        print(f"Error removing attribute '{attribute}': {str(e)}")
        return False

def get_selected_attributes(driver, base_xpath):
    selected_attributes = []
    try:
        # Locate all elements with the class 'GridLiteCell_Attribute' within the base_xpath
        elements = driver.find_elements(By.XPATH, f"{base_xpath}//div[contains(@class, 'GridLiteCell_Attribute')]")
        for element in elements:
            selected_attributes.append(element.text.strip())
    except NoSuchElementException:
        print("No selected attributes found.")
    return selected_attributes

def scroll_container(driver, container_xpath, at_end=False):
    if at_end:
        # Scroll up a bit and then back down
        scroll_script_up = """
        var container = document.evaluate(arguments[0], document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
        container.scrollBy(0, -container.clientHeight / 2);
        """
        driver.execute_script(scroll_script_up, container_xpath)
        time.sleep(0.5)
    
    # Scroll down
    scroll_script_down = """
    var container = document.evaluate(arguments[0], document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
    container.scrollBy(0, container.clientHeight / 2);
    """
    driver.execute_script(scroll_script_down, container_xpath)
    time.sleep(0.5)  # Wait for the scroll action to complete

def is_at_bottom(driver, container_xpath):
    scroll_script = """
    var container = document.evaluate(arguments[0], document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
    return (container.scrollHeight - container.scrollTop === container.clientHeight);
    """
    return driver.execute_script(scroll_script, container_xpath)

def extract_site_number(category_text):
    try:
        return int(re.search(r'\d+', category_text).group())
    except (AttributeError, ValueError):
        return None
    
def get_total_records(driver):
    try:
        total_records_element = driver.find_element(By.XPATH, "//*[@id='MainWindow']/div/div[1]/div[1]/label/span")
        total_records_text = total_records_element.text
        total_records = int(re.search(r'\d+', total_records_text).group())
        return total_records
    except Exception as e:
        print(f"Error getting total records: {str(e)}")
        return 0
    
def find_next_site(driver, current_number, container_xpath, max_attempts=40, lookahead=5):
    total_records = get_total_records(driver)  # Get the total records
    processed_rows_count = 0

    for attempt in range(max_attempts):
        try:
            rows = driver.find_elements(By.XPATH, f"{container_xpath}/div/div[contains(@class, 'GridLiteRow')]")
            for row in rows:
                category_element = row.find_element(By.XPATH, ".//div[contains(@class, 'GridLiteCell_Category')]")
                site_number = extract_site_number(category_element.text)
                if site_number and site_number > current_number and site_number <= current_number + lookahead:
                    return row, site_number

            processed_rows_count += len(rows)
            at_end = is_at_bottom(driver, container_xpath)
            print(f"Next site number {current_number + 1} not found. Attempt {attempt + 1}. Scrolling...")
            scroll_container(driver, container_xpath, at_end)
            time.sleep(0.5)

            # Check if we've processed all rows according to total records
            if processed_rows_count >= total_records:
                print(f"Processed {processed_rows_count} rows, which is equal to or exceeds the total records: {total_records}.")
                break
        except Exception as e:
            print(f"Error finding next site: {str(e)}")
            time.sleep(0.5)

    return None, None

def process_properties(driver, attributes_to_add, attributes_to_remove, attr_logger, start_number=1):
    current_number = start_number - 1
    container_xpath = "//*[@id='MainWindow']/div/div[2]/div/div/div[2]"
    total_records = get_total_records(driver)

    while True:
        next_row, next_number = find_next_site(driver, current_number, container_xpath, total_records)
        if not next_row:
            print(f"No more sites found after number {current_number}. Ending process.")
            break

        ActionChains(driver).double_click(next_row).perform()
        print(f"Processing site number {next_number}")
        
        if not switch_to_attributes_tab(driver):
            print(f"Skipping site number {next_number} due to failure in switching to Attributes tab.")
            continue

        add_base_xpath = "/html/body/div[15]/div/div/div/div/div[2]/div[2]/div[3]/div/div/div/div/div/div/div[1]/div/div[2]/div/div/div[2]/div"
        remove_base_xpath = "/html/body/div[15]/div/div/div/div/div[2]/div[2]/div[3]/div/div/div/div/div/div/div[2]/div/div[2]/div/div/div[2]/div"
        
        for attr in attributes_to_add:
            select_attribute(driver, attr, add_base_xpath)

        for attr in attributes_to_remove:
            remove_attribute(driver, attr, remove_base_xpath)

        check_and_log_exceptions(driver, remove_base_xpath, attributes_to_add, next_number, attr_logger)

        try:
            globals.wait_and_click(driver, By.CSS_SELECTOR, ".icon > .fa-floppy-disk-circle-xmark")
            print("Saved changes")
        except Exception as e:
            print(f"Failed to save changes for site number {next_number}. Error: {str(e)}")

        try:
            WebDriverWait(driver, 10).until(
                EC.invisibility_of_element_located((By.XPATH, "//div[contains(@class, 'modal-dialog')]"))
            )
            print("Modal closed")
        except TimeoutException:
            print(f"Modal did not close for site number {next_number}. Attempting to continue...")

        current_number = next_number
        time.sleep(0.5)