# -*- coding: utf-8 -*-

import os
import logging
import traceback
import datetime, time
import mimetypes, urllib2
import socket, errno

import config


class Request(object):

    def __init__(self, request_str):
        self._raw_request = request_str
        self._method = None
        self._uri = None
        self._protocol = None
        self._params = {}
        self._headers = {}
        self._body = None
        self._parse_request_str()

    def _parse_request_str(self):
        data = self._raw_request.split('\r\n')
        logging.debug(data[0])
        self._method, self._uri, self._protocol = data[0].split(' ')

        uri = self._uri.split('/')
        uri.pop(0)
        self._uri = '/{}'.format('/'.join(uri))
        if self._uri.find('?') > -1:
            self._uri, params = self._uri.split('?')

            params = params.split('&')
            for param in params:
                p, v = param.split('=', 1)
                self._params[p] = v

        self._uri = urllib2.unquote(self._uri)

        data.pop(0)
        while True:
            row = data.pop(0)
            if row == '':
                break

            p, v = row.split(':', 1)
            self._headers[p.strip()] = v.strip()

        self._body = '\r\n'.join(data)

    @property
    def method(self):
        return self._method

    @property
    def uri(self):
        return self._uri

    @property
    def protocol(self):
        return self._protocol

    @property
    def host(self):
        return self._headers.get('Host', None)

    @property
    def params(self):
        return self._params

    @property
    def headers(self):
        return self._headers

    @property
    def body(self):
        return self._body


class Response(object):

    def __init__(self, protocol, code, status, headers=None, body=None):
        self._protocol = protocol
        self._code = code
        self._status = status
        self._headers = headers or {}
        self._body = body or ''

    @property
    def protocol(self):
        return self._protocol

    @property
    def code(self):
        return self._code

    @property
    def status(self):
        return self._status

    @property
    def headers(self):
        return self._headers

    @property
    def body(self):
        return self._body if isinstance(self._body, str) else str(self._body)

    @protocol.setter
    def protocol(self, protocol):
        self._protocol = protocol

    @code.setter
    def code(self, code):
        self._code = code

    @status.setter
    def status(self, status):
        self._status = status

    @headers.setter
    def headers(self, headers):
        self._headers = dict(headers)

    def set_header(self, key, value):
        self._headers[key] = value

    @body.setter
    def body(self, body):
        self._body = body

    def __str__(self):
        data = ['{0} {1} {2}'.format(self._protocol, self._code, self._status)]
        data.extend('{0}: {1}'.format(*head) for head in self._headers.items())
        data.append('')
        if self._body is not None:
            data.append(self._body if isinstance(self._body, str) else str(self._body))

        return '\r\n'.join(data)


