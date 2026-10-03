import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def load_json(path):

    return json.loads(
        Path(path).read_text(
            encoding="utf-8"
        )
    )


def enrich_traceability_with_git(
    traceability_data,
    git_metadata
):

    if isinstance(traceability_data, dict):

        records = traceability_data.get(
            "traceability",
            []
        )

    else:

        records = traceability_data


    branch = git_metadata.get(
        "branch",
        ""
    )

    commit_sha = git_metadata.get(
        "commit_sha",
        ""
    )


    for record in records:

        existing_git = record.get(
            "git"
        ) or {}


        record["git"] = {

            "branch":
                existing_git.get(
                    "branch"
                )
                or branch,

            "commit_sha":
                existing_git.get(
                    "commit_sha"
                )
                or commit_sha

        }


    return records


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Attach real Git metadata and code "
            "traceability to the base manifest."
        )
    )


    parser.add_argument(
        "--base-manifest",
        required=True
    )

    parser.add_argument(
        "--git-metadata",
        required=True
    )

    parser.add_argument(
        "--traceability",
        required=True
    )

    parser.add_argument(
        "--output",
        default=str(
            Path(__file__).parent
            / "output"
            / "project-manifest.json"
        )
    )


    args = parser.parse_args()


    base_manifest = load_json(
        args.base_manifest
    )

    git_metadata = load_json(
        args.git_metadata
    )

    traceability_data = load_json(
        args.traceability
    )


    # Repository metadata
    base_manifest["repository"] = {

        "name":
            git_metadata.get(
                "name",
                ""
            ),

        "url":
            git_metadata.get(
                "url",
                ""
            ),

        "branch":
            git_metadata.get(
                "branch",
                ""
            ),

        "commit_sha":
            git_metadata.get(
                "commit_sha",
                ""
            )

    }


    # Manifest generation timestamp
    base_manifest["generated_at"] = (
        datetime.now(
            timezone.utc
        ).isoformat()
    )


    # Add repository Git metadata
    # into every traceability record
    traceability_records = (
        enrich_traceability_with_git(
            traceability_data,
            git_metadata
        )
    )


    base_manifest["traceability"] = (
        traceability_records
    )


    output_file = Path(
        args.output
    )


    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )


    output_file.write_text(
        json.dumps(
            base_manifest,
            indent=2
        ),
        encoding="utf-8"
    )


    print(
        f"Final project manifest generated: "
        f"{output_file}"
    )

    print(
        "Repository:",
        base_manifest[
            "repository"
        ].get("name")
    )

    print(
        "Branch:",
        base_manifest[
            "repository"
        ].get("branch")
    )

    print(
        "Commit:",
        base_manifest[
            "repository"
        ].get("commit_sha")
    )

    print(
        "Traceability records:",
        len(
            base_manifest.get(
                "traceability",
                []
            )
        )
    )


if __name__ == "__main__":

    main()