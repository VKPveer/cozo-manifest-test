import json
import os
import logging
from pathlib import Path
from datetime import datetime

from sample_service import (
    UserService,
    UserValidationService,
    UserReportService,
    normalize_email,
    generate_reference
)


logging.basicConfig(
    level=logging.INFO
)

logger = logging.getLogger(
    __name__
)


DATA_FILE = Path(
    "users.json"
)


def load_seed_users():

    if not DATA_FILE.exists():

        return []


    with open(
        DATA_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def save_users(
    users
):

    with open(
        DATA_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            users,
            file,
            indent=2
        )


def create_demo_users(
    user_service,
    validation_service
):

    demo_users = [

        {
            "name": "John Smith",
            "email": "john@example.com",
            "role": "admin"
        },

        {
            "name": "Alice Brown",
            "email": "alice@example.com",
            "role": "user"
        },

        {
            "name": "Bob Taylor",
            "email": "bob@example.com",
            "role": "manager"
        }

    ]


    created_users = []


    for item in demo_users:

        email = normalize_email(
            item["email"]
        )


        if not validation_service.validate_email(
            email
        ):

            logger.warning(
                "Invalid email: %s",
                email
            )

            continue


        if not validation_service.validate_name(
            item["name"]
        ):

            logger.warning(
                "Invalid name: %s",
                item["name"]
            )

            continue


        if not validation_service.validate_role(
            item["role"]
        ):

            logger.warning(
                "Invalid role: %s",
                item["role"]
            )

            continue


        created = user_service.create_user(

            item["name"],

            email,

            item["role"]

        )


        created_users.append(
            created
        )


    return created_users


def print_user_report(
    user_service,
    report_service
):

    users = list(
        user_service.users.values()
    )


    report = report_service.build_summary(
        users
    )


    print(
        "User Report"
    )

    print(
        "-----------"
    )

    print(
        "Total:",
        report["total_users"]
    )

    print(
        "Active:",
        report["active_users"]
    )

    print(
        "Inactive:",
        report["inactive_users"]
    )


def update_demo_user(
    user_service
):

    user = user_service.get_user(
        "user-1"
    )


    if not user:

        return


    updated = user_service.update_user(

        "user-1",

        name="John Updated",

        role="manager"

    )


    logger.info(
        "Updated user: %s",
        updated
    )


def deactivate_demo_user(
    user_service
):

    success = user_service.deactivate_user(
        "user-2"
    )


    logger.info(
        "Deactivate result: %s",
        success
    )


def search_demo_users(
    user_service
):

    results = user_service.search_users(
        "john"
    )


    print(
        "Search results:"
    )


    for user in results:

        print(
            user
        )


def export_demo_users(
    user_service
):

    output = user_service.export_users_json()


    print(
        "Exported JSON:"
    )

    print(
        output
    )


def generate_demo_reference():

    reference = generate_reference(
        "USR",
        123
    )


    print(
        "Generated reference:",
        reference
    )


def show_runtime_info():

    print(
        "Runtime information"
    )

    print(
        "Working directory:",
        os.getcwd()
    )

    print(
        "Timestamp:",
        datetime.utcnow().isoformat()
    )


def main():

    user_service = UserService()

    validation_service = (
        UserValidationService()
    )

    report_service = (
        UserReportService()
    )


    seed_users = load_seed_users()


    logger.info(
        "Loaded seed users: %s",
        len(seed_users)
    )


    created_users = create_demo_users(

        user_service,

        validation_service

    )


    logger.info(
        "Created users: %s",
        len(created_users)
    )


    update_demo_user(
        user_service
    )


    deactivate_demo_user(
        user_service
    )


    search_demo_users(
        user_service
    )


    print_user_report(

        user_service,

        report_service

    )


    export_demo_users(
        user_service
    )


    generate_demo_reference()


    save_users(
        list(
            user_service.users.values()
        )
    )


    show_runtime_info()


if __name__ == "__main__":

    main()