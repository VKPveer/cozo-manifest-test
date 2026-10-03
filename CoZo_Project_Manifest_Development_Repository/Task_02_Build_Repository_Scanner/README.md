# Task 02 - Build Repository Scanner


## Objective

Create a Python based repository scanner that reads a codebase
and creates a structured file inventory.


## Implemented Features


### Repository Scanning

- Recursively scans project folders
- Detects source files


### Configuration

Supports:

- Ignored folders
- Supported file extensions


### File Metadata Extraction

Extracts:

- File path
- File name
- Extension
- File type
- File size
- SHA256 hash
- Last modified timestamp


### Source Content Extraction

Reads source file content for future parsing.


## Output

Generated file:

output/file_inventory.json


Example flow:

Repository
    ↓
Scanner
    ↓
File Inventory JSON


## Status

Completed ✅


Next Task:

Task 03 - Implement Language Detection