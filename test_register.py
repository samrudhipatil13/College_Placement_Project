from utils.auth_utils import register_user

success, message = register_user("teststudent@gmail.com", "MyPassword123", role="student")
print(message)