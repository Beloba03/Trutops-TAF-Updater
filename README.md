# TAF File Updater for Trumpf CNC Laser Cutters

## Purpose

This program automates the process of updating .TAF files used by Trumpf CNC laser cutters. These files contain a list of parts (stored in .GEO files) and their locations on a sheet of metal, known as a nest. When the name of a .GEO file changes due to part revisions, the associated .TAF files need to be updated to reflect these changes. This is a time-consuming manual process. This program aims to speed up the updating process, saving hours of manual work by automatically finding and updating the paths of .GEO files in .TAF files. The program also contains teh ability to search PDF files for specific parts and validate PDF files with the corresponding TAF file.


## Features

- **Update all .TAF files** in a directory that contains a matching .GEO file based on the user's request.
- **Selective updating** of specific .TAF files to new revisions.
- **Configuration file support** to get TAF and GEO directories on startup.
- **Logging** of all modified files for easy tracking.
- **Validation** to ensure a .GEO file with the requested revision exists, with user confirmation for unmatched files.
- **Support for design and production parts**, handling both numerical and lettered revision formats and allowing transition between these formats.
- **Part type support** for HEX, CAB, ELB with a specific part number structure.
- **PDF search** to make looking for programs containing specific parts easier
- **PDF/program validation** to make sure that programs are made for the latest version of TAF files

## Modules Required

This program utilizes Python standard libraries including `re`, `os`, `shutil`, `Tkinter`, `Multiprocessing`, and `datetime`. The main modules include:

- `main_tkinter.py`
- `file_handling.py`
- `PDF_module.py`
- `pdf_taf_checker.py`

## Setup

### Prerequisites

- Python 3.11.7 or newer.
- Windows
- PyMuPDF 1.24.1 or newer.
- Configuration: Directories for GEO, TAF, and backups must be specified in the `config.txt` file.

### Installation

1. Ensure Python 3.11.7 or newer is installed on your system.
2. Clone this repository or download the source code.
3. Update the `config.txt` file with the paths to your GEO, TAF, and backup directories.

### Usage

**If running from `.exe`:** Run `main_tkinter.exe` (may need administrative privileges). On first launch select the appropriate directories.

**If running from `.py`:** Run `main_tkinter.py` to start the program. Use the Tkinter GUI to interact with the program. On first launch select the appropriate directories.


## Testing and Troubleshooting

This section outlines various test cases and their expected outcomes, helping users to troubleshoot common issues they might encounter.

For peer evaluation testing the files Example.TAF, Example2.TAF, and Example3.TAF (in the directory TEST_TAFS) have GEO files provided in the TEST_GEOS directory.

### Tested Scenarios

1. **Missing Configuration File**
   
   - **Test Case:** Run the program without a `config.txt` file present in the directory.
   - **Expected Outcome:** Error message: "Config file created at "directory"", New config.txt file will be created at "directory"

2. **Missing Lines in Configuration**
   
   - **Test Case:** Remove or corrupt the `BACKUP_DIR` line in the `config.txt` file.
   - **Expected Outcome:** Error message: "BACKUP_DIR configuration not found or is invalid in the configuration file."

3. **Missing GEO Files**
   
   - **Test Case:** Specify a .GEO file in the update request that does not exist in the GEO directory.
   - **Expected Outcome:** Prompt: "The GEO does not exist, are you sure you want to update? (Y/N):"

4. **Invalid GEO, TAF, TMT, or BACKUP Directory**
   
   - **Test Case:** Misconfigure the GEO directory path in `config.txt` to a non-existent location.
   - **Expected Outcome:** Error message: "The GEO directory /Users/benb/Python for Engineers/Python GEO TAF/GdEO was not found."

5. **Missing Backup Directory**
   
   - **Test Case:** Do not create a backup directory before running the program.
   - **Expected Outcome:** If `BACKUP_DIR` is specified but does not exist, the program will create the new directory and proceed with the operations.

6. **Wrong TAF File Specified**
   
   - **Test Case:** Specify a .TAF file for updating that does not exist or is not found in the specified TAF directory.
   - **Expected Outcome:** Error message: "TAF file not found."

7. **PDF has no TAF with same name**
   
   - **Test Case:** Specify a .PDF file for a revision check with no TAF that has the same name.
   - **Expected Outcome:** Error message: "TAF file not found."

### General Troubleshooting

- Ensure that the `config.txt` file is correctly formatted and located in the expected directory.
- Verify that all paths specified in the `config.txt` file are correct and accessible.
- Double-check the names and revisions of .GEO files to ensure they match your requirements before attempting to update .TAF files.
- For any unexpected behavior or errors, reviewing the log files may provide additional insights into what went wrong.

### Contact Info

If you have any questions feel free to contact me at ben.babineau@dal.ca!
