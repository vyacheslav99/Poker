from modules.base_model import BaseModel


class Params(BaseModel):

    def __init__(self, filename=None, **kwargs):
        self.user = None
        self.color_theme = 'green'

        super(Params, self).__init__(filename, **kwargs)
