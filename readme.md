# RMS Automations for Landstar Management

Using VS Code, create a venv and install the packages from requirements.txt
## Recommendations:
- Utilize `includes\constants.py` to store strings and other values that are likely to be used across scripts
- Utilize `includes\globals.py` for any generic functions
- Utilize `includes\helpers.py` for more specific functions related to each script to help keep things readable

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

## Automation Template
This is a boilerplate to speed up the process of creating new automations. Just create a copy for a given task and insert logic functions in the placeholder.