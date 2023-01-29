from models.base_model import BaseModel
from api.modules.utils import encrypt


class Authorization(BaseModel):

    def __init__(self, **kwargs):
        self.login = None
        self._password = None

        super().__init__(**kwargs)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        if value is not None:
            self._password = encrypt(value)
        else:
            self._password = value