import csv
import os
import queue
import time
from typing import List, Dict
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException
from includes.logging_config import setup_logging, get_logger
from includes.constants import DEFAULT_TIMEOUT, NB_RESERVATION_URL
from includes.BaseAutomation import BaseAutomation
from includes.SeleniumHelper import SeleniumHelper
from includes.argument_parser_utility import create_base_parser
import includes.globals as globals

class ThreadedNewbookResDump(BaseAutomation):
    def __init__(self, username: str, password: str, data: List[str], num_tabs: int = 5, 
                 start_reservation_id: str = None, debug: bool = False, batch_size: int = 10):
        super().__init__(username, password, debug)
        self.logger = get_logger('ThreadedNewbookResDump')
        self.data = data
        self.num_tabs = num_tabs
        self.start_reservation_id = start_reservation_id
        self.output_csv = "newbook_co_res_dump_threaded.csv"
        self.bookings_folder = "bookings"
        self.work_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self.batch_size = batch_size

    def setup(self):
        options = Options()
        if not self.debug:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=options)
        self.selenium_helper = SeleniumHelper(self.driver)

        if not os.path.exists(self.bookings_folder):
            os.makedirs(self.bookings_folder)

        if self.start_reservation_id and os.path.exists(self.output_csv):
            self.logger.info(f"Resuming from reservation ID: {self.start_reservation_id}")
        else:
            self.write_csv_header()

    def perform_automation(self):
        self.login(isNewbook=True)
        self.populate_work_queue()
        self.process_reservations()
        self.process_results()

    def login(self, isNewbook: bool = True):
        if isNewbook:
            globals.NB_login_nopause(self.driver, self.username, self.password)
            self.logger.info("Main thread logged in successfully.")
        else:
            super().login(isNewbook)

    def write_csv_header(self):
        with open(self.output_csv, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["ReservationID", "BillingInfo"])

    def populate_work_queue(self):
        start_processing = self.start_reservation_id is None
        for reservation_id in self.data:
            if self.start_reservation_id and reservation_id == self.start_reservation_id:
                start_processing = True
            if start_processing:
                self.work_queue.put(reservation_id)

    def process_reservations(self):
        window_handles = self.open_tabs()
        tab_to_reservation: Dict[str, str] = {}
        processed_count = 0
        
        while not self.work_queue.empty() or tab_to_reservation:
            # Fill empty tabs
            for handle in window_handles:
                if handle not in tab_to_reservation and not self.work_queue.empty():
                    reservation_id = self.work_queue.get()
                    self.driver.switch_to.window(handle)
                    url = f"{NB_RESERVATION_URL}{reservation_id}"
                    self.driver.get(url)
                    tab_to_reservation[handle] = reservation_id

            # Process loaded tabs
            for handle in list(tab_to_reservation.keys()):
                reservation_id = tab_to_reservation[handle]
                self.driver.switch_to.window(handle)
                if self.is_page_loaded():
                    self.process_loaded_reservation(reservation_id)
                    del tab_to_reservation[handle]
                    processed_count += 1

                    # Write results to CSV in batches
                    if processed_count % self.batch_size == 0:
                        self.write_results_to_csv()
                    
            time.sleep(0.5)  # Small delay to prevent excessive CPU usage

        # Write any remaining results
        self.write_results_to_csv()

    def open_tabs(self):
        for _ in range(self.num_tabs - 1):
            self.driver.execute_script("window.open('about:blank', '_blank');")
        return self.driver.window_handles

    def is_page_loaded(self):
        try:
            return self.selenium_helper.wait_for_element(By.XPATH, "//th[contains(text(), 'Booking Billing')]", timeout=0.1)
        except TimeoutException:
            return False

    def process_loaded_reservation(self, reservation_id: str):
        try:
            self.logger.info(f"Processing reservation: {reservation_id}")
            table = self.find_booking_billing_table()
            if table:
                billing_info = self.extract_billing_info(table)
                self.save_table_html(table, reservation_id)
                self.result_queue.put((reservation_id, billing_info))
            else:
                self.logger.warning(f"Booking billing table not found for reservation: {reservation_id}")
                self.result_queue.put((reservation_id, "Table not found"))
        except Exception as e:
            self.logger.error(f"Error processing reservation {reservation_id}: {str(e)}")
            self.result_queue.put((reservation_id, f"Error: {str(e)}"))

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

    def extract_billing_info(self, table):
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
        current_url = self.driver.current_url
        file_path = os.path.join(self.bookings_folder, f"{reservation_id}.html")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"<!-- URL: {current_url} -->\n")
            f.write(f"<!-- Reservation ID: {reservation_id} -->\n")
            f.write(html_content)
        self.logger.info(f"Saved HTML for reservation {reservation_id}")

    def process_results(self):
        with open(self.output_csv, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            while not self.result_queue.empty():
                reservation_id, billing_info = self.result_queue.get()
                writer.writerow([reservation_id, billing_info])

    def write_results_to_csv(self):
        with open(self.output_csv, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            while not self.result_queue.empty():
                reservation_id, billing_info = self.result_queue.get()
                writer.writerow([reservation_id, billing_info])
        self.logger.info(f"Wrote batch of results to CSV")

    def run(self, isNewbook: bool = True):
        try:
            self.setup()
            self.perform_automation()
            self.logger.info("Process completed successfully")
            self.logger.info("Please verify the results.")
        except Exception as e:
            self.logger.error(f"An error occurred: {str(e)}")
        finally:
            if self.driver:
                self.driver.quit()
            self.logger.info("Script execution completed.")

def load_reservation_ids(file_path: str) -> List[str]:
    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        return [row[0] for row in reader if row]

def main():
    parser = create_base_parser("Threaded Newbook Reservation Dump Automation Script")
    parser.add_argument("csv_file", help="Path to the CSV file containing reservation IDs")
    parser.add_argument("--start", help="Reservation ID to start processing from")
    parser.add_argument("--threads", type=int, default=5, help="Number of threads to use")
    args = parser.parse_args()

    logger = setup_logging("newbook_res_dump_threaded")

    reservation_ids = load_reservation_ids(args.csv_file)
    automation = ThreadedNewbookResDump(args.username, args.password, reservation_ids, 
                                        num_tabs=args.threads, start_reservation_id=args.start, 
                                        debug=args.debug, batch_size=20)
    automation.run(isNewbook=True)

if __name__ == "__main__":
    main()