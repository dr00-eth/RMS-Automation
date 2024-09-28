from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from includes.SeleniumHelper import SeleniumHelper
from includes.logging_config import get_logger
from includes import globals

class BaseAutomation:
    def __init__(self, username: str, password: str, debug: bool = False):
        self.username = username
        self.password = password
        self.debug = debug
        self.logger = get_logger(self.__class__.__name__)
        self.driver = None
        self.selenium_helper = None

    def setup(self):
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.selenium_helper = SeleniumHelper(self.driver)

    def login(self, isNewbook: bool = False):
        if isNewbook:
            globals.NB_login_with_2fa_and_wait(self.driver, self.username, self.password)
            return
        
        if self.debug:
            globals.RMS_login_training_with_2fa_and_wait(self.driver, self.username, self.password)
        else:
            globals.RMS_login_with_2fa_and_wait(self.driver, self.username, self.password)

    def navigate_to_page(self, url):
        self.driver.get(url)
        self.logger.info(f"Navigated to {url}")

    def run(self, isNewbook: bool = False):
        try:
            self.setup()
            self.login(isNewbook)
            self.perform_automation()
            self.logger.info("Process completed successfully")
            self.logger.info("Please verify the results.")
            input("Press Enter when you're done verifying...")
        except Exception as e:
            self.logger.error(f"An error occurred: {str(e)}")
        finally:
            if self.driver:
                self.driver.quit()
            self.logger.info("Script execution completed.")

    def perform_automation(self):
        # This method should be overridden by subclasses
        raise NotImplementedError("Subclasses must implement perform_automation method")