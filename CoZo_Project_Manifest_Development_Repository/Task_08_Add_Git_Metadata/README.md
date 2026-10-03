# Task 08 - Add Git Repository Metadata

## Objective

Extract Git repository metadata automatically and make it
available to the generated project manifest.

This prevents branch names, commit SHAs, and repository
information from being manually maintained in the manifest.


---

## Git Metadata Extracted

The Git metadata extractor identifies:

- Repository name
- Repository root
- Remote repository URL
- Current branch
- Current commit SHA
- Metadata generation timestamp


---

## Git Commands Used

Repository root:

git rev-parse --show-toplevel

Current branch:

git branch --show-current

Current commit:

git rev-parse HEAD

Remote repository:

git remote get-url origin


---

## Implementation

Main script:

git_metadata.py


The script executes Git commands against the current Git
repository and generates structured metadata.


---

## Output

Generated file:

output/git_metadata.json


Example:

{
    "repository_name": "CoZo_Project_Manifest_Development",
    "repository_root": "D:/AgentAPI/CoZo_Project_Manifest_Development",
    "remote_url": "",
    "branch": "master",
    "commit_sha": "5450643e1a8b0318acd1e46f6960245532ffebe9",
    "generated_at": "2026-09-30T..."
}


---

## Remote Repository URL

If a Git remote named `origin` exists, the remote URL is
automatically extracted.

If no remote is configured, `remote_url` remains empty.

No fake or hard-coded GitHub URL is required.


---

## Manifest Integration

Git metadata is passed to the project manifest generation
process.

Flow:

Git Repository

        ↓

git_metadata.py

        ↓

git_metadata.json

        ↓

manifest_generator.py

        ↓

project-manifest.json


The generated manifest receives:

- Repository name
- Repository URL
- Current branch
- Current commit SHA


---

## Example Manifest Repository Metadata

{
    "repository": {
        "name": "CoZo_Project_Manifest_Development",
        "url": "",
        "branch": "master",
        "commit_sha": "5450643e1a8b0318acd1e46f6960245532ffebe9",
        "generated_at": "..."
    }
}


---

## Validation

After Git metadata is integrated, the project manifest is
validated against the manifest schema.

Expected result:

PROJECT MANIFEST IS VALID


---

## Status

Completed


## Next Task

Task 09 - Code Traceability Mapping