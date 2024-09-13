# RMS Automations for Landstar Management

Using VS Code, create a venv and install the packages from requirements.txt
## Includes Structure
 - SeleniumHelper contains browser automation helper functions
 - PropertyManager contains helper functions for interacting with Property assignment grids
 - TaxManager is used for adjusting Site Type "Accounting" items
 - SiteProcessor is used for iterating over Sites in the Site Type/Site Number grid
 - AttributeManager is used for interacting with the Site Type Attributes tab.

## Attributes Processor
This script parses through all sites for a given property and has the ability to add/remove attributes to each site. As it goes it will log attribute exceptions (attributes assigned to a given site that were NOT defined in the list of ones that were to be allocated) to a file.

Usage: `python attributes_processor.py RMS_UNAME RMS_PWD "Property Name" (optional: --start XXX)`
Property Name argument **MUST** match exactly what is displayed in the RMS property dropdown. Use the optional `--start` argument to jump to a site number higher than 1
After sign-in, wait to clear trust date pop-up and go back to script terminal and press enter.

## Site Order by Numeric
This script is used for ordering site types by their numerical values rather than alphabetically

Usage: `python site_order_by_numeric.py RMS_UNAME RMS_PWD`
After sign-in, navigate to `Setup -> Site Type/Site Number`, select the property you want to order and go back to the script terminal and press enter.

## Bulk Rate Delete
This script is not used often, but if there is a need to bulk delete a given rate lookup you can use this.

Usage `python bulk_rate_delete.py RMS_UNAME RMS_PWD`
After sign-in, navigate to `Rate Manager`, select the correct property, open the `Rate Lookup` window, filter by the rate to be removed, then go back to the script terminal and press enter.

## Bulk Rate Table Re-assign
This script is not used often, but if there is a need to bulk rate re-assignement of a given rate table between properties you can use this.

Usage FIRST UPDATE `property_to_select` & `property_to_select` to match the EXACT property names, then: `python bulk_rate_table_reassign.py RMS_UNAME RMS_PWD`
After sign-in, navigate to `Rate Manager`, select the correct property, open the `Rate Tables` window, filter by the property & rate name to be moved, then go back to the script terminal and press enter.

## Reservation Info Gather
This script takes a CSV list, with or without column header (use: `--header`), of RMS reservation IDs and gathers vital details and a snapshot of the Guest Bill.

Usage `python res_work.py RMS_UNAME RMS_PWD path_to_input_csv.csv (optional: --headers, --update, --start XXX)`
- `--headers` indicates header row in source CSV
- `--update` checks previous output for missing data and updates just those reservations
- `--start` takes in a reservation number to start from

## Automation Template
This is a boilerplate to speed up the process of creating new automations. Just create a copy for a given task and insert logic functions in the placeholder.