import os
import logging
import uvicorn

from fastapi import FastAPI

from configs import config
from api.handlers import get_api_router


def create_app() -> FastAPI:
    app = FastAPI(debug=config.DEBUG, title=config.SERVER_NAME, version=config.SERVER_VERSION)
    app.include_router(get_api_router())
    return app


app = create_app()


def main():
    if not os.path.exists(config.DOCUMENT_ROOT):
        os.makedirs(config.DOCUMENT_ROOT, exist_ok=True)

    logging.basicConfig(**config.LOGGING)
    logging.debug('Enabled DEDUG mode logging level!')

    uvicorn.run(
        'httpd:app',
        # create_app(),
        host=config.LISTEN_ADDR,
        port=config.LISTEN_PORT,
        workers=config.WORKERS,
        log_level=logging.getLevelName(config.LOGGING['level']).lower()
    )


if __name__ == '__main__':
    main()
