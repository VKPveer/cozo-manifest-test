# Task 06 - Extract Imports & Dependencies


## Objective

Extract source code imports and create a dependency model
for understanding relationships between code components.


## Input

Python source files.

Example:

input/source_files/app.py


## Extracted Information

The extractor identifies:

- Imported modules
- From-import dependencies
- Dependency categories


## Dependency Categories


### Internal

Project source code dependencies.

Example:

sample_service.UserService


### External

Third-party packages.

Example:

pandas


### Standard Library

Python built-in modules.

Example:

os


## Output

Generated file:

output/dependencies.json


## Example Flow

Source Code

    ↓

AST Import Parser

    ↓

Dependency Model


## Status

Completed ✅


Next Task:

Task 07 - Generate Project Manifest