import socket, errno
import logging
import threading
import datetime, time
import random

from typing import Optional, Tuple, List

from configs import config
from server.handler import Handler
from server.router import Router
from server.dispatcher import Dispatcher


class Worker(object):

    def __init__(self, index: int):
        self.id = index
        self._queue: List[Tuple[str, int, socket.socket]] = []
        self._thread: Optional[threading.Thread] = None
        self._break = False
        self._handler: Optional[Handler] = None
        self._done = True
        self._locked = False
        self.last_used = datetime.datetime.now()
        self.init_thread()

    def _do_process(self):
        # данный метод вызывается из потока

        while not self._break:
            try:
                client_ip, client_port, sock = self._queue.pop(0)
            except IndexError:
                # без замораживания цикл вхолостую будет грузить процессор
                time.sleep(0.3)
                continue

            self._done = False
            try:
                logging.debug('[{0}] Accepted connection on {1}:{2}'.format(self.id, client_ip, client_port))

                self._handler = Handler(self.id, sock, client_ip, client_port)
                self._handler.handle_request()
            finally:
                sock.close()
                self._handler = None
                self._done = True
                logging.debug('[{0}] Stopped connection on {1}:{2}'.format(self.id, client_ip, client_port))

    def init_thread(self):
        self._thread = threading.Thread(target=self._do_process)
        self._thread.daemon = True
        self._thread.start()
        logging.debug('[{0}] Initialized Thread: {1}'.format(self.id, self._thread.name))

    def accept(self, sock: socket.socket, client_ip: str, client_port: int):
        self._queue.append((client_ip, client_port, sock))

    def stop(self):
        logging.debug('[{0}] Stop worker ({1})'.format(self.id, self._thread.name))
        self._break = True

        if self._handler:
            self._handler.stop()

        if self._thread and self._thread.is_alive():
            self._thread.join(0.5)

        for conn in self._queue:
            conn[2].close()

    def is_free(self) -> bool:
        return self._done

    def is_empty(self) -> bool:
        return len(self._queue) == 0

    def lock(self):
        self._locked = True

    def unlock(self):
        self._locked = False

    def locked(self) -> bool:
        return self._locked


class HTTPServer(object):

    def __init__(self, host: str, port: int, init_handlers: int = 0, max_handlers: int = 0):
        self.active = False
        self.sock: Optional[socket.socket] = None
        self.host: str = host
        self.port: int = port
        self.init_handlers: int = init_handlers
        self.max_handlers: int = max_handlers
        self.wrk_pool: List[Worker] = []
        self.wrk_svc_thread: Optional[threading.Thread] = None
        self.dispatcher: Optional[Dispatcher] = None

    def _init_socket(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen(5)
        self.sock.settimeout(1)
        logging.info('Started listening on {0}:{1}'.format(self.host, self.port))

    def _start_wrk_service(self):
        self.wrk_svc_thread = threading.Thread(target=self._do_wrk_service)
        self.wrk_svc_thread.daemon = True
        self.wrk_svc_thread.start()

    def _init_workers(self):
        for i in range(self.init_handlers):
            self.wrk_pool.append(Worker(i))

    def _get_worker(self) -> Optional[Worker]:
        for wrk in self.wrk_pool:
            if wrk.is_free() and not wrk.locked():
                wrk.last_used = datetime.datetime.now()
                return wrk

        if len(self.wrk_pool) < self.max_handlers:
            self.wrk_pool.append(Worker(len(self.wrk_pool) - 1))
            return self.wrk_pool[-1]

        # тут можно не сбрасывать коннект, а добавить в очередь любому занятому обработчику,
        # он его обработает, как только дойдет очередь
        if config.WHEN_REACHED_LIMIT == 0:
            return None
        else:  # elif config.WHEN_REACHED_LIMIT == 1:
            logging.debug('Delayed connection: limit connections exceeded')
            wrk = random.choice(self.wrk_pool)
            while wrk.locked():
                wrk = random.choice(self.wrk_pool)
            return wrk

    def _check_workers(self):
        if config.HANDLERS_CLEAN_POLICY != 0:
            # очистка лишних обработчиков.
            dt = datetime.datetime.now()
            i = 0

            while len(self.wrk_pool) > self.init_handlers and i < len(self.wrk_pool):
                self.wrk_pool[i].lock()
                if self.wrk_pool[i].is_free() and self.wrk_pool[i].is_empty() and (
                    config.HANDLERS_CLEAN_POLICY == 1 or (
                    config.HANDLERS_CLEAN_POLICY == 2 and
                    dt - self.wrk_pool[i].last_used > datetime.timedelta(minutes=config.HANDLERS_CLEAN_TIME))):
                    wrk = self.wrk_pool.pop(i)
                    wrk.stop()
                else:
                    self.wrk_pool[i].unlock()
                    i += 1

    def _accept_connection(self, sock: socket.socket, client_ip: str, client_port: int):
        worker = self._get_worker()

        if worker is None:
            sock.close()
            logging.info('Reset connection on {0}:{1}: limit connections exceeded'.format(client_ip, client_port))
        else:
            worker.accept(sock, client_ip, client_port)

    def _do_wrk_service(self):
        # выполняется в отдельном потоке!

        while self.active:
            try:
                self._check_workers()
                time.sleep(1)
            except Exception:
                logging.exception('Error at service workers!')

    def _do_serve_forever(self):
        while self.active:
            try:
                conn, addr = self.sock.accept()
            except socket.timeout:
                continue
            except IOError as e:
                if e.errno == errno.EINTR:
                    continue
                raise

            try:
                conn.setblocking(False)
                self._accept_connection(conn, *addr)
                # возврат завершившихся workers в пул вынесен в отдельный поток
                # self._check_workers()
            except Exception:
                logging.exception('Error on accept connection at {0}:{1}!'.format(*addr))

    def start(self):
        try:
            Router()  # init singleton object
            self.dispatcher = Dispatcher()
            self.active = True
            self._init_workers()
            self._start_wrk_service()
            self._init_socket()
            self._do_serve_forever()
        except KeyboardInterrupt:
            logging.info('KeyboardInterrupt')
        except Exception as e:
            logging.exception("Unexpected error: %s" % e)
        finally:
            self._close()

    def stop(self):
        self.active = False

    def _close(self):
        logging.info('Stop listen on {0}:{1}'.format(self.host, self.port))

        if self.sock:
            self.sock.close()

        if self.wrk_svc_thread and self.wrk_svc_thread.is_alive():
            self.wrk_svc_thread.join(0.5)

        for wrk in self.wrk_pool:
            wrk.stop()

        logging.info('Dumping games...')
        self.dispatcher.on_close()