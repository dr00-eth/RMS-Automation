# RMS Automations for Landstar Management

This project contains a set of automation scripts for RMS Cloud, designed to streamline various processes for Landstar Management.

## Table of Contents
1. [Installation](#installation)
2. [Project Structure](#project-structure)
3. [Scripts](#scripts)
   - [Attributes Processor](#attributes-processor)
   - [Site Order by Numeric](#site-order-by-numeric)
   - [Bulk Rate Delete](#bulk-rate-delete)
   - [Bulk Rate Table Re-assign](#bulk-rate-table-re-assign)
   - [Reservation Info Gather](#reservation-info-gather)
4. [Creating New Automations](#creating-new-automations)
5. [Troubleshooting](#troubleshooting)

## Installation

1. Clone this repository to your local machine.
2. Ensure you have Python 3.7+ installed.
3. Create a virtual environment:
   ```
   python -m venv venv
   ```
4. Activate the virtual environment:
   - On Windows: `venv\Scripts\activate`
   - On macOS and Linux: `source venv/bin/activate`
5. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Project Structure

- `includes/`: Contains helper classes and utility functions
  - `SeleniumHelper.py`: Helper functions for Selenium operations
  - `PropertyManager.py`: Manages property-related operations
  - `TaxManager.py`: Handles tax-related operations
  - `AttributeManager.py`: Manages attribute-related operations
  - `constants.py`: Stores project-wide constants
  - `logging_config.py`: Configures logging for all scripts
- `/`: Contains the main automation scripts
- `README.md`: This file
- `requirements.txt`: List of Python package dependencies

## Scripts

### Attributes Processor

Parses through all sites for a given property and adds/removes attributes to each site.

Usage:
```
python attributes_processor.py RMS_USERNAME RMS_PASSWORD "Property Name" [--start XXX]
```
- `--start`: Optional argument to start from a specific site number

### Site Order by Numeric

Orders site types by their numerical values rather than alphabetically.

Usage:
```
python site_order_by_numeric.py RMS_USERNAME RMS_PASSWORD
```

After sign-in, navigate to `Setup -> Site Type/Site Number`, select the property you want to order, and press Enter in the script terminal.

### Bulk Rate Delete

Used for bulk deletion of a given rate lookup.

Usage:
```
python bulk_rate_delete.py RMS_USERNAME RMS_PASSWORD
```

After sign-in, navigate to `Rate Manager`, select the correct property, open the `Rate Lookup` window, filter by the rate to be removed, then go back to the script terminal and press Enter.

### Bulk Rate Table Re-assign

Used for bulk rate reassignment of a given rate table between properties.

Usage:
```
python bulk_rate_table_reassign.py RMS_USERNAME RMS_PASSWORD PROPERTY_TO_SELECT PROPERTY_TO_REMOVE
```

Ensure `PROPERTY_TO_SELECT` and `PROPERTY_TO_REMOVE` match the exact property names in RMS Cloud.

### Reservation Info Gather

Gathers vital details and a snapshot of the Guest Bill for a list of reservation IDs.

Usage:
```
python res_work.py RMS_USERNAME RMS_PASSWORD path_to_input_csv.csv [--headers] [--update] [--start XXX] [--removefees] [--debug]
```
- `--headers`: Indicates header row in source CSV
- `--update`: Checks previous output for missing data and updates just those reservations
- `--start`: Takes in a reservation number to start from
- `--removefees`: Removes specified fees from guest bills
- `--debug`: Runs in training mode

## Creating New Automations

To create a new automation script, use the `automation_template.py` as a starting point. This template includes the basic structure and best practices for creating automations using this framework.

1. Copy `automation_template.py` and rename it to your new script name.
2. Modify the `AutomationTemplate` class to include your specific automation logic.
3. Update the `perform_action` and `process_data` methods with your automation steps.
4. Adjust the argument parser if you need additional command-line arguments.
5. Implement the `load_data_from_file` function if your automation requires input data.

## Troubleshooting

- If you encounter any issues with element locators, check the `constants.py` file and update the XPaths if necessary.
- For logging-related issues, refer to the `logging_config.py` file and ensure it's properly configured for your environment.
- If you're having trouble with a specific script, check the individual script's logging output for more detailed error messages.

For any other issues or questions, please contact the Drew.