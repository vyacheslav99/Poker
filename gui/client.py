import requests

from typing import Tuple


class Client:

    def __init__(self, host):
        self._host = host
        self._base_url = f'{self._host}/api/v1'

    def is_alive(self) -> Tuple[bool, str]:
        try:
            res = requests.get(f'{self._base_url}/is_alive')
            data = res.json()

            if res.ok:
                if {'server', 'version', 'status'} == set(data.keys()):
                    return True, '\n'.join([data[k] for k in data])
                else:
                    return False, 'Bad response format'
            else:
                if data:
                    mes = data['error']['message']
                else:
                    mes = res.text

                return False, mes
        except Exception as e:
            return False, str(e)