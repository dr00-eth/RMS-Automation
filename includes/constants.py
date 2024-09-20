# URLs
LOGIN_URL = "https://app13.rmscloud.com/Login"
CATEGORY_URL = "https://app13.rmscloud.com/#!/Setup/Category"

# Client ID
CLIENT_ID = "19681"

# XPaths
class XPaths:
    # Login page
    CLIENT_ID_INPUT = ".clientId"
    USERNAME_INPUT = ".username"
    PASSWORD_INPUT = ".pw-field"
    LOGIN_BUTTON = "#Login"
    LOGIN_TRAINING_BUTTON = "#LoginTraining"

    # Category page
    MAIN_WINDOW = '//*[@id="MainWindow"]/div/div[2]/div/div/div[2]'
    CONTAINER = '//*[@id="MainWindow"]/div/div[2]/div/div/div[2]/div'

    # Display Order
    DISPLAY_ORDER_BUTTON = '//*[@id="MainWindow"]/div/div[1]/div[2]/a[1]'
    CATEGORY_DISPLAY_ORDER = '//*[@id="CategoryDisplayOrder"]/div[2]/div/div[1]/div/div[2]/div/div/div[2]/div'

    # Property
    PROPERTY_ADD_BUTTON = '/html/body/div[20]/div/div/div/div/div[2]/div/div/div[2]/div/div/div[1]/div/div[1]/div[2]/a[2]'
    PROPERTY_REMOVE_BUTTON = '/html/body/div[20]/div/div/div/div/div[2]/div/div/div[2]/div/div/div[2]/div/div[1]/div[1]/a[1]'

    # Rate Tables
    RATE_TABLE_GRID_CONTAINER = '/html/body/div[16]/div/div/div/div/div[2]/div/div/div[2]/div'
    EDIT_BUTTON = '/html/body/div[16]/div/div/div/div/div[1]/div[4]/div[4]'
    PROPERTIES_BUTTON = "//*[@id='RateTableTopSection']/div/div/div[1]/div[2]/a"
    ERROR_MODAL_OK_BUTTON = '//*[@id="ResWarningsWrapper"]/div[4]/div/div[1]'
    AVAILABLE_PROPERTIES = "/html/body/div[20]/div/div/div/div/div[2]/div/div/div[2]/div/div/div[1]/div/div[2]/div[2]/div/div[2]/div"
    SELECTED_PROPERTIES = "/html/body/div[20]/div/div/div/div/div[2]/div/div/div[2]/div/div/div[2]/div/div[2]/div/div/div[2]/div"
    CLOSE_PROPERTIES_MODAL = "/html/body/div[20]/div/div/div/div/div[1]/div/div[1]"
    SAVE_CHANGES = "/html/body/div[17]/div/div/div/div/div[1]/div[2]/div[4]"

    # Bulk Rate Delete
    BULK_RATE_GRID_CONTAINER = "/html/body/div[16]/div/div/div/div/div[2]/div/div/div[2]/div"
    BULK_RATE_DELETE_BUTTON = "/html/body/div[16]/div/div/div/div/div[1]/div[4]/div[4]"
    BULK_RATE_CONFIRM_DELETE = '//*[@id="ResWarningsWrapper"]/div[4]/div/div[2]'

    # Site Ordering
    MOVE_UP_BUTTON = '//*[@id="CategoryDisplayOrder"]/div[2]/div/div[1]/div/div[1]/div[2]/a[1]'
    MOVE_DOWN_BUTTON = '//*[@id="CategoryDisplayOrder"]/div[2]/div/div[1]/div/div[1]/div[2]/a[2]'

    # Search
    SEARCH_INPUT = '//*[@id="kt_quick_search_toggle"]/div/input'

    # Reservation
    RES_SCREEN_INFO_BAR = "res-screen-info-bar-resid"

    # Guest Bill Management
    CORRECTIONS_BUTTON = "//button[contains(@class, 'btn-success') and .//span[contains(text(), 'Corrections')]]"
    VOID_CHARGE_OPTION = "//a[.//span[text()='Void Charge']]"
    INCORRECT_ENTRY_ROW = ".//div[contains(@class, 'GridLiteRow') and contains(., 'Incorrect Entry')]"
    VOID_TRANSACTION_BUTTON = ".//a[contains(@class, 'btn-default') and .//span[text()='Void Transaction']]"
    GUEST_BILL_LINK = '//*[@id="AcctRows"]/div/div[1]/div[25]/label/a'
    CLOSE_GUEST_BILL_MODAL = '//*[@id="AccountsButtonsRow"]/a[13]'

# Timeouts
DEFAULT_TIMEOUT = 10
LONG_TIMEOUT = 20

# Retry settings
MAX_RETRIES = 3
RETRY_DELAY = 1