import os
import platform
import uuid

import rsa
import base64
import requests
import logging

from requests import Response
from requests.exceptions import RequestException

from gui import config
from gui.common import const
from models.params import Params, Options
from models.player import Player


class ClientException(RequestException):

    def __init__(self, status: int, message: str, response: Response):
        super().__init__(response=response)

        self.status_code: int = status
        self.message: str = message


class BaseClient:

    def __init__(self, host: str | None):
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

    @property
    def base_host(self) -> str | None:
        return self._host

    @base_host.setter
    def base_host(self, value: str | None):
        self._host = value

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
                try:
                    text = response.text
                except Exception:
                    pass

            if not text:
                text = response.reason

            raise ClientException(response.status_code, text, response=response)

    def _request(
        self,
        method: str,
        endpoint: str,
        by_api: bool = True,
        query: dict | None = None,
        json: dict | None = None,
        files = None,
        headers: dict | None = None
    ) -> Response:
        url = self._make_url(endpoint, by_api=by_api)

        try:
            resp = getattr(requests, method)(
                url, params=query, json=json, files=files, headers=dict(self.get_default_headers(), **(headers or {})),
                timeout=config.REQUEST_TIMEOUT
            )

            logging.debug(f'client request: {method.upper()} {url} - {resp.status_code} {len(resp.content)}')
            self.raise_for_status(resp)
            return resp
        except ClientException as e:
            logging.error(f'client error: {method.upper()} {url} - {e.status_code} {e.message}')
            raise e
        except Exception as e:
            logging.error('server error', exc_info=e)
            raise e

    def _make_url(self, endpoint: str, by_api: bool = True) -> str:
        if by_api:
            prefix = 'api/'
        else:
            prefix = ''

        return f"{self._host}/{prefix}{endpoint.lstrip('/')}"

    def get(
        self, endpoint: str, by_api: bool = True, query: dict | None = None, headers: dict | None = None
    ) -> Response:
        return self._request('get', endpoint, by_api=by_api, query=query, headers=headers)

    def post(
        self, endpoint: str, by_api: bool = True, json: dict | None = None, files = None, headers: dict | None = None
    ) -> Response:
        return self._request('post', endpoint, by_api=by_api, json=json, files=files, headers=headers)

    def put(
        self, endpoint: str, by_api: bool = True, json: dict | None = None, files = None, headers: dict | None = None
    ) -> Response:
        return self._request('put', endpoint, by_api=by_api, json=json, files=files, headers=headers)

    def patch(
        self, endpoint: str, by_api: bool = True, json: dict | None = None, files = None, headers: dict | None = None
    ) -> Response:
        return self._request('patch', endpoint, by_api=by_api, json=json, files=files, headers=headers)

    def delete(
        self, endpoint: str, by_api: bool = True, query: dict | None = None, json: dict | None = None,
        headers: dict | None = None
    ) -> Response:
        return self._request('delete', endpoint, by_api=by_api, query=query, json=json, headers=headers)

    def encrypt(self, plain_value: str) -> str:
        if not self._public_key:
            self.load_public_key()

        pubkey = rsa.PublicKey.load_pkcs1(self._public_key.encode())
        cipher = rsa.encrypt(plain_value.encode(), pubkey)
        b64_value = base64.urlsafe_b64encode(cipher)
        return b64_value.decode()

    def load_public_key(self):
        resp = self.get('public-key')
        self._public_key = resp.text


