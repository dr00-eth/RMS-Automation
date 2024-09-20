import argparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.remote.webelement import WebElement
import csv
import os
import time
import traceback
from includes.SeleniumHelper import SeleniumHelper
from includes import globals
from typing import List, Dict
from includes.logging_config import setup_logging, get_logger
from includes.constants import DEFAULT_TIMEOUT, XPaths

class GuestBillManager:
    def __init__(self, selenium_helper: SeleniumHelper):
        self.selenium_helper = selenium_helper
        self.logger = get_logger(__name__)

    def void_fee(self, row: WebElement):
        row.click()
        time.sleep(0.5)

        corrections_button_xpath = XPaths.CORRECTIONS_BUTTON
        if not self.selenium_helper.wait_and_click(By.XPATH, corrections_button_xpath, timeout=DEFAULT_TIMEOUT):
            self.logger.error("Failed to click 'Corrections' button")
            return

        void_charge_xpath = XPaths.VOID_CHARGE_OPTION
        if not self.selenium_helper.wait_and_click(By.XPATH, void_charge_xpath, timeout=DEFAULT_TIMEOUT):
            self.logger.error("Failed to click 'Void Charge' option")
            return

        modal = self.selenium_helper.wait_for_element(By.CLASS_NAME, "VoidChargeModal", timeout=DEFAULT_TIMEOUT)
        if not modal:
            self.logger.error("Void charge modal did not appear")
            return

        incorrect_entry_xpath = XPaths.INCORRECT_ENTRY_ROW
        if not self.selenium_helper.wait_and_click(By.XPATH, incorrect_entry_xpath, timeout=DEFAULT_TIMEOUT):
            self.logger.error("Failed to select 'Incorrect Entry' reason")
            return

        void_button_xpath = XPaths.VOID_TRANSACTION_BUTTON
        if not self.selenium_helper.wait_and_click(By.XPATH, void_button_xpath, timeout=DEFAULT_TIMEOUT):
            self.logger.error("Failed to click 'Void Transaction' button")
            return

        if not self.selenium_helper.wait_for_invisibility(By.CLASS_NAME, "VoidChargeModal", timeout=DEFAULT_TIMEOUT):
            self.logger.error("Void charge modal did not close")

    def is_matching_fee(self, description: str, fee_to_remove: str) -> bool:
        return fee_to_remove.lower() in description.lower()

    def get_grid_rows(self):
        accounts_data_grid = self.selenium_helper.wait_for_element(By.CLASS_NAME, "AccountsDataGrid")
        line_items = accounts_data_grid.find_element(By.XPATH, './/div[contains(@class, "GridLiteRowsContainer")]')
        return line_items.find_elements(By.XPATH, './/div[contains(@class, "GridLiteRow")]')

    def remove_fees(self, fees_to_remove: List[str]):
        fees_removed = 0
        while fees_removed < len(fees_to_remove):
            rows = self.get_grid_rows()
            fee_found = False

            for row in rows:
                try:
                    columns = row.find_elements(By.XPATH, './/div[contains(@class, "GridLiteColumn")]')
                    if len(columns) >= 3:
                        description = columns[2].text.strip()
                        
                        for fee in fees_to_remove:
                            if self.is_matching_fee(description, fee):
                                self.logger.info(f"Attempting to void fee: {description} (matched with '{fee}')")
                                self.void_fee(row)
                                time.sleep(3)
                                fees_removed += 1
                                fee_found = True
                                break

                    if fee_found:
                        break
                except Exception as e:
                    self.logger.error(f"Error processing a row: {str(e)}")

            if not fee_found:
                self.logger.info("No more matching fees found")
                break

        self.logger.info(f"Finished processing fees. Removed {fees_removed} fee(s)")

