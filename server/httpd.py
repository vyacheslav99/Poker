import logging
import argparse

from core import config
from core.http_server import HTTPServer


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", "-p", type=int, action="store", default=config.PORT)
    ap.add_argument("--workers", "-w", type=int, action="store", default=config.INIT_HANDLERS)
    ap.add_argument("--doc_root", "-r", type=str, action="store", default=config.DOCUMENT_ROOT)
    args = ap.parse_args()
    config.DOCUMENT_ROOT = args.doc_root

    logging.basicConfig(**config.LOGGING)
    server = HTTPServer(config.LISTEN_ADDR, args.port, args.workers, config.MAX_HANDLERS)

    logging.info("Starting server...")
    server.start()
    logging.info("Server stopped")

if __name__ == '__main__':
    main()