class GameServerClient(BaseClient):

    FILES_BASE_PATH = '/static/files'
    USER_PATH = '/user'
    USER_AVATAR_PATH = f'{USER_PATH}/avatar'
    USER_PARAMS_PATH = f'{USER_PATH}/params'
    USER_OPTIONS_PATH = f'{USER_PATH}/game_options'

    def is_alive(self) -> tuple[bool, str]:
        try:
            resp = self.get('/is_alive', by_api=False)
            data = resp.json()

            if {'server', 'version', 'status'} == set(data.keys()):
                return True, '\n'.join([data[k] for k in data])
            else:
                return False, 'Incompatible server'
        except RequestException as e:
            return False, 'Server unavailable'

    def username_is_free(self, username: str) -> bool:
        resp = self.get('/is_free_username', query={'username': username})
        data = resp.json()
        return data['success']

    def _load_player(self, data: dict, set_current_token: bool = True) -> Player:
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

        resp = self.post(self.USER_PATH, json=payload)
        return self._load_player(resp.json(), set_current_token=False)

    def get_user(self) -> Player:
        resp = self.get(self.USER_PATH)
        return self._load_player(resp.json())

    def authorize_safe(self, username: str, password: str) -> str:
        payload = {
            'username': username,
            'password': self.encrypt(password)
        }

        resp = self.post('/login', json=payload)
        data = resp.json()
        self.token = data.get('access_token')
        return self.token

    def logout(self):
        self.post('/logout')
        self.token = None

    def delete_user(self, password: str):
        payload = {
            'password': self.encrypt(password)
        }

        self.delete(self.USER_PATH, json=payload)
        self.token = None

    def change_username(self, new_username: str) -> str:
        """
        Смена имени пользователя (логина)
        При этом происходит завершение всех активных сеансов, кроме текущего
        По текущему сеансу будет перевыпущен токен, текущий токен станет недействительным.
        Новый токен вернет этот метод
        """

        payload = {'new_username': new_username}
        resp = self.patch(f'{self.USER_PATH}/username', json=payload)
        data = resp.json()
        self.token = data.get('access_token')
        return self.token

    def change_password(self, curr_password: str, new_password: str, close_sessions: bool = False):
        payload = {
            'password': self.encrypt(curr_password),
            'new_password': self.encrypt(new_password),
            'close_sessions': close_sessions
        }

        self.patch(f'{self.USER_PATH}/passwd', json=payload)

    def save_user_data(self, user: Player) -> Player:
        resp = self.patch(self.USER_PATH, json=self._dump_player(user))
        return self._load_player(resp.json())

    def save_avatar(self, file_path: str) -> Player:
        files = {
            'file': (os.path.split(file_path)[1], open(file_path, 'rb'))
        }

        resp = self.put(self.USER_AVATAR_PATH, files=files)
        return self._load_player(resp.json())

    def clear_avatar(self) -> Player:
        resp = self.delete(self.USER_AVATAR_PATH)
        return self._load_player(resp.json())

    def get_params(self) -> dict:
        try:
            resp = self.get(self.USER_PARAMS_PATH)
        except ClientException as err:
            if err.status_code != 404:
                raise
            else:
                return {}

        return resp.json()

    def set_params(self, params: Params):
        self.put(self.USER_PARAMS_PATH, json=params.as_dict())

    def get_game_options(self) -> dict:
        try:
            resp = self.get(self.USER_OPTIONS_PATH)
        except ClientException as err:
            if err.status_code != 404:
                raise
            else:
                return {}

        return resp.json()

    def set_game_options(self, options: Options):
        self.put(self.USER_OPTIONS_PATH, json=options.as_dict())

    def download_avatar(self, remote_path: str, save_to_path: str):
        resp = self.get(f'{self.FILES_BASE_PATH}/{remote_path}', by_api=False)

        if len(resp.content) > 0:
            with open(save_to_path, 'wb') as f:
                f.write(resp.content)
        else:
            raise ClientException(500, 'No content', response=resp)

    def get_overall_statistics(
        self, include_user_ids: list[uuid.UUID] = None, sort_field: str = None, sort_desc: bool = None,
        limit: int = None
    ) -> list[Player]:
        """
        Получить статистику по всем игрокам

        Вернет статистику по первым :limit: игрокам, отсортированным по полю :sort_field:
        в указанном :sort_desc: порядке.
        Если есть авторизация - в списке всегда будет присутсвовать текущий авторизованный пользователь, независимо от
        его реального положения в общем списке с учетом сортировки.
        В список всегда будут включены пользователи с переданными в :include_user_ids: id пользователя, независимо от
        их реального положения в общем списке с учетом сортировки.

        :sort_field: поле сортировки на сервере, по умолчанию summary
        :sort_desc: направление сортировки на сервере, по умолчанию true (descending)
        :limit: сколько вернуть строк, по умолчанию 20. Вернет первые limit строк после применения сортировки
            + дополнительно включенных пользователей (авторизованного и явно перечисленных), независимо от того -
            попали они в limit или нет
        """

        query = {}

        if include_user_ids:
            query['include_user_ids'] = include_user_ids
        if sort_field:
            query['sort_field'] = sort_field
        if sort_desc:
            query['sort_desc'] = sort_desc
        if limit:
            query['limit'] = limit

        resp = self.get('/statistics', query=query)
        data = resp.json()

        return [Player(**row) for row in data['items']]

    def reset_user_statistics(self):
        """ Сброс статистики текущего авторизованного пользователя """

        self.delete(f'{self.USER_PATH}/statistics')
