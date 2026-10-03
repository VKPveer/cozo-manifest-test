# Task 05 - Extract Code Symbols


## Objective

Convert parsed code structure into a searchable
symbol index for AI coding agents.


## Input

code_structure.json


## Output

symbols.json


## Extracted Symbols


### Classes

Stores:

- Class name
- File reference


### Methods

Stores:

- Class name
- Method name
- Signature
- Parameters
- File
- Line start
- Line end


### Functions

Stores:

- Function name
- Signature
- Parameters
- File
- Line start
- Line end


## Example Use Case

AI agent can search:

"Where is create_user implemented?"

and locate:

Class:
UserService

Method:
create_user()

File:
sample.py


## Status

Completed ✅


Next Task:

Task 06 - Extract Imports & DependenciesClasses, methods, functions and signatures extraction will be added here.