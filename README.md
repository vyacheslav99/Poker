﻿# Poker
Игра Расписной покер

Версия 1.0.0

## Структура папок

* `/api` логика игрового сервера (web-сервис)
* `/configs` все конфиги приложения
* `/core` игровой движок
* `/doc` проектная документация
* `/domain` классы схемы и модели данных
* `/gui` оконное приложение `pyQt5`
* `/migrations` скрипты миграций БД
* `/resources` ресурсы для оконного приложения
* `/server` движок игрового сервера (web-сервис)

## Сервер

Требования:
* python >= 3.6

#### Развертывание

* утановить/обновить зависимости одной из команд:
  * `python -m pip install -r requirements.txt`
  * или для запуска через `pipenv`:
  * `pipenv install`
  * `pipenv update`
* создать файл конфига `config.py` в папке `configs/` скопировав `config.py.tmpl` в `config.py`
* настроить конфиг в полученном файле `configs/config.py`
* запустить сервер командой:

  `python httpd.py`
  * или для запуска через `pipenv`:
  `pipenv run python httpd.py`
  
Параметры запуска:
* --debug_mode, -dbg: Включить вывод отладочной информации
* --listen_addr address, -a address: Хост сервера. По умолчанию config.LISTEN_ADDR
* --port port, -p port: Порт сервера. По умолчанию config.LISTEN_PORT
* --log_file filename, -l filename: Перенаправить вывод логов в указанный файл.
По умолчанию настройки логирования прописаны в конфиге

## Приложения

#### gui

Требования:
* python 3.10
* pyQt5

Развертывание и запуск

* утановить/обновить зависимости одной из команд:
  * `python -m pip install -r requirements.txt`
  * или для запуска через `pipenv`:
  * `pipenv install`
  * `pipenv update`
* запустить игру:
  `python poker.py`
  * или для запуска через `pipenv`:
  `pipenv run python poker.py`
