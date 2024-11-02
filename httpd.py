import os
import logging
import uvicorn

from configs import config
# Не убирать этот импорт, так как переменная импортируется при старте сервера uvicorn-ом
# в ситуации, когда в метод uvicorn.run в качестве объекта сервера передается строка импорта ('httpd:app') а не объект.
# Такой способ нужен для того, чтобы можно было при старте передать workers более 1
from api import app


def main():
    if not os.path.exists(config.DOCUMENT_ROOT):
        os.makedirs(config.DOCUMENT_ROOT, exist_ok=True)

    logging.basicConfig(**config.LOGGING)
    logging.debug('Enabled DEDUG mode logging level!')

    uvicorn.run(
        'httpd:app',
        # app,
        host=config.LISTEN_ADDR,
        port=config.LISTEN_PORT,
        workers=config.WORKERS,
        log_level=logging.getLevelName(config.LOGGING['level']).lower(),
    )


if __name__ == '__main__':
    main()
