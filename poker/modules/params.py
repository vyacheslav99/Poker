from modules.base_model import BaseModel


class Params(BaseModel):

    def __init__(self, filename=None, **kwargs):
        super(Params, self).__init__(filename, **kwargs)