class Handler(object):
    """ Класс обработчик соединения с клиентом """

    __log_format_str = '[{thread_id}] - {client_ip}:{client_port} "{method} {uri} {protocol}" {code} {len_response}'

    __index_page_tmpl = '\r\n'.join(('<!doctype html>', '<html>', '<head>', '<meta content="text/html; charset=utf-8">',
                                     '<title>Content of directory "{directory}"</title>', '</head>', '<body>',
                                     '<h3>Content of directory "{directory}"</h3>',
                                     '<table border="1", bordercolor="whitesmoke", cellspacing="0" cellpadding="3">',
                                     '<thead>', '<tr>', '<td>File Name</td>', '<td>Type</td>', '<td>Size</td>',
                                     '<td>Created</td>', '<td>Modified</td>', '</tr>', '</thead>', '<tbody>', '{tbody}',
                                     '</tbody>', '</table>', '</body>', '</html>'))

    __table_row_tmpl = '\r\n'.join((
        '<tr>', '<td>{file_name}</td>', '<td>{file_type}</td>', '<td>{file_size}</td>', '<td>{fcreated}</td>',
        '<td>{fmodified}</td>', '</tr>'))

    __error_page_tmpl = '\r\n'.join(('<!doctype html>', '<html>', '<head>', '<meta content="text/html; charset=utf-8">',
                                     '<title>{code} {title}</title>', '</head>', '<body>', '<h1>{title}</h1>', '<p>',
                                     '{error_message}', '</p>', '</body>', '</html>'))

    def __init__(self, worker_id, sock, client_ip, client_port):
        self.id = worker_id
        self.__can_stop = False
        self.sock = sock
        self.client_ip = client_ip
        self.client_port = client_port
        self.raw_request = b''
        self.raw_response = b''
        self.request = None
        self.response = None

    def _sizeof_fmt(self, size):
        kb = 1024.0
        mb = kb * 1024.0
        gb = mb * 1024.0
        tb = gb * 1024.0
        if size <= kb:
            return '{0} byte(s)'.format(str(size))
        elif (size > kb) and (size <= mb):
            return '{0} Kb'.format(str(round(size / kb, 2)))
        elif (size > mb) and (size <= gb):
            return '{0} Mb'.format(str(round(size / mb, 2)))
        elif (size > gb) and (size <= tb):
            return '{0} Gb'.format(str(round(size / gb, 2)))
        elif size > tb:
            return '{0} Tb'.format(str(round(size / tb, 2)))
        else:
            return str(size)

    def _get_headers(self):
        return {
            'Date': datetime.datetime.today().strftime("%a, %d %b %Y %H:%M %Z"),
            'Server': 'MyServer/1.0.0',
            'Content-Length': 0,
            'Content-Type': 'text/plain',
            #'Content-Encoding': 'utf-8',
            'Connection': 'close'
        }

    def _get_request_method(self):
        # вытягивает метод из исходной строки запроса, если запрос не удалось распарсить, иначе из запроса
        if self.request:
            return self.request.method
        else:
            return self.raw_request.split('\r\n')[0].split(' ')[0] or 'GET'

    def _render_directory_index(self, path):
        files = []
        folders = []
        full_item = ''

        up_path = path.replace(config.DOCUMENT_ROOT, '')
        if up_path and up_path != '/':
            up_path = os.path.split(up_path)[0]
        folders.append(self.__table_row_tmpl.format(
            file_name='<a href={0}>{1}</a>'.format(urllib2.quote(up_path) or '/', '&lt;UP&gt;'), file_type='&lt;dir&gt;', file_size='',
            fcreated='', fmodified=''))

        for item in os.listdir(path):
            if self.__can_stop: break
            try:
                full_item = os.path.join(path, item).replace('\\', '/')
                if os.path.isdir(full_item):
                    folders.append(self.__table_row_tmpl.format(
                        file_name='<a href={0}>{1}</a>'.format(urllib2.quote(full_item.replace(config.DOCUMENT_ROOT, '')), item),
                        file_type='&lt;dir&gt;', file_size='',
                        fcreated=datetime.datetime.fromtimestamp(os.path.getctime(full_item)).strftime("%d.%m.%Y %H:%M:%S"),
                        fmodified=datetime.datetime.fromtimestamp(os.path.getmtime(full_item)).strftime("%d.%m.%Y %H:%M:%S")))
                else:
                    files.append(self.__table_row_tmpl.format(
                        file_name='<a href={0}>{1}</a>'.format(urllib2.quote(full_item.replace(config.DOCUMENT_ROOT, '')), item),
                        file_type=self._get_content_type(full_item), file_size=self._sizeof_fmt(os.path.getsize(full_item)),
                        fcreated=datetime.datetime.fromtimestamp(os.path.getctime(full_item)).strftime("%d.%m.%Y %H:%M:%S"),
                        fmodified=datetime.datetime.fromtimestamp(os.path.getmtime(full_item)).strftime("%d.%m.%Y %H:%M:%S")))
            except Exception:
                logging.exception('[{0}] Cannot access to file/folder "{1}"'.format(self.id, full_item))

        folders.extend(files)
        return self.__index_page_tmpl.format(directory=path.replace(config.DOCUMENT_ROOT, ''), tbody='\r\n'.join(folders))

    def _wrap_error(self):
        html = self.__error_page_tmpl.format(code=self.response.code, title=self.response.status,
            error_message=self.response.body.replace('\r\n', '<br>').replace('\n', '<br>') if self.response.body else '')
        self.response.headers = self._get_headers()
        self.response.set_header('Content-Type', 'text/html')
        self.response.set_header('Content-Length', len(html))
        self.response.body = html

    def _get_content_type(self, file_name):
        return mimetypes.guess_type(file_name)[0] or 'application/octet-stream'

    def _create_file_response(self, method, file_name, file_data=None):
        resp = Response(self.request.protocol, 200, 'OK', headers=self._get_headers())

        if not file_data and method == 'GET':
            with open(file_name, 'rb') as f:
                file_data = f.read()

        resp.set_header('Content-Length', len(file_data) or (os.path.getsize(file_name) if os.path.exists(file_name) else 0))
        resp.set_header('Content-Type', self._get_content_type(file_name))
        if method == 'GET':
            resp.body = file_data

        return resp

    def _create_response(self):
        if self.__can_stop:
            return None

        if not self.raw_request:
            return Response('HTTP/1.1', 400, 'Bad request')

        try:
            self.request = Request(self.raw_request)

            if self.request.method not in ('GET', 'HEAD'):
                return Response(self.request.protocol, 405, 'Method Not Allowed')

            # Действия по get-запросу (на head-запрос все то же, только блок body в response оставляем пустым):
            # 1. если адрес запроса (uri) - папка: если такой путь есть в document_root и там есть index.html -
            # надо вернуть index.html из нее, если index-а нет - вернуть стандартный index (рендерим свой шаблон),
            # который будет содержать ссылки на список файлов и папок папки, и ссылку на переход в папку верхнего уровня.
            # Если такой папки нет - вернем 404.
            # 2. если uri - файл: если такой файл есть по этому пути - вернуть содержимое этого файла, при этом правильно
            # определить и передать его content-type (в т.ч. под эту логику и подпадает условие на счет file.html).
            # Если пути uri не существует - вернуть 404.
            # Параметры запроса игнорируем (по условию задачи).
            path = '{0}{1}'.format(config.DOCUMENT_ROOT, self.request.uri)
            if os.path.exists(path):
                if os.path.isdir(path):
                    if os.path.exists(os.path.join(path, 'index.html')):
                        return self._create_file_response(self.request.method, os.path.join(path, 'index.html'))

                    return self._create_file_response(self.request.method, 'index.html',
                                                      file_data=self._render_directory_index(path))
                else:
                    return self._create_file_response(self.request.method, path)
            else:
                return Response(self.request.protocol, 404, 'Not Found')
        except Exception as e:
            logging.exception('[{0}] Error on prepare response to {1}:{2}'.format(self.id, self.client_ip, self.client_port))
            return Response('HTTP/1.1', 500, 'Internal Server Error',
                body=(traceback.format_exc() if config.DEBUG else e) if self._get_request_method() != 'HEAD' else None)

    def _read_request(self):
        while not self.__can_stop:
            try:
                data = self.sock.recv(1024)
            except socket.error as e:
                if e.errno == errno.WSAEWOULDBLOCK:
                    time.sleep(0.1)
                    continue
                else:
                    raise

            self.raw_request += data
            if len(data) < 1024:
                break

    def _do_work_request(self):
        self.response = self._create_response()
        if self.response:
            # если response - ошибка, нужно вернуть страницу ошибки (рендерим свой шаблон)
            if self.response.code != 200 and self._get_request_method() != 'HEAD':
                self._wrap_error()
            self.raw_response = str(self.response)
            logging.info(self.__log_format_str.format(thread_id=self.id, client_ip=self.client_ip,
                                                      client_port=self.client_port,
                                                      method=self._get_request_method(),
                                                      uri=self.request.uri if self.request else '/',
                                                      protocol=self.response.protocol,
                                                      code=self.response.code, len_response=len(self.raw_response)))

    def _send_response(self):
        while not self.__can_stop:
            n = self.sock.send(self.raw_response)
            if n == len(self.raw_response):
                break
            self.raw_response = self.raw_response[n:]

    # def _close(self):
    #     self.sock.close()
    #     self.sock = None

    def handle_request(self):
        try:
            self._read_request()
            self._do_work_request()
            self._send_response()
            #self._close() #  закрывать коннект будем в worker-е
        except Exception:
            logging.exception('[{0}] Error on handle request at {1}:{2}'.format(self.id, self.client_ip, self.client_port))

    def stop(self):
        self.__can_stop = True
