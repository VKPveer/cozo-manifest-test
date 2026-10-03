# Task 04 - Implement Code Parser


## Objective

Parse Python source code and convert it into
structured code information for the project manifest.


## Implemented Features


### AST Parsing

Uses Python AST module to understand source code.


### Code Extraction

Extracts:

- Classes
- Methods
- Functions
- Parameters
- Method signatures


## Input

Python source file:

test_code/sample.py


## Output

Generated:

output/code_structure.json


Example:

Class:

UserService


Methods:

- create_user(self,name,email)
- delete_user(self,user_id)


Functions:

- helper_function()


## Status

Completed ✅


Next Task:

Task 05 - Extract Code Symbols