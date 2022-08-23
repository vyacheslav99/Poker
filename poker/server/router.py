import logging

from typing import Optional, Tuple, List, Callable

from domain.models.request import HttpMethods


class Router:

    _instance = None
    _roadmap = {}
    __methods = tuple(v for v in HttpMethods)
    __reg_error = 'Cannot register handler for route "{0} {1}"! {2}\nProcessed: {3}.{4}'
    __reg_conflict = 'Cannot register handler for route "{0} {1}"! {2}\nProcessed: {3}.{4}\nRegistered: {5}.{6}'
    __found_endpoint = 'Found endpoint :: {0} {1} : {2}.{3}'

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(Router, cls).__new__(cls)
            cls._instance._roadmap = {k: {} for k in cls.__methods}

        return cls._instance

    def collect(self, package):
        # {'/url/for/route': (type:str, function:callable, params:[], class, method)}
        # types: A: absolute, V: variable, S: starting with

        logging.info(dir(package))

        for cls in dir(package):
            if not cls.startswith('_'):
                obj = getattr(package, cls)

                if str(type(obj)).startswith('<class'):
                    for attr in dir(obj):
                        if not attr.startswith('_') and type(obj.__dict__.get(attr)) == staticmethod:
                            func = getattr(obj, attr)
                            doc = func.__doc__

                            if doc:
                                routes = []
                                methods = []

                                for line in doc.split('\n'):
                                    if ':route:' in line:
                                        routes.append(line.split(':route:')[1].strip())
                                    if ':methods:' in line:
                                        methods.extend(line.split(':methods:')[1].strip().split(','))

                                self.register(routes, methods, func, cls, attr)

    def _add(self, path: str, method: str, func: Callable, class_name: str, attr_name: str):
        if not path or not path.startswith('/'):
            raise Exception(self.__reg_error.format(method, path, 'Bad url address!', class_name, attr_name))

        type_ = 'A'
        params = []
        path = path.lower().strip()
        method = method.upper().strip()

        if method not in self.__methods:
            raise Exception(self.__reg_error.format(method, path, 'Method not allowed!', class_name, attr_name))

        if path.find('<') > -1:
            type_ = 'V'
            for i, p in enumerate(path.split('/')):
                if p.startswith('<'):
                    params.append(i)
        elif path.endswith('*'):
            type_ = 'S'

        self._raise_if_exists(type_, method, path, class_name, attr_name)
        logging.debug(self.__found_endpoint.format(method, path, class_name, attr_name))
        self._roadmap[method][path] = (type_, func, params, class_name, attr_name)

    def _raise_if_exists(self, type_, method: str, path: str, class_name: str, attr_name: str):
        key, obj = self._get(method, path)

        if key:
            if (obj[0] in ['S', 'A'] and key == path) or (obj[0] == 'V' and type_ == 'V'):
                raise Exception(self.__reg_conflict.format(
                    method, path, 'Route already registered!', class_name, attr_name, obj[3], obj[4]))

    def _find_var(self, method: str, path: str) -> Optional[str]:
        for tmpl in self._roadmap[method]:
            if self._roadmap[method][tmpl][0] == 'V':
                if self._match(tmpl, path):
                    return tmpl

        return None

    def _find_starts(self, method: str, path: str) -> Optional[str]:
        for tmpl in self._roadmap[method]:
            if self._roadmap[method][tmpl][0] == 'S':
                if path.startswith(tmpl.replace('*', '')):
                    return tmpl

        return None

    def _get(self, method: str, path: str) -> Tuple[str, tuple]:
        path = path.lower()
        method = method.upper()
        key = path

        # абсолютное совпадение
        obj = self._roadmap[method].get(path)

        # поищем по шаблонам
        if obj is None:
            key = self._find_var(method, path)
            if key:
                obj = self._roadmap[method][key]

        # поищем начинающиеся с
        if obj is None:
            key = self._find_starts(method, path)
            if key:
                obj = self._roadmap[method][key]

        return key, obj

    def _match(self, template: str, path: str) -> bool:
        tmpl_parts = template.split('/')
        path_parts = path.split('/')

        if len(tmpl_parts) != len(path_parts):
            return False

        for i, p in enumerate(tmpl_parts):
            if p != path_parts[i] and not p.startswith('<'):
                return False

        return True

    def register(self, routes: List[str], methods: List[str], func: Callable, class_name: str | None, attr_name: str):
        for path in routes:
            if not methods:
                methods = [s for s in self.__methods]

            for method in methods:
                try:
                    self._add(path, method, func, class_name, attr_name)
                except Exception as e:
                    logging.exception('Route registration error', exc_info=e)

    def get(self, method: str, path: str) -> Tuple[Optional[Callable], Optional[List[str]]]:
        params = []
        key, obj = self._get(method, path)

        if not obj:
            return None, None

        if obj[0] == 'V':
            parts = path.split('/')
            params = [parts[i] for i in obj[2]]
        elif obj[0] == 'S':
            params = [path.replace(key.replace('*', ''), '')]

        return obj[1], params
