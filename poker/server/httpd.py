import logging
import argparse

from poker.server.core import config
from poker.server.core.http_server import HTTPServer


def main():
    # todo: Перенести это потом в модуль хранилища
    # if not os.path.exists(config.DOCUMENT_ROOT):
    #     os.makedirs(config.DOCUMENT_ROOT, exist_ok=True)

    ap = argparse.ArgumentParser()
    ap.add_argument('--debug_mode', '-dbg', action='store_true', help='Включить вывод отладочной информации')
    ap.add_argument('--listen_addr', '-a', help=f'Хост сервера. По умолчанию {config.LISTEN_ADDR}')
    ap.add_argument("--port", "-p", type=int, help=f'Порт сервера. По умолчанию {config.LISTEN_PORT}')
    ap.add_argument("--log_file", "-l", type=str, help='Перенаправить вывод логов в указанный файл. '
                                                       'Если не задан, логи будут писаться в консоль')
    args = ap.parse_args()

    if args.log_file:
        config.LOGGING['filename'] = args.log_file

    if args.debug_mode:
        config.DEBUG = True
        config.LOGGING['level'] = logging.DEBUG

    logging.basicConfig(**config.LOGGING)
    server = HTTPServer(args.listen_addr or config.LISTEN_ADDR, args.port or config.LISTEN_PORT,
                        config.INIT_HANDLERS, config.MAX_HANDLERS)

    logging.debug("Enabled DEDUG mode logging level!")
    logging.info("Starting server...")
    server.start()
    logging.info("Server stopped")


if __name__ == '__main__':
    main()
