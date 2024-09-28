import csv
import os
from typing import List, Dict
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException, WebDriverException
from includes.logging_config import setup_logging
from includes.constants import DEFAULT_TIMEOUT, NB_RESERVATION_URL
from includes.BaseAutomation import BaseAutomation
from includes.argument_parser_utility import create_base_parser

class NewbookResDump(BaseAutomation):
    def __init__(self, username: str, password: str, data: List[str], start_reservation_id: str = None, debug: bool = False):
        super().__init__(username, password, debug)
        self.data = data
        self.start_reservation_id = start_reservation_id
        self.output_csv = "newbook_co_res_dump.csv"
        self.bookings_folder = "bookings"

    def setup(self):
        super().setup()
        if not os.path.exists(self.bookings_folder):
            os.makedirs(self.bookings_folder)

        if self.start_reservation_id and os.path.exists(self.output_csv):
            self.logger.info(f"Resuming from reservation ID: {self.start_reservation_id}")
        else:
            with open(self.output_csv, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["ReservationID", "BillingInfo"])

    def perform_automation(self):
        self.process_reservations()

    def process_reservations(self):
        start_processing = self.start_reservation_id is None
        for reservation_id in self.data:
            if self.start_reservation_id and reservation_id == self.start_reservation_id:
                start_processing = True
            
            if start_processing:
                self.logger.info(f"Processing reservation: {reservation_id}")
                url = f"{NB_RESERVATION_URL}{reservation_id}"
                
                try:
                    self.selenium_helper.driver.get(url)
                    self.selenium_helper.wait_for_page_load()
                    self.handle_locked_session_dialog()
                    
                    table = self.find_booking_billing_table()
                    if table:
                        billing_info = self.extract_billing_info(table)
                        self.write_to_csv(reservation_id, billing_info)
                        self.save_table_html(table, reservation_id)
                    else:
                        self.logger.warning(f"Booking billing table not found for reservation: {reservation_id}")
                        self.write_to_csv(reservation_id, "Table not found")
                except WebDriverException as e:
                    self.logger.error(f"WebDriver error for reservation {reservation_id}: {str(e)}")
                    self.write_to_csv(reservation_id, f"Error: {str(e)}")
                except Exception as e:
                    self.logger.error(f"Error processing reservation {reservation_id}: {str(e)}")
                    self.write_to_csv(reservation_id, f"Error: {str(e)}")
            else:
                self.logger.info(f"Skipping reservation: {reservation_id}")

    def handle_locked_session_dialog(self):
        try:
            dialog = self.selenium_helper.wait_for_element(By.ID, "locked_session_dialog", timeout=1, _retry_tries=1, _retry_delay=0)
            if dialog:
                self.logger.info("Locked session dialog detected. Handling...")
                self.selenium_helper.wait_for_element(By.ID, "password").send_keys(self.password)
                self.selenium_helper.wait_and_click(By.CLASS_NAME, "confirm_button")
                self.selenium_helper.wait_for_invisibility(By.ID, "locked_session_dialog")
                self.logger.info("Locked session dialog handled successfully.")
        except TimeoutException:
            # Dialog not found, no action needed
            pass

    def find_booking_billing_table(self):
        try:
            th_element = self.selenium_helper.wait_for_element(
                By.XPATH, "//th[contains(text(), 'Booking Billing')]", 
                timeout=DEFAULT_TIMEOUT
            )
            return th_element.find_element(By.XPATH, "./ancestor::table")
        except Exception as e:
            self.logger.error(f"Error finding booking billing table: {str(e)}")
            return None

    def extract_billing_info(self, table: WebElement):
        rows = table.find_elements(By.XPATH, ".//tbody/tr")
        footer = table.find_elements(By.XPATH, ".//tfoot/tr/td")

        billing_info = []
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 3:
                key = cells[1].text.strip()
                value = cells[2].text.strip()
                billing_info.append(f"{key}:{value}")

        if len(footer) >= 2:
            billing_info.append(f"{footer[0].text.strip()}:{footer[1].text.strip()}")

        return " | ".join(billing_info)

    def save_table_html(self, table, reservation_id):
        html_content = table.get_attribute('outerHTML')
        file_path = os.path.join(self.bookings_folder, f"{reservation_id}.html")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        self.logger.info(f"Saved HTML for reservation {reservation_id}")

    def write_to_csv(self, reservation_id, billing_info):
        with open(self.output_csv, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([reservation_id, billing_info])

def load_reservation_ids(file_path: str) -> List[str]:
    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        return [row[0] for row in reader if row]

def main():
    parser = create_base_parser("Newbook Reservation Dump Automation Script")
    parser.add_argument("csv_file", help="Path to the CSV file containing reservation IDs")
    parser.add_argument("--start", help="Reservation ID to start processing from")
    args = parser.parse_args()

    setup_logging("newbook_res_dump")

    reservation_ids = load_reservation_ids(args.csv_file)
    automation = NewbookResDump(args.username, args.password, reservation_ids, args.start, args.debug)
    automation.run(isNewbook=True)

if __name__ == "__main__":
    main()