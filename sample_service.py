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
