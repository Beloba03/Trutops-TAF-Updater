# TAF File Updater for Trumpf CNC Laser Cutters

## Purpose

This program automates the process of updating .TAF files used by Trumpf CNC laser cutters. These files contain a list of parts (stored in .GEO files) and their locations on a sheet of metal, known as a nest. When the name of a .GEO file changes due to part revisions, the associated .TAF files need to be updated to reflect these changes. This is a time-consuming manual process. This program aims to speed up the updating process, saving hours of manual work by automatically finding and updating the paths of .GEO files in .TAF files.

## Project video

The project video is accesible at the following link:
https://drive.google.com/file/d/1WFt3TDTAFl8Jq0j9CZuuLbqSYM-E8JTE/view?usp=sharing

## Features

- **Update all .TAF files** in a directory that contains a matching .GEO file based on the user's request.
- **Selective updating** of specific .TAF files to new revisions.
- **Configuration file support** to get TAF and GEO directories on startup.
- **Logging** of all modified files for easy tracking.
- **Validation** to ensure a .GEO file with the requested revision exists, with user confirmation for unmatched files.
- **Support for design and production parts**, handling both numerical and lettered revision formats and allowing transition between these formats.
- **Part type support** for HEX, CAB, ELB with a specific part number structure.
- **Optional features** include part number replacement in specific TAFs and backup storage for modified TAF files, linked to log entries.

## Modules Required

This program utilizes Python standard libraries including `re`, `os`, `shutil`, and `datetime`. The main modules include:

- `main.py`
- `file_handling.py`

## Setup

### Prerequisites

- Python 3.11.7 or newer. Tested on both Unix and Windows OS environments.
- Configuration: Directories for GEO, TAF, and backups must be specified in the `config.txt` file.

### Installation

1. Ensure Python 3.11.7 or newer is installed on your system.
2. Clone this repository or download the source code.
3. Update the `config.txt` file with the paths to your GEO, TAF, and backup directories.

### Usage

Run `main.py` to start the program. Follow the on-screen prompts to specify the .GEO file revisions and the .TAF files you wish to update. The program will automatically update the .TAF files based on your input and log all changes.
It is recommended to test the program in an enclosed environment before deploying it on a full database to ensure compatibility and to prevent any data loss.

## Testing and Troubleshooting

This section outlines various test cases and their expected outcomes, helping users to troubleshoot common issues they might encounter.

For peer evaluation testing the files Example.TAF, Example2.TAF, and Example3.TAF (in the directory TEST_TAFS) have GEO files provided in the TEST_GEOS directory.

### Tested Scenarios

1. **Missing Configuration File**
   
   - **Test Case:** Run the program without a `config.txt` file present in the directory.
   - **Expected Outcome:** Error message: "The configuration file config.txt was not found."

2. **Missing Lines in Configuration**
   
   - **Test Case:** Remove or corrupt the `BACKUP_DIR` line in the `config.txt` file.
   - **Expected Outcome:** Error message: "BACKUP_DIR configuration not found or is invalid in the configuration file."

3. **Missing GEO Files**
   
   - **Test Case:** Specify a .GEO file in the update request that does not exist in the GEO directory.
   - **Expected Outcome:** Prompt: "The GEO does not exist, are you sure you want to update? (Y/N):"

4. **Invalid GEO and/or TAF Directory**
   
   - **Test Case:** Misconfigure the GEO directory path in `config.txt` to a non-existent location.
   - **Expected Outcome:** Error message: "The GEO directory /Users/benb/Python for Engineers/Python GEO TAF/GdEO was not found."

5. **Missing Backup Directory**
   
   - **Test Case:** Do not create a backup directory before running the program.
   - **Expected Outcome:** If `BACKUP_DIR` is specified but does not exist, the program will create the new directory and proceed with the operations.

6. **Wrong TAF File Specified**
   
   - **Test Case:** Specify a .TAF file for updating that does not exist or is not found in the specified TAF directory.
   - **Expected Outcome:** Error message: "TAF file not found."

### General Troubleshooting

- Ensure that the `config.txt` file is correctly formatted and located in the expected directory.
- Verify that all paths specified in the `config.txt` file are correct and accessible.
- Double-check the names and revisions of .GEO files to ensure they match your requirements before attempting to update .TAF files.
- For any unexpected behavior or errors, reviewing the log files may provide additional insights into what went wrong.

### Contact Info

If you have any questions feel free to contact me at ben.babineau@dal.ca!