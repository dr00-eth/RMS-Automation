# RMS Automations for Landstar Management

This project contains a set of automation scripts for RMS Cloud and Newbook, designed to streamline various processes for Landstar Management.

## Table of Contents
1. [Installation](#installation)
2. [Project Structure](#project-structure)
3. [Scripts](#scripts)
   - [Attributes Processor](#attributes-processor)
   - [Bulk Rate Delete](#bulk-rate-delete)
   - [Bulk Rate Table Re-assign](#bulk-rate-table-re-assign)
   - [Site Order by Numeric](#site-order-by-numeric)
   - [Tax Processor](#tax-processor)
   - [Reservation Info Gather](#reservation-info-gather)
   - [Newbook Reservation Dump](#newbook-reservation-dump)
   - [Threaded Newbook Reservation Dump](#threaded-newbook-reservation-dump)
4. [Utility Scripts](#utility-scripts)
5. [Creating New Automations](#creating-new-automations)
6. [Troubleshooting](#troubleshooting)

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
  - `SiteProcessor.py`: Processes individual sites
  - `constants.py`: Stores project-wide constants
  - `logging_config.py`: Configures logging for all scripts
  - `BaseAutomation.py`: Base class for all automation scripts
  - `BaseManager.py`: Base class for manager classes
  - `argument_parser_utility.py`: Utility functions for parsing command-line arguments
  - `decorators.py`: Contains custom decorators
  - `globals.py`: Global functions and variables
- `/`: Contains the main automation scripts
- `README.md`: This file
- `requirements.txt`: List of Python package dependencies

## Scripts

### Attributes Processor

Parses through all sites for a given property and adds/removes attributes to each site.

Usage:
```
python attributes_processor.py RMS_USERNAME RMS_PASSWORD "Property Name" [--start XXX] [--debug]
```

### Bulk Rate Delete

Used for bulk deletion of a given rate lookup.

Usage:
```
python bulk_rate_delete.py RMS_USERNAME RMS_PASSWORD [--debug]
```

### Bulk Rate Table Re-assign

Used for bulk rate reassignment of a given rate table between properties.

Usage:
```
python bulk_rate_table_reassign.py RMS_USERNAME RMS_PASSWORD PROPERTY_TO_SELECT PROPERTY_TO_REMOVE [--debug]
```

### Site Order by Numeric

Orders site types by their numerical values rather than alphabetically.

Usage:
```
python site_order_by_numeric.py RMS_USERNAME RMS_PASSWORD [--debug]
```

### Tax Processor

Processes taxes for all sites of a given property.

Usage:
```
python tax_processor.py RMS_USERNAME RMS_PASSWORD "Property Name" [--start XXX] [--debug]
```

### Reservation Info Gather

Gathers vital details and a snapshot of the Guest Bill for a list of reservation IDs.

Usage:
```
python res_work.py RMS_USERNAME RMS_PASSWORD path_to_input_csv.csv [--headers] [--update] [--start XXX] [--removefees] [--removejournal] [--debug]
```

### Newbook Reservation Dump

Extracts reservation data from Newbook.

Usage:
```
python newbook_res.py RMS_USERNAME RMS_PASSWORD path_to_input_csv.csv [--start XXX] [--debug]
```

### Threaded Newbook Reservation Dump

A multi-threaded version of the Newbook Reservation Dump for improved performance.

Usage:
```
python threaded_newbook_res.py RMS_USERNAME RMS_PASSWORD path_to_input_csv.csv [--start XXX] [--threads N] [--debug]
```

## Utility Scripts

- `create_embedded_viewer.py`: Creates an embedded viewer for booking data.
- `automation_template.py`: Template for creating new automation scripts.

## Creating New Automations

To create a new automation script:

1. Copy `automation_template.py` and rename it to your new script name.
2. Modify the new class (inheriting from `BaseAutomation`) to include your specific automation logic.
3. Implement the `perform_automation` method with your automation steps.
4. Update the argument parser if you need additional command-line arguments.
5. Implement any additional methods needed for your specific automation tasks.

## Troubleshooting

- If you encounter any issues with element locators, check the `constants.py` file and update the XPaths if necessary.
- For logging-related issues, refer to the `logging_config.py` file and ensure it's properly configured for your environment.
- If you're having trouble with a specific script, check the individual script's logging output for more detailed error messages.
- When creating new automations, ensure you're properly inheriting from the `BaseAutomation` class and implementing the `perform_automation` method.

For any other issues or questions, please contact the [Drew Meyer](mailto:andrewmeyer23@gmail.com)