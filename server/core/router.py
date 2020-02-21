import logging
import controllers


class Router(object):

    __methods = ('get', 'post', 'put', 'delete', 'head', 'options', 'patch', 'copy', 'link', 'unlink', 'purge', 'lock',
                 'unlock', 'propfind', 'view')
    __reg_error = 'Cannot register handler for route "{0} {1}"! {2}\nProcessed: {3}.{4}'
    __reg_conflict = 'Cannot register handler for route "{0} {1}"! {2}\nProcessed: {3}.{4}\nRegistered: {5}.{6}'
    __found_endpoint = 'Found endpoint :: {0} {1} : {2}.{3}'

    def __init__(self):
        # {'/url/for/route': (type:str, function:callable, params:[], class, method)}
        # types: A: absolute, V: variable, S: starting with
        self._roadmap = {k: {} for k in self.__methods}
        self._build_roadmap()

    def _build_roadmap(self):
        for cls in dir(controllers):
            if not cls.startswith('_'):
                obj = eval(f'controllers.{cls}')

                if str(type(obj)).startswith('<class'):
                    for attr in obj.__dict__:
                        if not attr.startswith('_') and type(obj.__dict__[attr]) == staticmethod:
                            func = eval(f'controllers.{cls}.{attr}')
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

    def _add(self, path, method, func, class_name, attr_name):
        if not path or not path.startswith('/'):
            raise Exception(self.__reg_error.format(method.upper(), path, 'Bad url address!', class_name, attr_name))

        type_ = 'A'
        params = []
        path = path.lower().strip()
        method = method.lower().strip()

        if method not in self.__methods:
            raise Exception(self.__reg_error.format(method.upper(), path, 'Method not allowed!', class_name, attr_name))

        if path.find('<') > -1:
            type_ = 'V'
            for i, p in enumerate(path.split('/')):
                if p.startswith('<'):
                    params.append(i)
        elif path.endswith('*'):
            type_ = 'S'

        self._raise_if_double(method, path, class_name, attr_name)
        logging.debug(self.__found_endpoint.format(method.upper(), path, class_name, attr_name))
        self._roadmap[method][path] = (type_, func, params, class_name, attr_name)

    def _raise_if_double(self, method, path, class_name, attr_name):
        key, obj = self._get(method, path)

        if obj and obj[0] != 'S' and (obj[3] != class_name or obj[4] != attr_name):
            raise Exception(self.__reg_conflict.format(
                method.upper(), path, 'Route already registered!', class_name, attr_name, obj[3], obj[4]))

    def _find_var(self, method, path):
        for tmpl in self._roadmap[method]:
            if self._roadmap[method][tmpl][0] == 'V':
                if self._match(tmpl, path):
                    return tmpl

        return None

    def _find_starts(self, method, path):
        for tmpl in self._roadmap[method]:
            if self._roadmap[method][tmpl][0] == 'S':
                if path.startswith(tmpl.replace('*', '')):
                    return tmpl

        return None

    def _get(self, method, path):
        path = path.lower()
        method = method.lower()
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

    def _match(self, template, path):
        tmpl_parts = template.split('/')
        path_parts = path.split('/')

        if len(tmpl_parts) != len(path_parts):
            return False

        for i, p in enumerate(tmpl_parts):
            if p != path_parts[i] and not p.startswith('<'):
                return False

        return True

    def register(self, routes, methods, func, class_name, attr_name):
        for path in routes:
            if not methods:
                methods = [s for s in self.__methods]

            for method in methods:
                self._add(path, method, func, class_name, attr_name)

    def get(self, method, path):
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


roadmap = Router()
