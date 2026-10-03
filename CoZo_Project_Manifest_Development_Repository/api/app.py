import json
import os
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel


# =========================================================
# Paths / Configuration
# =========================================================

ROOT = Path(__file__).resolve().parent.parent

TEMP_ROOT = (
    ROOT
    / "api"
    / "temp_repos"
)

BUILD_DIR = (
    ROOT
    / "build"
)

PIPELINE_SCRIPT = (
    ROOT
    / "run_pipeline.py"
)


# =========================================================
# FastAPI App
# =========================================================

app = FastAPI(
    title="CoZo Project Manifest API",
    version="1.1"
)


# =========================================================
# Request Models
# =========================================================

class ManifestRequest(BaseModel):

    github_url: str

    branch: str | None = None

    work_items_file: str | None = None


class GitCommitPushRequest(BaseModel):

    repo_path: str

    commit_message: str

    # Optional safety check.
    # If supplied, it must match the currently checked-out branch.
    branch: str | None = None

    # false = local commit only
    # true  = commit + GitHub push
    push: bool = False


# =========================================================
# Common Helpers
# =========================================================

def ensure_temp_root():

    if (
        TEMP_ROOT.exists()
        and not TEMP_ROOT.is_dir()
    ):

        raise RuntimeError(
            f"{TEMP_ROOT} exists but is not a directory. "
            "Delete that file and create a folder named temp_repos."
        )


    TEMP_ROOT.mkdir(
        parents=True,
        exist_ok=True
    )


def get_git_executable():

    git_executable = shutil.which(
        "git"
    )


    if git_executable:

        return git_executable


    common_git_path = Path(
        r"C:\Program Files\Git\cmd\git.exe"
    )


    if common_git_path.exists():

        return str(
            common_git_path
        )


    raise RuntimeError(
        "Git executable was not found. "
        "Add C:\\Program Files\\Git\\cmd to PATH."
    )


def run_command(
    command,
    cwd=None
):

    env = os.environ.copy()


    # Force child Python processes to use UTF-8.
    # This avoids Windows cp1252 errors for characters such as ✅.
    env["PYTHONUTF8"] = "1"

    env["PYTHONIOENCODING"] = "utf-8"


    result = subprocess.run(

        command,

        cwd=cwd,

        capture_output=True,

        text=True,

        encoding="utf-8",

        errors="replace",

        env=env

    )


    if result.returncode != 0:

        raise RuntimeError(

            "\nCommand failed:\n"

            + " ".join(
                str(item)
                for item in command
            )

            + "\n\nSTDOUT:\n"

            + result.stdout

            + "\n\nSTDERR:\n"

            + result.stderr

        )


    return result


def run_git(
    repo_path: Path,
    *arguments
):

    git_executable = get_git_executable()


    return run_command(

        [

            git_executable,

            "-C",

            str(
                repo_path
            ),

            *arguments

        ]

    )


def load_json_file(
    file_path: Path
):

    if not file_path.exists():

        raise RuntimeError(
            f"Required file not found: {file_path}"
        )


    with open(

        file_path,

        "r",

        encoding="utf-8"

    ) as file:

        return json.load(
            file
        )


# =========================================================
# Manifest Helpers
# =========================================================

def clone_repository(
    github_url: str,
    target_folder: Path,
    branch: str | None
):

    git_executable = get_git_executable()


    command = [

        git_executable,

        "clone"

    ]


    if branch:

        command.extend(

            [

                "--branch",

                branch

            ]

        )


    command.extend(

        [

            github_url,

            str(
                target_folder
            )

        ]

    )


    run_command(
        command
    )


def run_manifest_pipeline(
    repo_folder: Path,
    work_items_file: str | None
):

    if not PIPELINE_SCRIPT.exists():

        raise RuntimeError(
            f"Pipeline script not found: {PIPELINE_SCRIPT}"
        )


    command = [

        sys.executable,

        str(
            PIPELINE_SCRIPT
        ),

        "--repo",

        str(
            repo_folder
        )

    ]


    if work_items_file:

        work_items_path = Path(
            work_items_file
        )


        if not work_items_path.exists():

            raise RuntimeError(
                f"Work-items file not found: {work_items_path}"
            )


        if not work_items_path.is_file():

            raise RuntimeError(
                "work_items_file must point to a JSON file."
            )


        command.extend(

            [

                "--work-items",

                str(
                    work_items_path
                )

            ]

        )


    run_command(
        command
    )


# =========================================================
# Health Endpoint
# =========================================================

@app.get(
    "/health"
)
def health():

    return {

        "status":
            "ok",

        "pipeline_script_exists":
            PIPELINE_SCRIPT.exists(),

        "git_executable":
            get_git_executable(),

        "build_directory":
            str(
                BUILD_DIR
            )

    }


# =========================================================
# Generate Manifest
# =========================================================

@app.post(
    "/generate-manifest"
)
def generate_manifest(
    request: ManifestRequest
):

    job_id = str(
        uuid.uuid4()
    )


    ensure_temp_root()


    repo_folder = (

        TEMP_ROOT

        /

        job_id

    )


    try:

        # -----------------------------------------
        # Clone GitHub repository
        # -----------------------------------------

        clone_repository(

            request.github_url,

            repo_folder,

            request.branch

        )


        # -----------------------------------------
        # Run complete project-manifest pipeline
        # -----------------------------------------

        run_manifest_pipeline(

            repo_folder,

            request.work_items_file

        )


        # -----------------------------------------
        # Generated output files
        # -----------------------------------------

        manifest_file = (

            BUILD_DIR

            /

            "project-manifest.json"

        )


        validation_file = (

            BUILD_DIR

            /

            "validation_report.json"

        )


        # -----------------------------------------
        # Load generated manifest
        # -----------------------------------------

        manifest = load_json_file(
            manifest_file
        )


        validation = None


        if validation_file.exists():

            validation = load_json_file(
                validation_file
            )


        # -----------------------------------------
        # API response
        # -----------------------------------------

        return {

            "job_id":
                job_id,

            "status":
                "completed",

            "repository":
                request.github_url,

            "branch":
                request.branch,

            "validation":
                validation,

            "manifest":
                manifest

        }


    except HTTPException:

        raise


    except Exception as error:

        raise HTTPException(

            status_code=500,

            detail=str(
                error
            )

        )


    finally:

        # -----------------------------------------
        # Remove temporary cloned repository
        # -----------------------------------------

        if repo_folder.exists():

            shutil.rmtree(

                repo_folder,

                ignore_errors=True

            )


