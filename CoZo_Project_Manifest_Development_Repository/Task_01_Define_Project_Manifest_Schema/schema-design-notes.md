# Project Manifest Schema Design

## Purpose

project-manifest.json will provide a machine-readable
index of the complete codebase.

The manifest will help AI coding agents understand:

- Existing files
- Existing classes
- Existing methods
- Existing dependencies
- Relationship with CoZo Requirements, Stories and Tasks


## Main Sections

1. Repository Information

Contains:
- Repository name
- Repository URL
- Branch
- Commit SHA


2. File Information

Contains:
- File path
- File type
- Programming language


3. Code Structure

Contains:
- Classes
- Functions
- Methods
- Method signatures
- Parameters
- Return types


4. Dependency Information

Contains:
- Imports
- External libraries
- Internal dependencies


5. Traceability Information

Contains:

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
Method


## Future Extensions

Possible additions:

- Test mapping
- API endpoints
- Database objects
- Pipeline references
- Agent execution history