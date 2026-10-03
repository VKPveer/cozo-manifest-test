# CoZo Project Manifest Development — Repository-Wide Version

This package has been converted from hard-coded sample files to a repository-wide pipeline.

## What it now does

- Accepts a real cloned GitHub repository (`--repo`) or a repository ZIP (`--repo-zip`).
- Recursively scans supported source files across all folders.
- Detects language per file.
- Parses every Python file with Python AST; performs best-effort symbol extraction for common non-Python languages without inventing external dependencies.
- Extracts symbols and source line locations repository-wide.
- Extracts Python imports and JS/TS imports repository-wide.
- Classifies Python dependencies as standard-library/internal/external using the repository's actual module tree (no `sample*` rule).
- Reads Git metadata from the target repository. For GitHub ZIP archives (which normally have no `.git` folder), URL/branch/SHA can be supplied explicitly.
- Maps Requirement → Story → Task → code using a backend-neutral work-items contract. No CoZo MongoDB collection names are guessed.
- Generates and validates one `project-manifest.json`.
- Includes a CLI reader for agent queries.

## Install

```bash
pip install -r requirements.txt
```

## Run against a cloned repository

```bash
python run_pipeline.py --repo "D:\\path\\to\\real-project"
```

Optional traceability export:

```bash
python run_pipeline.py --repo "D:\\path\\to\\real-project" --work-items "D:\\path\\to\\work_items.json"
```

## Run directly against a GitHub/project ZIP

```bash
python run_pipeline.py --repo-zip "D:\\downloads\\project.zip" --repository-url "https://github.com/org/repo.git" --branch main --commit-sha <sha>
```

The ZIP is extracted under `build/extracted_repo` and all nested folders are scanned.

## Outputs

`build/project-manifest.json` — final manifest  
`build/validation_report.json` — schema validation result  
Intermediate Task 02–09 outputs are also placed in `build/`.

## Traceability input contract

The real CoZo backend/API should export records into this neutral shape (see `work_items.example.json`):

```json
{
  "items": [
    {
      "tenant_id": "...",
      "project_id": "...",
      "requirement_ids": ["REQ-..."],
      "story_id": "STORY-...",
      "task_id": "TASK-...",
      "task_run_id": "RUN-...",
      "code_reference": {
        "file": "repository/relative/path.py",
        "class_name": "ClassName",
        "symbol": "method_name"
      }
    }
  ]
}
```

This deliberately does **not** invent MongoDB collections or production API fields. Once the backend team confirms those contracts, an adapter can export them into this format.

## Important limitations

Python parsing is AST-based and suitable for structural indexing. Non-Python parsing is intentionally best-effort regex parsing in this dependency-free package; for production-grade JavaScript/TypeScript/Java/C#/etc. symbol accuracy, add language-native parsers (for example Tree-sitter) as a later enhancement.
