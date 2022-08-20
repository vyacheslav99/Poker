from models.base_model import BaseModel
from modules.utils import encrypt


class AuthRequest(BaseModel):

    def __init__(self, filename=None, **kwargs):
        self.login = None
        self._password = None

        super().__init__(filename=filename, **kwargs)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        if value is not None:
            self._password = encrypt(value)
        else:
            self._password = value


class RegisterRequest(AuthRequest):

    def __init__(self, filename=None, **kwargs):
        self.name = None

        super().__init__(filename=filename, **kwargs)