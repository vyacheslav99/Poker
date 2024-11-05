import yoyo
from api import config


def main():
    backend = yoyo.get_backend(config.YOYO_DB_DSN)
    migrations = yoyo.read_migrations('migrations')

    with backend.lock():
        backend.apply_migrations(backend.to_apply(migrations))


if __name__ == '__main__':
    main()
