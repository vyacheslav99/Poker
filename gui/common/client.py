import os
import platform
import rsa
import base64
import requests
from requests import Response
from requests.exceptions import RequestException

from models.params import Params, Options
from models.player import Player
from gui.common import const


class ClientException(RequestException):

    def __init__(self, status: int, message: str, response: Response):
        super().__init__(response=response)

        self.status_code: int = status
        self.message: str = message


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

        return (f'Poker game client/{const.VERSION}|'
                f'{plat_info.node}|'
                f'{plat_info.system}; {plat_info.version}|'
                f'{plat_info.machine}; {plat_info.processor}')

    def get_default_headers(self) -> dict:
        headers = {'User-Agent': self._user_agent}

        if self.token:
            headers.update(Authorization=f'bearer {self.token}')

        return headers

    def raise_for_status(self, response: Response):
        if response.status_code >= 400:
            text = None

            try:
                body = response.json()
                text = body.get('detail', body.get('message', body.get('error')))
            except Exception:
                pass

            if not text:
                text = response.text

            if not text:
                text = response.reason

            raise ClientException(response.status_code, text, response=response)

    def _request(
        self, method: str, url: str, query: dict | None = None, json: dict | None = None, files = None,
        headers: dict | None = None
    ) -> Response:
        resp = getattr(requests, method)(
            url, params=query, json=json, files=files, headers=dict(self.get_default_headers(), **(headers or {})),
            timeout=const.REQUEST_TIMEOUT
        )
        self.raise_for_status(resp)
        return resp

    def _make_api_url(self, endpoint: str) -> str:
        return f'{self._host}/api/{endpoint}'

    def _make_base_url(self, endpoint: str) -> str:
        return f'{self._host}/{endpoint}'

    def get(self, url: str, query: dict | None = None, headers: dict | None = None) -> Response:
        return self._request('get', url, query=query, headers=headers)

    def post(self, url: str, json: dict | None = None, files = None, headers: dict | None = None) -> Response:
        return self._request('post', url, json=json, files=files, headers=headers)

    def put(self, url: str, json: dict | None = None, files = None, headers: dict | None = None) -> Response:
        return self._request('put', url, json=json, files=files, headers=headers)

    def patch(self, url: str, json: dict | None = None, files = None, headers: dict | None = None) -> Response:
        return self._request('patch', url, json=json, files=files, headers=headers)

    def delete(
        self, url: str, query: dict | None = None, json: dict | None = None, headers: dict | None = None
    ) -> Response:
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

    FILES_BASE_PATH = 'static/files'

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

    def username_is_free(self, username: str) -> bool:
        resp = self.get(self._make_api_url('is_free_username'), query={'username': username})
        data = resp.json()
        return data['success']

    def _make_player(self, data: dict, set_current_token: bool = True) -> Player:
        return Player(
            uid=data['uid'],
            login=data['username'],
            password=self.token if set_current_token else None,
            name=data['fullname'],
            avatar=data['avatar']
        )

    def _dump_player(self, player: Player, only_patch_fields: bool = True) -> dict:
        fields_map = {'uid': 'uid', 'login': 'username', 'name': 'fullname', 'avatar': 'avatar'}
        patch_fields = {'name'}

        if only_patch_fields:
            return {fields_map[k]: v for k, v in player.as_dict().items() if k in patch_fields}
        else:
            return {fields_map[k]: v for k, v in player.as_dict().items() if k in fields_map.keys()}

    def registration(self, username: str, password: str) -> Player:
        payload = {
            'username': username,
            'password': self.encrypt(password)
        }

        resp = self.post(self._make_api_url('user'), json=payload)
        return self._make_player(resp.json(), set_current_token=False)

    def get_user(self) -> Player:
        resp = self.get(self._make_api_url('user'))
        return self._make_player(resp.json())

    def authorize_safe(self, username: str, password: str) -> str:
        payload = {
            'username': username,
            'password': self.encrypt(password)
        }

        resp = self.post(self._make_api_url('login'), json=payload)
        data = resp.json()
        self.token = data.get('access_token')
        return self.token

    def logout(self):
        self.post(self._make_api_url('logout'))
        self.token = None

    def delete_user(self, password: str):
        payload = {
            'password': self.encrypt(password)
        }

        self.delete(self._make_api_url('user'), json=payload)
        self.token = None

    def change_username(self, new_username: str) -> str:
        """
        Смена имени пользователя (логина)
        При этом происходит завершение всех активных сеансов, кроме текущего
        По текущему сеансу будет перевыпущен токен, текущий токен станет недействительным.
        Новый токен вернет этот метод
        """

        payload = {'new_username': new_username}
        resp = self.patch(self._make_api_url('user/username'), json=payload)
        data = resp.json()
        self.token = data.get('access_token')
        return self.token

    def change_password(self, curr_password: str, new_password: str, close_sessions: bool = False):
        payload = {
            'password': self.encrypt(curr_password),
            'new_password': self.encrypt(new_password),
            'close_sessions': close_sessions
        }

        self.patch(self._make_api_url('user/passwd'), json=payload)

    def save_user_data(self, user: Player) -> Player:
        resp = self.patch(self._make_api_url('user'), json=self._dump_player(user))
        return self._make_player(resp.json())

    def save_avatar(self, file_path: str) -> Player:
        files = {
            'file': (os.path.split(file_path)[1], open(file_path, 'rb'))
        }

        resp = self.put(self._make_api_url('user/avatar'), files=files)
        return self._make_player(resp.json())

    def clear_avatar(self) -> Player:
        resp = self.delete(self._make_api_url('user/avatar'))
        return self._make_player(resp.json())

    def get_params(self) -> dict:
        try:
            resp = self.get(self._make_api_url('user/params'))
        except ClientException as err:
            if err.status_code != 404:
                raise
            else:
                return {}

        return resp.json()

    def set_params(self, params: Params):
        self.put(self._make_api_url('user/params'), json=params.as_dict())

    def get_game_options(self) -> dict:
        try:
            resp = self.get(self._make_api_url('user/game_options'))
        except ClientException as err:
            if err.status_code != 404:
                raise
            else:
                return {}

        return resp.json()

    def set_game_options(self, options: Options):
        self.put(self._make_api_url('user/game_options'), json=options.as_dict())

    def download_avatar(self, remote_path: str, save_to_path: str):
        resp = self.get(self._make_base_url(f'{self.FILES_BASE_PATH}/{remote_path}'))

        if len(resp.content) > 0:
            with open(save_to_path, 'wb') as f:
                f.write(resp.content)
        else:
            raise ClientException(500, 'No content', response=resp)
