import platform
import rsa
import base64
import requests
from requests import Response
from requests.exceptions import RequestException

from models.params import Params, Options
from models.player import Player
from gui.common import const


class BaseClient:

    def __init__(self, host):
        self._host = host
        self._token: str | None = None
        self._user_agent: str = self.get_user_agent()
        self._public_key: str | None = None

    @property
    def token(self) -> str | None:
        return self._token

    @token.setter
    def token(self, value: str):
        self._token = value

    def get_user_agent(self) -> str:
        plat_info = platform.uname()

        return (f'Poker game client/1.0.0 {plat_info.node} ('
                f'{plat_info.system}; {plat_info.release}; {plat_info.version}; '
                f'{plat_info.machine}; {plat_info.processor})')

    def get_default_headers(self) -> dict:
        headers = {'User-Agent': self._user_agent}

        if self.token:
            headers.update(Authorization=f'bearer {self.token}')

        return headers

    def _request(
        self, method: str, url: str, query: dict | None = None, json: dict | None = None, headers: dict | None = None
    ) -> Response:
        resp = getattr(requests, method)(
            url, params=query, json=json, headers=dict(self.get_default_headers(), **(headers or {})),
            timeout=const.REQUEST_TIMEOUT
        )
        resp.raise_for_status()
        return resp

    def _make_api_url(self, endpoint: str) -> str:
        return f'{self._host}/api/{endpoint}'

    def _make_base_url(self, endpoint: str) -> str:
        return f'{self._host}/{endpoint}'

    def get(self, url: str, query: dict | None = None, headers: dict | None = None) -> Response:
        return self._request('get', url, query=query, headers=headers)

    def post(self, url: str, json: dict | None = None, headers: dict | None = None) -> Response:
        return self._request('post', url, json=json, headers=headers)

    def put(self, url: str, json: dict | None = None, headers: dict | None = None) -> Response:
        return self._request('put', url, json=json, headers=headers)

    def patch(self, url: str, json: dict | None = None, headers: dict | None = None) -> Response:
        return self._request('patch', url, json=json, headers=headers)

    def delete(self, url: str, query: dict | None = None, json: dict | None = None,
               headers: dict | None = None) -> Response:
        return self._request('delete', url, query=query, json=json, headers=headers)

    def encrypt(self, plain_value: str) -> str:
        if not self._public_key:
            self.load_public_key()

        pubkey = rsa.PublicKey.load_pkcs1(self._public_key.encode())
        cipher = rsa.encrypt(plain_value.encode(), pubkey)
        b64_value = base64.urlsafe_b64encode(cipher)
        return b64_value.decode()

    def load_public_key(self):
        resp = self.get(self._make_api_url('public-key'))
        self._public_key = resp.text


class GameServerClient(BaseClient):

    def is_alive(self) -> tuple[bool, str]:
        try:
            resp = self.get(self._make_base_url('is_alive'))
            data = resp.json()

            if {'server', 'version', 'status'} == set(data.keys()):
                return True, '\n'.join([data[k] for k in data])
            else:
                return False, 'Bad response format'
        except RequestException as e:
            return False, str(e)

    def get_params(self) -> Params:
        # todo: Метод сервера пока не реализован, сделаю вместе с ним
        pass

    def set_params(self, params: Params):
        # todo: Метод сервера пока не реализован, сделаю вместе с ним
        pass

    def get_game_agreements(self) -> Options:
        # todo: Метод сервера пока не реализован, сделаю вместе с ним
        pass

    def set_game_agreements(self, options: Options):
        # todo: Метод сервера пока не реализован, сделаю вместе с ним
        pass

    def _make_player(self, data: dict) -> Player:
        return Player(
            uid=data['uid'],
            login=data['username'],
            password=self.token,
            name=data['fullname'],
            avatar=data['avatar']
        )

    def get_user(self) -> Player:
        resp = self.get(self._make_api_url('user'))
        return self._make_player(resp.json())

    def authorize_safe(self, username: str, password: str) -> str:
        self.token = None
        payload = {
            'username': username,
            'password': self.encrypt(password)
        }

        resp = self.post(self._make_api_url('login'), json=payload)
        data = resp.json()
        self.token = data.get('access_token')
        return self.token
