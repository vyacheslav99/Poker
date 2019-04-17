import os
import logging
import argparse

from core import config
from core.http_server import HTTPServer


def main():
    if not os.path.exists(config.DOCUMENT_ROOT):
        os.makedirs(config.DOCUMENT_ROOT, exist_ok=True)

    ap = argparse.ArgumentParser()
    ap.add_argument('--listen_addr', '-a', help=f'Хост сервера. По умолчанию {config.LISTEN_ADDR}')
    ap.add_argument("--port", "-p", type=int, help=f'Порт сервера. По умолчанию {config.PORT}')
    ap.add_argument("--log_file", "-l", type=str, help='Перенаправить вывод логов указанный файл. '
                                                       'Если не задан, логи будут писаться в консоль')
    args = ap.parse_args()

    if args.log_file:
        config.LOGGING['filename'] = args.log_file

    logging.basicConfig(**config.LOGGING)
    server = HTTPServer(args.listen_addr or config.LISTEN_ADDR, args.port or config.PORT,
                        config.INIT_HANDLERS, config.MAX_HANDLERS)

    logging.info("Starting server...")
    server.start()
    logging.info("Server stopped")

if __name__ == '__main__':
    main()
