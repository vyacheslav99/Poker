import logging
import traceback
import time
import socket, errno
import json

from configs import config
from . import utils
from .helpers import Request, Response, HTTPException
from .router import Router


class Handler(object):

    __log_format_str = '[{thread_id}] - {client_ip}:{client_port} "{method} {uri} {protocol}" {code} {len_response}'

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
        self.roadmap = Router()  # get singleton obect

    def _route(self, addr, method):
        return self.roadmap.get(method, addr)

    def _get_request_method(self):
        # вытягивает метод из исходной строки запроса, если запрос не удалось распарсить, иначе из запроса

        if self.request:
            return self.request.method
        else:
            return utils.decode(self.raw_request).split('\r\n')[0].split(' ')[0] or 'GET'

    def _create_response(self):
        if self.__can_stop:
            return None

        if not self.raw_request:
            return self._error_response(400, 'Bad request', 'bad_request', 'Request is empty')

        try:
            self.request = Request(self.raw_request)
            handler_, params = self._route(self.request.uri, self.request.method)

            if callable(handler_):
                resp = handler_(self.request, *params)
                if not isinstance(resp, Response):
                    if isinstance(resp, (dict, list, tuple)):
                        resp = Response(200, 'OK', body=json.dumps(resp))
                    else:
                        resp = Response(200, 'OK', headers=Response.default_headers({'Content-Type': 'text/html'}), body=resp)
                return resp
            else:
                return self._error_response(405, 'Method Not Allowed', 'bad_request',
                                            f'Handler for route <{self.request.method} {self.request.uri}> not registered')
        except HTTPException as e:
            logging.exception('[{0}] Error on prepare response to {1}:{2}'.format(
                self.id, self.client_ip, self.client_port))
            return self._error_response(e.http_code, e.http_status, e.code, e.message)
        except Exception as e:
            logging.exception('[{0}] Unhandled exception on prepare response to {1}:{2}'.format(
                self.id, self.client_ip, self.client_port))
            return self._error_response(500, 'Internal Server Error', 'internal_error', f'{e.__class__}: {e}')

    def _error_response(self, code, status, err_code, err_message=None):
        return Response(code, status, body=json.dumps({'code': err_code, 'message': err_message})
                        if self._get_request_method() != 'HEAD' else None)

    def _read_request(self):
        while not self.__can_stop:
            try:
                data = self.sock.recv(1024)
            except socket.error as e:
                if e.errno == errno.EWOULDBLOCK:
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
            self.raw_response = bytes(self.response)
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
            # self._close() #  закрывать коннект будем в worker-е
        except Exception:
            logging.exception('[{0}] Error on handle request at {1}:{2}'.format(self.id, self.client_ip, self.client_port))

    def stop(self):
        self.__can_stop = True
