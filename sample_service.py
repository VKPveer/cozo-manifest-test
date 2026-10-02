import json
from datetime import datetime
from typing import Optional


class UserService:

    def __init__(self):

        self.users = {}

        self.audit_log = []


    def create_user(
        self,
        name,
        email,
        role="user"
    ):

        user_id = (
            f"user-{len(self.users) + 1}"
        )

        user = {
            "id": user_id,
            "name": name,
            "email": email,
            "role": role,
            "active": True,
            "created_at": (
                datetime.utcnow().isoformat()
            )
        }

        self.users[user_id] = user

        self._write_audit(
            "create_user",
            user_id
        )

        return user


    def get_user(
        self,
        user_id
    ):

        return self.users.get(
            user_id
        )


    def update_user(
        self,
        user_id,
        name=None,
        email=None,
        role=None
    ):

        user = self.users.get(
            user_id
        )

        if not user:

            return None


        if name is not None:

            user["name"] = name


        if email is not None:

            user["email"] = email


        if role is not None:

            user["role"] = role


        user["updated_at"] = (
            datetime.utcnow().isoformat()
        )


        self._write_audit(
            "update_user",
            user_id
        )


        return user


    def deactivate_user(
        self,
        user_id
    ):

        user = self.users.get(
            user_id
        )


        if not user:

            return False


        user["active"] = False


        self._write_audit(
            "deactivate_user",
            user_id
        )


        return True


    def activate_user(
        self,
        user_id
    ):

        user = self.users.get(
            user_id
        )


        if not user:

            return False


        user["active"] = True


        self._write_audit(
            "activate_user",
            user_id
        )


        return True


    def delete_user(
        self,
        user_id
    ):

        if user_id not in self.users:

            return False


        del self.users[user_id]


        self._write_audit(
            "delete_user",
            user_id
        )


        return True


    def search_users(
        self,
        search_text
    ):

        search_text = (
            search_text.lower()
        )


        results = []


        for user in self.users.values():

            if (
                search_text
                in user["name"].lower()
                or
                search_text
                in user["email"].lower()
            ):

                results.append(
                    user
                )


        return results


    def list_active_users(
        self
    ):

        return [

            user

            for user
            in self.users.values()

            if user.get(
                "active"
            )

        ]


    def export_users_json(
        self
    ):

        return json.dumps(
            list(
                self.users.values()
            ),
            indent=2
        )


    def get_user_count(
        self
    ):

        return len(
            self.users
        )


    def _write_audit(
        self,
        action,
        user_id
    ):

        self.audit_log.append({

            "action": action,

            "user_id": user_id,

            "timestamp":
                datetime.utcnow().isoformat()

        })


class UserValidationService:

    def validate_email(
        self,
        email
    ):

        return (
            isinstance(
                email,
                str
            )
            and "@" in email
            and "." in email
        )


    def validate_name(
        self,
        name
    ):

        return (
            isinstance(
                name,
                str
            )
            and len(
                name.strip()
            ) >= 2
        )


    def validate_role(
        self,
        role
    ):

        allowed_roles = {
            "user",
            "admin",
            "manager"
        }


        return (
            role
            in allowed_roles
        )


class UserReportService:

    def build_summary(
        self,
        users
    ):

        total = len(
            users
        )


        active = len([

            user

            for user
            in users

            if user.get(
                "active"
            )

        ])


        inactive = (
            total
            -
            active
        )


        return {

            "total_users":
                total,

            "active_users":
                active,

            "inactive_users":
                inactive

        }


def helper_function(
    value
):

    return value


def normalize_email(
    email
):

    return (
        email
        .strip()
        .lower()
    )


def generate_reference(
    prefix,
    number
):

    return (
        f"{prefix}-{number:06d}"
    )