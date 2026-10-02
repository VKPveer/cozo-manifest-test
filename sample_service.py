class UserService:

    def create_user(self, name, email):
        return {
            "name": name,
            "email": email
        }


    def delete_user(self, user_id):
        return True


def helper_function(value):
    return value

class UserService:

    def create_user(self, name, email):
        return {
            "name": name,
            "email": email
        }

    def delete_user(self, user_id):
        return True

    def update_user(self, user_id, name):
        return {
            "user_id": user_id,
            "name": name
        }


def helper_function(value):
    return value