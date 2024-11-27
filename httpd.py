import logging
import logging.config
import uvicorn
from fastapi import FastAPI

from api import create_app, config

app: FastAPI = create_app()


def main():
    # logging.basicConfig(**config.LOGGING)
    logging.config.dictConfig(config.LOGGING)
    logging.debug('Enabled DEDUG mode logging level!')

    uvicorn.run(
        'httpd:app',
        # app,
        host=config.LISTEN_ADDR,
        port=config.LISTEN_PORT,
        workers=config.WORKERS,
        log_level=logging.getLevelName(config.LOG_LEVEL).lower(),
    )


if __name__ == '__main__':
    main()
