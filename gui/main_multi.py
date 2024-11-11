import os

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from models.params import Params, Options, Profiles
from gui.common import const
from gui.main_base import MainWnd


class MultiPlayerMainWnd(MainWnd):

    def __init__(self, app, *args):
        super().__init__()

        self.app = app
        self.__dev_mode = '--dev_mode' in args
        self.params = Params(filename=const.PARAMS_FILE if os.path.exists(const.PARAMS_FILE) else None)
        self.profiles = Profiles(filename=const.PROFILES_FILE if os.path.exists(const.PROFILES_FILE) else None)
        self.options = Options()
        self.curr_profile = None
        self._bikes = []
        self.load_bikes()

        self._started = False
        self._timer = None
        self._start_time = None
        self._prv_game_time = None
        self._bike_timer = None
        self.players = []
        self.table = {}
        self.game = None
        self.is_new_round = False
        self.is_new_lap = False
        self.order_dark = None
        self.joker_walk_card = None
        self.joker_selection = False
        self.can_show_results = False

        self.buttons = []
        self.labels = []
        self.table_label = None
        self.next_button = None
        self.deal_label = None
        self.first_move_label = None
        self.order_info_label = None
        self.ja_take_btn = None
        self.ja_take_by_btn = None
        self.ja_give_btn = None
        self.grid_stat_button = None
        self.game_table = None
        self.ja_lear_buttons = []
        self.round_result_labels = []
        self.service_wnd = None
        self.sb_labels = (QLabel(), QLabel())
        self.bike_area = None

        for i, lb in enumerate(self.sb_labels):
            self.statusBar().addPermanentWidget(lb, stretch=1 if i == 0 else -1)

        self.start_actn = None
        self.throw_actn = None
        self.svc_actn = None
        self.profiles_group = None

        self._stat_wnd = None

        self.init_profile()
        self.setWindowIcon(QIcon(const.MAIN_ICON))
        self.setWindowTitle(const.MAIN_WINDOW_TITLE)

        view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(QRectF(0, 0, *const.AREA_SIZE))
        view.setScene(self.scene)
        self.apply_decoration()
        self.init_menu_actions()

        # view.setFocusPolicy(Qt.StrongFocus)
        self.setCentralWidget(view)
        self.setFixedSize(*const.WINDOW_SIZE)
        self.resize(*const.WINDOW_SIZE)
        self.center()
        self.show()