class ResWork:
    def __init__(self, driver, selenium_helper: SeleniumHelper, remove_fees: bool = False):
        self.driver = driver
        self.selenium_helper = selenium_helper
        self.csv_filename = "reservation_data.csv"
        self.csv_headers = ["ReservationId", "ResStatus", "ArriveDate", "DepartDate", "LegacyResId", "BaseRate", "TotalRate", "GuestBill", "ResNote", "ItemizedBill"]
        self.temp_filename = "temp_reservation_data.csv"
        self.guest_bill_manager = GuestBillManager(selenium_helper)
        self.remove_fees = remove_fees
        self.logger = get_logger(__name__)

    def process_reservations(self, csv_file_path, start_reservation_id=None, has_headers=False):
        with open(csv_file_path, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            
            if has_headers:
                next(csv_reader)  # Skip the header row
            
            reservation_ids = list(csv_reader)
            total_rows = len(reservation_ids)

            start_processing = start_reservation_id is None
            processed_count = 0

            with open(self.csv_filename, 'a', newline='') as output_file:
                writer = csv.DictWriter(output_file, fieldnames=self.csv_headers)
                
                if not os.path.isfile(self.csv_filename) or os.path.getsize(self.csv_filename) == 0:
                    writer.writeheader()

                for index, row in enumerate(reservation_ids, start=1):
                    reservation_id = row[0]  # Assuming reservation ID is in the first column
                    
                    if reservation_id == start_reservation_id:
                        start_processing = True

                    if start_processing:
                        processed_count += 1
                        print(f"Processing reservation {processed_count} of {total_rows}: {reservation_id}")
                        try:
                            self.process_single_reservation(reservation_id, writer)
                        except Exception as e:
                            print(f"Error processing reservation {reservation_id}: {str(e)}")
                            print(f"Last successfully processed reservation: {reservation_id}")
                            return  # Stop processing and exit

    def identify_missing_data(self, input_csv_path: str) -> Dict[str, List[str]]:
        input_reservations = set()
        print(f"Reading input reservations from: {input_csv_path}")
        with open(input_csv_path, 'r') as input_file:
            input_reader = csv.reader(input_file)
            next(input_reader)  # Skip header
            for row in input_reader:
                input_reservations.add(row[0])  # Assuming reservation ID is in the first column
        print(f"Total input reservations: {len(input_reservations)}")
        print(f"Sample of input reservations: {list(input_reservations)[:5]}")

        missing_data = {}
        processed_reservations = set()
        print(f"Reading processed reservations from: {self.csv_filename}")
        with open(self.csv_filename, 'r') as existing_file:
            reader = csv.DictReader(existing_file)
            existing_headers = reader.fieldnames
            for row in reader:
                reservation_id = row['ReservationId']
                processed_reservations.add(reservation_id)
                missing_fields = []
                for field in self.csv_headers:
                    if field not in existing_headers or not row.get(field, ''):
                        missing_fields.append(field)
                if reservation_id in input_reservations and missing_fields:
                    missing_data[reservation_id] = missing_fields
        print(f"Total processed reservations: {len(processed_reservations)}")
        print(f"Sample of processed reservations: {list(processed_reservations)[:5]}")

        # Check for reservations in input but not in processed
        missing_reservations = input_reservations - processed_reservations
        for reservation_id in missing_reservations:
            missing_data[reservation_id] = self.csv_headers  # All fields are missing
        print(f"Reservations in input but not in processed: {len(missing_reservations)}")
        print(f"Sample of missing reservations: {list(missing_reservations)[:5]}")

        print(f"Total missing or incomplete reservations: {len(missing_data)}")
        return missing_data

    def update_missing_data(self, input_csv_path: str, start_reservation_id: str = None):
        self.update_csv_headers()
        
        missing_data = self.identify_missing_data(input_csv_path)
        total_to_update = len(missing_data)
        
        print(f"Found {total_to_update} reservations to update or add")
        
        updated_count = 0
        added_count = 0
        skipped_count = 0
        error_count = 0
        start_processing = start_reservation_id is None

        with open(self.csv_filename, 'r') as existing_file, open(self.temp_filename, 'w', newline='') as temp_file:
            reader = csv.DictReader(existing_file)
            writer = csv.DictWriter(temp_file, fieldnames=self.csv_headers)
            writer.writeheader()

            existing_reservations = {row['ReservationId']: row for row in reader if row['ReservationId']}

            for reservation_id in missing_data:
                if reservation_id == start_reservation_id:
                    start_processing = True

                if not start_processing:
                    if reservation_id in existing_reservations:
                        writer.writerow(self.clean_row_data(existing_reservations[reservation_id]))
                    continue

                if reservation_id in existing_reservations:
                    row = existing_reservations[reservation_id]
                    if row.get('ResStatus') == "Cancelled":
                        print(f"Skipping cancelled reservation: {reservation_id}")
                        skipped_count += 1
                        writer.writerow(self.clean_row_data(row))
                        continue

                    updated_count += 1
                    print(f"Updating existing reservation {updated_count} of {total_to_update}: {reservation_id}")
                    try:
                        updated_row = self.process_single_reservation(reservation_id, None, row)
                        cleaned_row = self.clean_row_data(updated_row)
                        if any(cleaned_row.values()):  # Only write non-empty rows
                            writer.writerow(cleaned_row)
                        else:
                            print(f"Warning: Empty data for reservation {reservation_id}, keeping original data")
                            writer.writerow(self.clean_row_data(row))
                    except Exception as e:
                        print(f"Error processing reservation {reservation_id}: {str(e)}")
                        writer.writerow(self.clean_row_data(row))
                        error_count += 1
                else:
                    added_count += 1
                    print(f"Adding new reservation {added_count} of {total_to_update}: {reservation_id}")
                    try:
                        new_row = self.process_single_reservation(reservation_id, None)
                        cleaned_row = self.clean_row_data(new_row)
                        if any(cleaned_row.values()):  # Only write non-empty rows
                            writer.writerow(cleaned_row)
                        else:
                            print(f"Warning: Empty data for new reservation {reservation_id}, skipping")
                            error_count += 1
                    except Exception as e:
                        print(f"Error processing new reservation {reservation_id}: {str(e)}")
                        error_count += 1

            # Write any remaining existing reservations that weren't in the missing_data set
            for reservation_id, row in existing_reservations.items():
                if reservation_id not in missing_data:
                    writer.writerow(self.clean_row_data(row))

        print(f"Update completed. Updated {updated_count} reservations, added {added_count} new reservations, "
            f"skipped {skipped_count} cancelled reservations, encountered {error_count} errors.")
        os.replace(self.temp_filename, self.csv_filename)

    def clean_row_data(self, row: Dict[str, str]) -> Dict[str, str]:
        cleaned_row = {}
        for field in self.csv_headers:
            if field in row:
                cleaned_row[field] = row[field]
            else:
                cleaned_row[field] = ""
        return cleaned_row

    def update_main_file(self, updated_row):
        with open(self.csv_filename, 'r') as file:
            rows = list(csv.DictReader(file))

        for i, row in enumerate(rows):
            if row['ReservationId'] == updated_row['ReservationId']:
                rows[i] = self.clean_row_data(updated_row)
                break

        with open(self.csv_filename, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=self.csv_headers)
            writer.writeheader()
            writer.writerows(rows)

    def update_csv_headers(self):
        temp_filename = 'temp_output.csv'
        headers_updated = False

        with open(self.csv_filename, 'r') as input_file, open(temp_filename, 'w', newline='') as output_file:
            reader = csv.reader(input_file)
            writer = csv.writer(output_file)

            # Read existing headers
            existing_headers = next(reader, None)

            if existing_headers != self.csv_headers:
                # Write new headers
                writer.writerow(self.csv_headers)
                headers_updated = True

                # Create a mapping from old to new header positions
                header_map = {header: i for i, header in enumerate(existing_headers)}

                # Write data rows
                for row in reader:
                    new_row = [''] * len(self.csv_headers)
                    for i, header in enumerate(self.csv_headers):
                        if header in header_map:
                            new_row[i] = row[header_map[header]]
                    writer.writerow(new_row)
            else:
                # If headers are already up to date, just write everything as is
                writer.writerow(existing_headers)
                for row in reader:
                    writer.writerow(row)

        if headers_updated:
            os.replace(temp_filename, self.csv_filename)
            print("Updated CSV headers to include new fields.")
        else:
            os.remove(temp_filename)
            print("CSV headers are already up to date.")

    def process_single_reservation(self, reservation_id: str, writer: csv.DictWriter, existing_data: Dict[str, str] = None) -> Dict[str, str]:
        self.search_reservation(reservation_id)
        if self.is_reservation_loaded(reservation_id):
            time.sleep(3)
            reservation_data = self.extract_reservation_data(reservation_id)
            
            if existing_data:
                for field in self.csv_headers:
                    if field not in existing_data or not existing_data[field]:
                        existing_data[field] = reservation_data.get(field, "")
                reservation_data = existing_data

            if (not existing_data or not existing_data.get('ItemizedBill')) and reservation_data.get('ResStatus') != "Cancelled":
                self.process_guest_bill(reservation_data)
            elif reservation_data.get('ResStatus') == "Cancelled":
                self.logger.info(f"Skipping guest bill processing for cancelled reservation {reservation_id}")

            if None in reservation_data:
                self.logger.warning(f"Warning: None key found in reservation_data for reservation {reservation_id}")
                del reservation_data[None]

            cleaned_data = {}
            for field in self.csv_headers:
                if field in reservation_data:
                    cleaned_data[field] = reservation_data[field]
                else:
                    self.logger.warning(f"Warning: Missing field '{field}' for reservation {reservation_id}")
                    cleaned_data[field] = ""

            if writer:
                try:
                    writer.writerow(cleaned_data)
                except ValueError as e:
                    self.logger.error(f"Error writing row for reservation {reservation_id}: {str(e)}")
                    self.logger.error(f"Reservation data: {cleaned_data}")
                    raise

            return cleaned_data
        return {field: "" for field in self.csv_headers}

    def search_reservation(self, reservation_id: str):
        search_input = self.selenium_helper.wait_for_element(By.XPATH, XPaths.SEARCH_INPUT)
        if search_input:
            search_input.clear()
            search_input.send_keys(reservation_id)
            search_input.send_keys(Keys.RETURN)
            time.sleep(4)
        else:
            self.logger.error("Failed to find search input")

    def is_reservation_loaded(self, reservation_id: str) -> bool:
        try:
            # Wait for either the reservation view or search results to load
            self.selenium_helper.wait_for_element(By.CLASS_NAME, "rms-portlet-caption", timeout=10)
            
            # Check if we're on the search results page
            search_results = self.selenium_helper.is_element_visible_by_dimensions(By.CLASS_NAME, "ReservationSearchScreen", timeout=1)
            
            if not search_results:
                print(f"Single Res Detected for ResID: {reservation_id}")
                # We're likely on a single reservation view
                res_id_element = self.selenium_helper.wait_for_element(By.CLASS_NAME, "res-screen-info-bar-resid")
                return res_id_element and reservation_id in res_id_element.text
            else:
                print(f"Search Results Detected for ResID: {reservation_id}")
                # We're on the search results page
                return self.handle_search_results(reservation_id)
        except TimeoutException:
            self.logger.error("Timeout waiting for page to load")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error in is_reservation_loaded: {str(e)}")
            return False

    def handle_search_results(self, reservation_id: str) -> bool:
        try:
            grid_container = self.selenium_helper.wait_until_stable(
                By.XPATH, '//*[@id="MainWindow"]/div/div/div[2]/div[2]/div/div[2]/div/div/div[2]/div',
                timeout=20
            )
            if not grid_container:
                self.logger.error("Failed to find stable grid container")
                return False

            rows = grid_container.find_elements(By.XPATH, './/div[contains(@class, "GridLiteRow")]')
            self.logger.info(f"Found {len(rows)} rows in search results")
            
            for row in rows:
                try:
                    # Find the anchor tag within the second column
                    anchor_xpath = './/div[contains(@class, "GridLiteColumn")][2]//a[@class="rms-a"]'
                    anchor = row.find_element(By.XPATH, anchor_xpath)
                    res_id_column = anchor.text.strip()
                    self.logger.info(f"Checking column: '{res_id_column}' against '{reservation_id}'")
                    if reservation_id in res_id_column:
                        self.logger.info(f"Found matching reservation: {reservation_id}")
                        # Click the anchor tag using wait_and_click
                        if self.selenium_helper.wait_and_click(By.XPATH, f"({anchor_xpath})[contains(text(), '{reservation_id}')]"):
                            # Wait for the reservation to load after clicking
                            return self.selenium_helper.wait_for_element(By.CLASS_NAME, "res-screen-info-bar-resid", timeout=10) is not None
                        else:
                            self.logger.error(f"Failed to click reservation {reservation_id}")
                            return False
                except StaleElementReferenceException:
                    self.logger.warning("Encountered stale element, continuing to next row")
                    continue
                except NoSuchElementException:
                    self.logger.warning(f"Could not find anchor tag for reservation {reservation_id}, continuing to next row")
                    continue
            
            self.logger.warning(f"Reservation {reservation_id} not found in search results")
            return False
        except TimeoutException:
            self.logger.error("Timeout while handling search results")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error in handle_search_results: {str(e)}")
            return False

    def extract_reservation_data(self, reservation_id):
        data = {"ReservationId": reservation_id}
        
        data["ArriveDate"] = self.selenium_helper.get_element_text(By.XPATH, '//*[@id="GridRow-Arrive"]/label')
        data["DepartDate"] = self.selenium_helper.get_element_text(By.XPATH, "//*[@id='GridRow-Depart']/label")
        data["ResStatus"] = self.selenium_helper.get_element_value(By.XPATH, "//*[@id='GridRow-Status']/input")
        data["LegacyResId"] = self.selenium_helper.get_element_value(By.XPATH, "//*[@id='GridRow-Spare10']/input")
        data["BaseRate"] = self.selenium_helper.get_element_value(By.XPATH, "//*[@id='GridRow-BaseTariff']/input")
        data["TotalRate"] = self.selenium_helper.get_element_value(By.XPATH, "//*[@id='GridRow-TotalTariff']/input")
        data["GuestBill"] = self.selenium_helper.get_element_value(By.XPATH, "//*[@id='GridRow-Acc_General']/input")
        data["ResNote"] = self.selenium_helper.get_element_value(By.ID, "ResNote")
        data["ItemizedBill"] = "" # gets populated in another function
        
        return data

    def process_guest_bill(self, reservation_data):
        try:
            guest_bill_link = self.selenium_helper.wait_for_element(By.XPATH, XPaths.GUEST_BILL_LINK)
            guest_bill_link.click()
            self.logger.info("Clicked on the guest bill link")
            time.sleep(3)

            accounts_data_grid = self.selenium_helper.wait_for_element(By.CLASS_NAME, "AccountsDataGrid")
            self.logger.info("Found the AccountsDataGrid")

            if self.remove_fees:
                self.guest_bill_manager.remove_fees(fees_to_remove)

            itemized_bill = self.extract_itemized_bill(accounts_data_grid)
            reservation_data["ItemizedBill"] = itemized_bill
        except TimeoutException:
            self.logger.error("Timeout while trying to process guest bill")
            reservation_data["ItemizedBill"] = "Failed to load guest bill"
        except Exception as e:
            self.logger.error(f"Error processing guest bill: {str(e)}")
            reservation_data["ItemizedBill"] = f"Error: {str(e)}"

        self.close_guest_bill_modal()

    def extract_itemized_bill(self, accounts_data_grid: WebElement):
        line_items = accounts_data_grid.find_element(By.XPATH, './/div[contains(@class, "GridLiteRowsContainer")]')
        rows = line_items.find_elements(By.XPATH, './/div[contains(@class, "GridLiteRow")]')
        itemized_bill = []

        for index, row in enumerate(rows):
            columns = row.find_elements(By.XPATH, './/div[contains(@class, "GridLiteColumn")]')
            if len(columns) >= 6:
                try:
                    date = self.selenium_helper.sanitize_text(columns[0].text)
                    description = self.selenium_helper.sanitize_text(columns[2].text)
                    debit = self.selenium_helper.sanitize_text(columns[3].text)
                    credit = self.selenium_helper.sanitize_text(columns[4].text)
                    balance = self.selenium_helper.sanitize_text(columns[5].text)

                    if date or description or debit or credit or balance:
                        item = f"{date} | {description} | Debit: {debit} | Credit: {credit} | Balance: {balance}"
                        itemized_bill.append(item)
                except Exception as e:
                    print(f"Error processing row {index + 1}: {str(e)}")

        print(f"Processed {len(itemized_bill)} items for the itemized bill")
        return " || ".join(itemized_bill)

    def close_guest_bill_modal(self):
        try:
            close_button = self.selenium_helper.wait_for_element(By.XPATH, XPaths.CLOSE_GUEST_BILL_MODAL)
            close_button.click()
        except TimeoutException:
            self.logger.error("Failed to find close button for guest bill modal")

def automate_process(username, password, csv_file_path, start_reservation_id, has_headers, update_mode, remove_fees, is_debug):
    logger = get_logger(__name__)
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=chrome_options)
    try:
        logger.info("Starting the automation process")
        if is_debug:
            globals.login_training_with_2fa_and_wait(driver, username, password)
        else:
            globals.login_with_2fa_and_wait(driver, username, password)
        
        selenium_helper = SeleniumHelper(driver)
        res_work = ResWork(driver, selenium_helper, remove_fees)
        
        if update_mode:
            res_work.update_missing_data(csv_file_path, start_reservation_id)
        else:
            res_work.process_reservations(csv_file_path, start_reservation_id, has_headers)

        logger.info("Process completed successfully")
        logger.info("Please verify the results.")
        input("Press Enter when you're done verifying...")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        logger.error("Traceback:")
        logger.error(traceback.format_exc())
    finally:
        driver.quit()
        logger.info("Script execution completed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RMS Cloud Reservation Processing Automation Script")
    parser.add_argument("username", help="Your RMS Cloud username")
    parser.add_argument("password", help="Your RMS Cloud password")
    parser.add_argument("csv_file", help="Path to the CSV file containing reservation IDs")
    parser.add_argument("--start", help="Reservation ID to start processing from")
    parser.add_argument("--headers", action="store_true", help="Specify if the source CSV file has headers")
    parser.add_argument("--update", action="store_true", help="Update mode: process only missing data")
    parser.add_argument("--removefees", action="store_true", help="Remove specified fees from guest bills")
    parser.add_argument("--debug", action="store_true", help="Runs in training")
    args = parser.parse_args()

    # Set these for use with --removefees arg
    # Uses Substring matching so be as specific as necessary
    fees_to_remove = ["Admin Fee", "Hotel Occupancy", "Resort Fee"]

    setup_logging("res_work")
    automate_process(args.username, args.password, args.csv_file, args.start, args.headers, args.update, args.removefees, args.debug)