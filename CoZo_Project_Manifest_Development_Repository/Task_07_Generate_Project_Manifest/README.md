# Task 07 - Generate Project Manifest

## Objective

Generate a unified `project-manifest.json` by combining all extracted codebase information from previous tasks.

The manifest acts as a semantic index of the repository for AI-assisted coding, code discovery, and traceability.

---

# Input Sources

## Task 02 - Repository Scanner

Input:

`file_inventory.json`

Contains:

- File paths
- File names
- File extensions
- File size
- File hash
- Last modified information

---

## Task 03 - Language Detection

Input:

`language_updated_inventory.json`

Contains:

- Programming language information

Example:

```
app.py -> Python
```

---

## Task 04 - Code Parser

Input:

`code_structure.json`

Contains:

- Classes
- Methods
- Functions
- Parameters
- Method signatures
- Line locations

---

## Task 05 - Code Symbols

Input:

`symbols.json`

Contains:

- Class symbols
- Method symbols
- Function symbols
- File references
- Line start and end locations

---

## Task 06 - Dependencies

Input:

`dependencies.json`

Contains:

- Imports
- Internal dependencies
- External libraries
- Standard libraries

---

# Manifest Generation Flow

```
file_inventory.json
        +
language_updated_inventory.json
        +
code_structure.json
        +
symbols.json
        +
dependencies.json

        ↓

manifest_generator.py

        ↓

project-manifest.json
```

---

# Generated Output

Output file:

```
output/project-manifest.json
```

The generated manifest contains:

## Repository Metadata

Includes:

- Repository name
- Repository URL
- Branch
- Commit SHA
- Manifest generation timestamp

Repository-specific configuration is managed through:

```
config.json
```

---

## File Information

Each source file contains:

- File path
- File name
- Programming language
- File extension
- File type
- Metadata information

---

## Code Symbols

The manifest stores searchable code symbols.

Includes:

- Classes
- Methods
- Functions
- Method signatures
- Parameters
- Source file references
- Line locations

Example:

```
UserService

    |
    ├── create_user(self,name,email)
    |
    └── delete_user(self,user_id)
```

---

## Dependencies

The manifest stores dependency information.

Includes:

- Internal project dependencies
- External libraries
- Standard libraries

Example:

```
app.py

    |
    ├── sample_service.UserService
    |
    ├── pandas
    |
    └── os
```

---

# Traceability

Reserved for future mapping between business requirements and implementation artefacts.

Future mapping:

```
Project Goal

        ↓

Requirement

        ↓

User Story

        ↓

Task

        ↓

Code File

        ↓

Code Symbol
```

---

# Configuration

Repository information is maintained through:

```
config.json
```

Example:

```json
{
    "repository": {
        "name": "sample-project",
        "url": "",
        "branch": "main",
        "commit_sha": ""
    }
}
```

---

# Validation

Manifest validation is performed using:

```
manifest-schema.json
```

Validation flow:

```
project-manifest.json

        ↓

manifest-schema.json

        ↓

Validation Result
```

Successful validation:

```
✅ PROJECT MANIFEST IS VALID
```

---

# Task Status

Completed ✅

Implemented:

- Manifest generation
- Repository metadata support
- File information merge
- Language information merge
- Code symbol attachment
- Dependency attachment
- Schema validation

---

# Next Task

Task 08 - Add Git Repository Metadata