# =========================================================
# Manifest Download
# =========================================================

@app.get(
    "/manifest/download"
)
def download_manifest():

    manifest_file = (

        BUILD_DIR

        /

        "project-manifest.json"

    )


    if not manifest_file.exists():

        raise HTTPException(

            status_code=404,

            detail=(
                "project-manifest.json not found"
            )

        )


    return FileResponse(

        path=str(
            manifest_file
        ),

        filename=(
            "project-manifest.json"
        ),

        media_type=(
            "application/json"
        )

    )


# =========================================================
# Git Commit / Optional Push
# =========================================================

@app.post(
    "/git/commit-push"
)
def git_commit_push(
    request: GitCommitPushRequest
):

    repo_path = Path(
        request.repo_path
    ).resolve()


    try:

        # -----------------------------------------
        # Validate local repository path
        # -----------------------------------------

        if not repo_path.exists():

            raise HTTPException(

                status_code=404,

                detail=(
                    f"Repository path not found: "
                    f"{repo_path}"
                )

            )


        if not repo_path.is_dir():

            raise HTTPException(

                status_code=400,

                detail=(
                    "repo_path must point to a directory."
                )

            )


        git_dir = (

            repo_path

            /

            ".git"

        )


        if not git_dir.exists():

            raise HTTPException(

                status_code=400,

                detail=(
                    f"Not a Git repository: "
                    f"{repo_path}"
                )

            )


        # -----------------------------------------
        # Current Git branch
        # -----------------------------------------

        branch_result = run_git(

            repo_path,

            "branch",

            "--show-current"

        )


        current_branch = (
            branch_result.stdout.strip()
        )


        if not current_branch:

            raise RuntimeError(
                "Unable to determine current Git branch."
            )


        # -----------------------------------------
        # Optional branch safety check
        # -----------------------------------------

        if (

            request.branch

            and

            request.branch
            !=
            current_branch

        ):

            raise HTTPException(

                status_code=400,

                detail=(

                    f"Requested branch "
                    f"'{request.branch}' "

                    f"does not match "
                    f"currently checked-out branch "

                    f"'{current_branch}'."

                )

            )


        # -----------------------------------------
        # Git remote URL
        # -----------------------------------------

        remote_result = run_git(

            repo_path,

            "config",

            "--get",

            "remote.origin.url"

        )


        remote_url = (
            remote_result.stdout.strip()
        )


        # -----------------------------------------
        # Detect working-tree changes
        # -----------------------------------------

        status_result = run_git(

            repo_path,

            "status",

            "--porcelain"

        )


        changes = (

            status_result.stdout

            .strip()

            .splitlines()

        )


        # =================================================
        # CASE 1:
        # No new local file changes
        #
        # If push=true, still push any previously committed
        # local commits that have not reached GitHub yet.
        # =================================================

        if not changes:

            pushed = False


            if request.push:

                run_git(

                    repo_path,

                    "push",

                    "origin",

                    current_branch

                )


                pushed = True


            # Current local HEAD SHA
            head_result = run_git(

                repo_path,

                "rev-parse",

                "HEAD"

            )


            current_sha = (
                head_result.stdout.strip()
            )


            return {

                "status":
                    "no_changes",

                "repository":
                    str(
                        repo_path
                    ),

                "remote":
                    remote_url,

                "branch":
                    current_branch,

                "commit_sha":
                    current_sha,

                "committed":
                    False,

                "pushed":
                    pushed,

                "message": (

                    "No new working-tree changes found. "
                    "Existing local commits were pushed."

                    if pushed

                    else

                    "No local changes found."

                )

            }


        # =================================================
        # CASE 2:
        # Local working-tree changes exist
        # =================================================


        # -----------------------------------------
        # Stage all changes
        # -----------------------------------------

        run_git(

            repo_path,

            "add",

            "-A"

        )


        # -----------------------------------------
        # Commit changes
        # -----------------------------------------

        run_git(

            repo_path,

            "commit",

            "-m",

            request.commit_message

        )


        # -----------------------------------------
        # Get new commit SHA
        # -----------------------------------------

        sha_result = run_git(

            repo_path,

            "rev-parse",

            "HEAD"

        )


        commit_sha = (
            sha_result.stdout.strip()
        )


        pushed = False


        # -----------------------------------------
        # Push ONLY when explicitly requested
        # -----------------------------------------

        if request.push:

            run_git(

                repo_path,

                "push",

                "origin",

                current_branch

            )


            pushed = True


        # -----------------------------------------
        # Return result
        # -----------------------------------------

        return {

            "status":
                "completed",

            "repository":
                str(
                    repo_path
                ),

            "remote":
                remote_url,

            "branch":
                current_branch,

            "commit_sha":
                commit_sha,

            "committed":
                True,

            "pushed":
                pushed,

            "commit_message":
                request.commit_message,

            "changed_files":
                changes

        }


    except HTTPException:

        raise


    except Exception as error:

        raise HTTPException(

            status_code=500,

            detail=str(
                error
            )

        )