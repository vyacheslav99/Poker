# Poker
Игра Расписной покер

Версия 1.0.0

Группа проектов

## Развертывание
Требования:
* python 3.6
* pipenv

#### Сервер
* создать файл конфига `config.py` в папке `poker/server/core`
скопировав `config.py.tmpl` в `config.py`

* настроить конфиг в файле

  `poker/server/core/config.py`
  
* запустить сервер командой:

  `pipenv run python httpd.py`
  
Параметры запуска:
* --debug_mode, -dbg: Включить вывод отладочной информации
* --listen_addr address, -a address: Хост сервера. По умолчанию config.LISTEN_ADDR
* --port port, -p port: Порт сервера. По умолчанию config.LISTEN_PORT
* --log_file filename, -l filename: Перенаправить вывод логов в указанный файл.
По умолчанию настройки логирования прописаны в конфиге

#### Клиент
* утановить/обновить зависимости одной из команд:
  * `pipenv install`
  * `pipenv update`

* создать файл конфига `config.py` в папке `poker/gui`
скопировав `config.py.tmpl` в `config.py`

* настроить конфиг в файле

  `poker/gui/config.py`

* запустить игру:

  `pipenv run python game.py`