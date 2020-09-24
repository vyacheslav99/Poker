from modules.base_model import BaseModel


class Params(BaseModel):

    def __init__(self, filename=None, **kwargs):
        self.user = None
        self.color_theme = 'green'

        super(Params, self).__init__(filename, **kwargs)


class Profile(BaseModel):

    def __init__(self, filename=None, **kwargs):
        self.uid = None
        self.login = None
        self.name = None
        self.avatar = None

        self.started = 0            # кол-во начатых игр
        self.completed = 0          # кол-во сыгранных игр
        self.throw = 0              # кол-во брошенных партий
        self.winned = 0             # кол-во выигранных партий
        self.lost = 0               # кол-во проигранных партий
        self.scores = 0             # общий суммарный выигрыш (сумма очков всех сыгранных партий)
        self.money = 0.0            # общая сумма денег (сумма денег всех сыгранных партий)
        self.last_scores = 0        # последний выигрыш (очки)
        self.last_money = 0.0       # последний выигрыш (деньги)
        self.best_scores = 0        # лучший выигрыш (очки)
        self.best_money = 0.0       # лучший выигрыш (деньги)

        super(Profile, self).__init__(filename, **kwargs)


class Profiles(object):

    def __init__(self, filename=None):
        pass
