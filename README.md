# Poker
Игра Расписной покер

Версия 2.0.0

## Структура папок

* `/api` логика игрового сервера (web-сервис)
* `/core` игровой движок
* `/doc` проектная документация
* `/gui` оконное приложение `pyQt5`
* `/migrations` скрипты миграций БД
* `/models` модели движка
* `/resources` ресурсы для оконного приложения

## Сервер

Требования:
* python >= 3.10

#### Развертывание

* утановить/обновить зависимости через `pipenv`:
  * `pipenv install`
  * `pipenv update`
* создать файл конфига `config.py` в папке `api/` скопировав `config.py.tmpl` в `config.py`
* настроить конфиг в полученном файле `api/config.py`
* запустить сервер командой:

  `python httpd.py`
  * или для запуска через `pipenv`:
  `pipenv run python httpd.py`
  
## Приложения

#### gui (singleplayer)

Требования:
* python 3.10
* pyQt5

Развертывание и запуск

* утановить/обновить зависимости командой:
  * `pipenv install`
  * `pipenv update`
* создать файл настроек `poker.ini` скопировав `poker.ini.tmpl` в `poker.ini`
* настроить все что надо в полученном файле
* запустить игру:
  `python poker.py`
  * или для запуска через `pipenv`:
  `pipenv run python poker.py`

#### gui (multiplayer)

* все то же самое, что и в singleplayer, только запускать приложение с параметром `--mp`
  `pipenv run python poker.py --mp`