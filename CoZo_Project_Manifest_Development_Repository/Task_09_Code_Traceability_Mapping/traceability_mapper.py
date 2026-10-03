import argparse
import json
import os
from pathlib import Path
from datetime import datetime

def load(path):
    return json.loads(
        Path(path).read_text(
            encoding="utf-8"
        )
    )


def norm(path):
    return (
        str(path or "")
        .replace("\\", "/")
        .strip("/")
    )


def resolve_symbol(
    symbols,
    ref
):

    wanted_file = norm(
        ref.get("file")
    )

    wanted_name = (
        ref.get("symbol")
        or ref.get("method")
        or ref.get("name")
    )

    wanted_class = (
        ref.get("class_name")
        or ref.get("class")
    )


    exact_matches = []
    basename_matches = []


    for symbol in symbols:

        if (
            wanted_name
            and symbol.get("name") != wanted_name
        ):
            continue


        if (
            wanted_class is not None
            and symbol.get("class_name") != wanted_class
        ):
            continue


        symbol_file = norm(
            symbol.get("file")
        )


        if symbol_file == wanted_file:

            exact_matches.append(
                symbol
            )


        elif (
            wanted_file
            and os.path.basename(symbol_file)
            ==
            os.path.basename(wanted_file)
        ):

            basename_matches.append(
                symbol
            )


    if len(exact_matches) == 1:

        return exact_matches[0]


    if len(exact_matches) > 1:

        raise ValueError(
            f"Ambiguous exact code reference: {ref}"
        )


    if len(basename_matches) == 1:

        return basename_matches[0]


    if len(basename_matches) > 1:

        raise ValueError(
            f"Ambiguous filename {wanted_file}; "
            "provide repository-relative path."
        )


    return None


def get_requirement_ids(
    work_item
):

    # Flat format
    requirement_ids = work_item.get(
        "requirement_ids"
    )

    if requirement_ids:

        return requirement_ids


    requirement_id = work_item.get(
        "requirement_id"
    )

    if requirement_id:

        return [
            requirement_id
        ]


    # Nested format
    requirement = work_item.get(
        "requirement",
        {}
    )

    nested_requirement_id = requirement.get(
        "requirement_id"
    )

    if nested_requirement_id:

        return [
            nested_requirement_id
        ]


    return []


def get_story_id(
    work_item
):

    # Flat format
    story_id = (
        work_item.get("story_id")
        or work_item.get("user_story_id")
    )

    if story_id:

        return story_id


    # Nested format
    user_story = work_item.get(
        "user_story",
        {}
    )

    return user_story.get(
        "story_id"
    )


def get_task_id(
    work_item
):

    # Flat format
    task_id = work_item.get(
        "task_id"
    )

    if task_id:

        return task_id


    # Nested format
    task = work_item.get(
        "task",
        {}
    )

    return task.get(
        "task_id"
    )


def get_task_run_id(
    work_item
):

    task_run_id = work_item.get(
        "task_run_id"
    )

    if task_run_id:

        return task_run_id


    task_run = work_item.get(
        "task_run",
        {}
    )

    return task_run.get(
        "task_run_id"
    )


def build(
    records,
    symbols
):

    output = []


    for work_item in records:

        code_reference = work_item.get(
            "code_reference"
        ) or {}


        matched_symbol = (

            resolve_symbol(
                symbols,
                code_reference
            )

            if code_reference

            else None
        )


        record = {

            "tenant_id":
                work_item.get(
                    "tenant_id"
                ),

            "project_id":
                work_item.get(
                    "project_id"
                ),

            "requirement_ids":
                get_requirement_ids(
                    work_item
                ),

            "story_id":
                get_story_id(
                    work_item
                ),

            "task_id":
                get_task_id(
                    work_item
                ),

            "task_run_id":
                get_task_run_id(
                    work_item
                ),

            "git":
                work_item.get(
                    "git",
                    {}
                ),
              "mapped_at": datetime.now().astimezone().isoformat(
                           timespec="seconds"
               ),

            "code_reference":
                None

        }


        if matched_symbol:

            record["code_reference"] = {

                "file":
                    matched_symbol.get(
                        "file"
                    ),

                "symbol_type":
                    matched_symbol.get(
                        "symbol_type"
                    ),

                "class_name":
                    matched_symbol.get(
                        "class_name"
                    ),

                "symbol":
                    matched_symbol.get(
                        "name"
                    ),

                "signature":
                    matched_symbol.get(
                        "signature"
                    ),

                "line_start":
                    matched_symbol.get(
                        "line_start"
                    ),

                "line_end":
                    matched_symbol.get(
                        "line_end"
                    )

            }


        elif code_reference:

            record[
                "unresolved_code_reference"
            ] = code_reference


        output.append(
            record
        )


    return output


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Map backend-neutral work-item records "
            "to extracted code symbols."
        )
    )


    parser.add_argument(
        "--symbols",
        required=True
    )


    parser.add_argument(
        "--work-items",
        help=(
            'JSON file: {"items":[...]} or a list. '
            "Omit to generate empty traceability."
        )
    )


    parser.add_argument(
        "--output",
        default=str(
            Path(__file__).parent
            / "output"
            / "traceability.json"
        )
    )


    args = parser.parse_args()


    symbols = load(
        args.symbols
    )


    records = []


    if args.work_items:

        raw = load(
            args.work_items
        )

        if isinstance(
            raw,
            dict
        ):

            records = raw.get(
                "items",
                []
            )

        else:

            records = raw


    result = {

        "traceability":
            build(
                records,
                symbols
            )

    }


    output_file = Path(
        args.output
    )


    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )


    output_file.write_text(
        json.dumps(
            result,
            indent=2
        ),
        encoding="utf-8"
    )


    unresolved = sum(

        1
        for item in result["traceability"]

        if item.get(
            "unresolved_code_reference"
        )

    )


    print(
        f"Traceability generated: "
        f"{len(result['traceability'])} records "
        f"-> {output_file}"
    )


    if unresolved:

        print(
            f"Unresolved code references: "
            f"{unresolved}"
        )


if __name__ == "__main__":

    main()