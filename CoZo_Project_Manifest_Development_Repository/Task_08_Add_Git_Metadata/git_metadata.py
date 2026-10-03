import argparse
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone


def run_git(repo_path, *args):

    result = subprocess.run(
        [
            "git",
            "-C",
            str(repo_path),
            *args
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    if result.returncode != 0:
        return ""

    return result.stdout.strip()


def get_repository_name(
    repository_url,
    repo_path
):

    # Prefer repository name from remote URL
    if repository_url:

        url = repository_url.strip().rstrip("/")

        # HTTPS:
        # https://github.com/VKPveer/cozo-manifest-test.git

        # SSH:
        # git@github.com:VKPveer/cozo-manifest-test.git

        if ":" in url and "://" not in url:
            name = url.rsplit(":", 1)[-1]
        else:
            name = url.rsplit("/", 1)[-1]

        name = name.rsplit("/", 1)[-1]

        if name.endswith(".git"):
            name = name[:-4]

        if name:
            return name

    # Fallback for non-Git/local repository
    return Path(repo_path).resolve().name


def build_git_metadata(repo_path):

    repo_path = Path(repo_path).resolve()

    repository_url = run_git(
        repo_path,
        "config",
        "--get",
        "remote.origin.url"
    )

    branch = run_git(
        repo_path,
        "branch",
        "--show-current"
    )

    commit_sha = run_git(
        repo_path,
        "rev-parse",
        "HEAD"
    )

    repository_name = get_repository_name(
        repository_url,
        repo_path
    )

    return {
        "name": repository_name,
        "url": repository_url,
        "branch": branch,
        "commit_sha": commit_sha,
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat()
    }


def main():

    parser = argparse.ArgumentParser(
        description="Extract Git metadata for project manifest."
    )

    parser.add_argument(
        "--repo",
        required=True,
        help="Path to cloned Git repository."
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Output git_metadata.json path."
    )

    args = parser.parse_args()

    metadata = build_git_metadata(
        args.repo
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
            metadata,
            indent=2
        ),
        encoding="utf-8"
    )

    print(
        f"Git metadata generated: {output_file}"
    )

    print(
        "Repository:",
        metadata["name"]
    )

    print(
        "Branch:",
        metadata["branch"]
    )

    print(
        "Commit:",
        metadata["commit_sha"]
    )


if __name__ == "__main__":
    main()