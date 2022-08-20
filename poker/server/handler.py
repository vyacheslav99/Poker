import logging
import time
import socket, errno
import marshmallow

from typing import Optional, Tuple, List, Callable

from modules import utils
from server.helpers import Request, Response, HTTPException
from server.router import Router
from models.request import HttpMethods


class Handler(object):

    __log_format_str = '[{thread_id}] - {client_ip}:{client_port} "{method} {uri} {protocol}" {code} {len_response}'

    def __init__(self, worker_id: int, sock: socket.socket, client_ip: str, client_port: int):
        self.id: int = worker_id
        self.__can_stop = False
        self.sock: socket.socket = sock
        self.client_ip: str = client_ip
        self.client_port: int = client_port
        self.raw_request: bytes = b''
        self.raw_response: bytes = b''
        self.request: Optional[Request] = None
        self.response: Optional[Response] = None
        self.roadmap: Router = Router()  # get singleton obect

    def _route(self, addr: str, method: str) -> Tuple[Optional[Callable], Optional[List[str]]]:
        return self.roadmap.get(method, addr)

    def _get_request_method(self) -> str:
        # вытягивает метод из исходной строки запроса, если запрос не удалось распарсить, иначе из запроса

        if self.request:
            return self.request.method
        else:
            return utils.decode(self.raw_request).split('\r\n')[0].split(' ')[0] or HttpMethods.GET

    def _create_response(self) -> Optional[Response]:
        if self.__can_stop:
            return None

        if not self.raw_request:
            return self._error_response(400, 'Bad request', message='Request is empty')

        try:
            self.request = Request(self.raw_request)
            handler_, params = self._route(self.request.uri, self.request.method)

            if callable(handler_):
                resp = handler_(self.request, *params)

                if not isinstance(resp, Response):
                    if isinstance(resp, tuple):
                        if len(resp) == 3:
                            status, code, resp = resp[2], resp[1], resp[0]
                        elif len(resp) == 2:
                            status, code, resp = resp[1], 'OK', resp[0]
                        else:
                            status, code, resp = 200, 'OK', resp
                    else:
                        status, code, resp = 200, 'OK', resp

                    resp = Response(status, code, body=resp)

                return resp
            else:
                return self._error_response(405, 'Method Not Allowed',
                    message=f'Handler for route <{self.request.method} {self.request.uri}> not registered')
        except HTTPException as e:
            logging.exception('[{0}] Error on prepare response to {1}:{2}'.format(
                self.id, self.client_ip, self.client_port))
            return self._error_response(e.http_status, e.http_error, code=e.code, message=e.message)
        except marshmallow.exceptions.MarshmallowError as e:
            logging.exception('[{0}] Error request params or body validation to {1}:{2}'.format(
                self.id, self.client_ip, self.client_port))
            return self._error_response(400, 'Bad request', message=f'{e.__class__}: {e}')
        except Exception as e:
            logging.exception('[{0}] Unhandled exception on prepare response to {1}:{2}'.format(
                self.id, self.client_ip, self.client_port))
            return self._error_response(500, 'Internal Server Error', message=f'{e.__class__}: {e}')

    def _error_response(self, status: int, error: str, code: str = 'error', message: str = None) -> Response:
        body = None

        if self._get_request_method() != HttpMethods.HEAD and (code or message):
            body = {}
            if code:
                body['code'] = code
            if message:
                body['message'] = message

        return Response(status, error, body=body)

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
