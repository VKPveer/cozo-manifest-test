from sample_service import UserService

import os
import json


def main():

    service = UserService()

    service.create_user(
        "John",
        "john@test.com"
    )


if __name__ == "__main__":
    main()
