# TAF File Updater for Trumpf CNC Laser Cutters

## Purpose

This program automates the process of updating .TAF files used by Trumpf CNC laser cutters. These files contain a list of parts (stored in .GEO files) and their locations on a sheet of metal, known as a nest. When the name of a .GEO file changes due to part revisions, the associated .TAF files need to be updated to reflect these changes. Traditionally, this is a time-consuming manual process. This program aims to streamline the updating process, saving hours of manual work by automatically finding and updating the paths of .GEO files in .TAF files.

## Features

- **Update all .TAF files** in a directory that contains a matching .GEO file based on the user's request.
- **Selective updating** of specific .TAF files to new revisions.
- **Configuration file support** to get TAF and GEO directories on startup.
- **Logging** of all modified files for easy tracking.
- **Validation** to ensure a .GEO file with the requested revision exists, with user confirmation for unmatched files.
- **Support for design and production parts**, handling both numerical and alphabetical revision formats and allowing conversion between these formats.
- **Part type support** for HEX, CAB, ELB with a specific part number structure.
- **Optional features** include targeted part number replacement in specific files and backup storage for modified TAF files, linked to log entries.

## Modules Required

This program utilizes Python standard libraries including `re`, `os`, `shutil`, and `datetime` for its functionality. The main modules include:

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

## Testing

It is recommended to test the program in an enclosed environment before deploying it on a full database to ensure compatibility and to prevent any unintended data loss.
