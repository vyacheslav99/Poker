from models.base_model import BaseModel


class AuthRequest(BaseModel):

    def __init__(self, filename=None, **kwargs):
        self.login = None
        self.password = None

        super().__init__(filename=filename, **kwargs)