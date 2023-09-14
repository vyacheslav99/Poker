import logging

from functools import wraps
from typing import Union, Optional, Tuple, List, Callable, Dict
from dataclasses import dataclass
from marshmallow import Schema

from server.helpers import HttpMethods, Request, Response, SecurityProvider


@dataclass
class EndpointMeta:
    security: Tuple[SecurityProvider] = None
    query_schema: Schema = None
    body_schema: Schema = None
    response_schema: Schema = None


class Router:

    def __init__(self, api_prefix: str = None):
        self._api_prefix = api_prefix
        self._items: List[Dict] = []

    def __getitem__(self, key):
        return self._items[key]

    def endpoint(self, rule: str, methods: Union[str, List[str]], security: Tuple[SecurityProvider] = None,
                 query_schema: Schema = None, body_schema: Schema = None, response_schema: Schema = None):
        def _prepare_body(body, resp_schema):
            if hasattr(body, 'as_dict'):
                body = body.as_dict()
            elif hasattr(body, 'asdict'):
                body = body.asdict()

            return dict(success=True, result=resp_schema.dump(body))

        def wrapper(func):
            @wraps(func)
            def wrapped(*args, **kwargs):
                request: Request = args[0]
                meta: EndpointMeta = kwargs.pop('__metadata__', None)

                if meta:
                    if meta.query_schema:
                        request._params = meta.query_schema.load(request.params)
                    if meta.body_schema:
                        request._json = meta.body_schema.load(request.json)

                    for provider in meta.security or []:
                        provider.exec(request)

                response = func(*args, **kwargs)

                if meta and meta.response_schema:
                    if isinstance(response, Response):
                        if response.status < 400:
                            response.body = _prepare_body(response.body, meta.response_schema)
                    elif isinstance(response, tuple):
                        if response[-1] < 400:
                            response = (_prepare_body(response[0], meta.response_schema), *response[1:])
                    else:
                        response = _prepare_body(response, meta.response_schema)

                return response

            self._items.append({
                'rule': f'{self._api_prefix or ""}{rule}',
                'methods': methods,
                'func': wrapped,
                'meta': EndpointMeta(
                    security=security,
                    query_schema=query_schema,
                    body_schema=body_schema,
                    response_schema=response_schema
                )
            })

            return wrapped

        return wrapper


class ApiDispatcher:

    _instance = None
    _roadmap = {}
    __methods = tuple(v for v in HttpMethods)
    __reg_error = 'Cannot register handler for route "{0} {1}"! {2}\nProcessed: {3}.{4}'
    __reg_conflict = 'Cannot register handler for route "{0} {1}"! {2}\nProcessed: {3}.{4}\nRegistered: {5}.{6}'
    __found_endpoint = 'Found endpoint :: {0} {1} : {2}.{3}'

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(ApiDispatcher, cls).__new__(cls)
            cls._instance._roadmap = {k: {} for k in cls.__methods}

        return cls._instance

    def collect_package(self, package):
        for cls in dir(package):
            if not cls.startswith('_'):
                obj = getattr(package, cls)

                if str(type(obj)).startswith('<class') and str(type(obj)) != "<class 'module'>":
                    self.register_class(obj)

    def register_class(self, controller_class):
        for attr in dir(controller_class):
            if not attr.startswith('_') and type(controller_class.__dict__.get(attr)) == staticmethod:
                func = getattr(controller_class, attr)
                doc = func.__doc__

                if doc:
                    routes = []
                    methods = []

                    for line in doc.split('\n'):
                        if ':route:' in line:
                            routes.append(line.split(':route:')[1].strip())
                        if ':methods:' in line:
                            methods.extend(line.split(':methods:')[1].strip().split(','))

                    self.register(routes, methods, func, class_name=controller_class.__name__, attr_name=attr)

    def register(self, routes: List[str], methods: List[str], func: Callable, class_name: str = None, attr_name: str = None):
        for path in routes:
            if not methods:
                methods = [s for s in self.__methods]

            for method in methods:
                try:
                    self.add(path, method, func, EndpointMeta(), class_name=class_name, attr_name=attr_name)
                except Exception as e:
                    logging.exception('Route registration error', exc_info=e)

    def collect(self, collection: Router):
        for obj in collection:
            if isinstance(obj['methods'], str):
                obj['methods'] = [obj['methods']]

            for method in obj['methods']:
                try:
                    self.add(obj['rule'], method, obj['func'], obj['meta'], '<module>', str(obj['func']).split(' ')[1])
                except Exception as e:
                    logging.exception('Route registration error', exc_info=e)

    def add(self, path: str, method: str, func: Callable, meta: EndpointMeta, class_name: str = None, attr_name: str = None):
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
        self._roadmap[method][path] = {
            'type': type_,
            'func': func,
            'params': params,
            'meta': meta,
            'class': class_name,
            'attr': attr_name
        }

    def get(self, method: str, path: str) -> Tuple[Optional[Callable], Optional[List[str]], Optional[EndpointMeta]]:
        params = []
        key, obj = self._get(method, path)

        if not obj:
            return None, None, None

        if obj['type'] == 'V':
            parts = path.split('/')
            params = [parts[i] for i in obj['params']]
        elif obj['type'] == 'S':
            params = [path.replace(key.replace('*', ''), '')]

        return obj['func'], params, obj['meta']

    def _raise_if_exists(self, type_, method: str, path: str, class_name: str, attr_name: str):
        key, obj = self._get(method, path)

        if key:
            if (obj['type'] in ['S', 'A'] and key == path) or (obj['type'] == 'V' and type_ == 'V'):
                raise Exception(self.__reg_conflict.format(
                    method, path, 'Route already registered!', class_name, attr_name, obj['class'], obj['attr']))

    def _find_var(self, method: str, path: str) -> Optional[str]:
        for tmpl in self._roadmap[method]:
            if self._roadmap[method][tmpl]['type'] == 'V':
                if self._match(tmpl, path):
                    return tmpl

        return None

    def _find_starts(self, method: str, path: str) -> Optional[str]:
        for tmpl in self._roadmap[method]:
            if self._roadmap[method][tmpl]['type'] == 'S':
                if path.startswith(tmpl.replace('*', '')):
                    return tmpl

        return None

    def _get(self, method: str, path: str) -> Tuple[str, dict]:
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