# Poker
Игра Расписной покер

Версия 1.0.0

Группа проектов

## Структура папок

* `/server` проект игрового сервера: `python`
* `/clients` проекты клиентов к серверу
    * `/console` консольный (для тестирования серверных api): `python`
    * `/gui` кросс-платформенный оконный клиент для ПК: `python`
    * `/mobile` мобильный клиент: `java (android sdk)`
    * `/web` браузерный клиент: `JavaScript (Ext?)`
    * `/windows` клиент для ПК на Windows: `Delphi`
* `/doc` проектная документация

## Сервер

Требования:
* python 3.6
* pipenv

#### Развертывание

* утановить/обновить зависимости одной из команд:
  * `pipenv install`
  * `pipenv update`

* создать файл конфига `config.py` в папке `server/`
скопировав `config.py.tmpl` в `config.py`

* настроить конфиг в файле

  `server/config.py`
  
* запустить сервер командой:

  `pipenv run python httpd.py`
  
Параметры запуска:
* --debug_mode, -dbg: Включить вывод отладочной информации
* --listen_addr address, -a address: Хост сервера. По умолчанию config.LISTEN_ADDR
* --port port, -p port: Порт сервера. По умолчанию config.LISTEN_PORT
* --log_file filename, -l filename: Перенаправить вывод логов в указанный файл.
По умолчанию настройки логирования прописаны в конфиге

## Клиент

#### gui

Требования:
* python 3.6
* pipenv

Развертывание и запуск

* утановить/обновить зависимости одной из команд:
  * `pipenv install`
  * `pipenv update`

* создать файл конфига `config.py` в папке `clients/gui`
скопировав `config.py.tmpl` в `config.py`

* настроить конфиг в файле

  `clients/gui/config.py`

* запустить игру:

  `pipenv run python game.py`