from server.helpers import HTTPException


class LoginAlreadyExists(HTTPException):
    code = 'LOGIN_ALREADY_EXISTS'
    message = 'Ошибка регистрации пользователя: такой логин уже зарегистрирован'

    def __init__(self, code: str = None, message: str = None):
        super().__init__(409, code=code or self.code, message=message or self.message)
