Как регистрировать обработчиков маршрутов.

## Способ регистрации 1: Через классы-контроллеры

Класс-контроллер - это любой класс пакета, содержащий методы-обработчики маршрутов.
Чтобы метод класса был задействован для маршрутизации, он должны обладать следующими свойствами:
* Быть статическими (обернуты декоратором @staticmethod)
* Содержать в докстринге ключи, описывающие адрес и обрабатываемые методы запроса:
`:route:` обрабатываемый путь  
`:methods:` список обрабатываемых методов запроса  
Данные ключи можно помещать по нескольку раз в одну и ту же процедуру, тогда она просто будет назначена на все указанные адреса/методы.  
Только нужно следить, чтоб не конфликтовали параметры функции.  
Пути и методы запроса можно указывать в любом регистре.
* Принимать как минимум один параметр - первым параметром будет передан объект `helpers.Request`
* Последующими парамтры могут присутсвовать или нет, в зависимости от наличия их в обрабатываемом адресе

Метод-контроллер должен вернуть один из перечисленных вариантов:
* Экземпляр объекта `Response`
* Объект любого типа, без ошибок перобразующийся в json
* Последовательность из 3-х элементов: `object:json-like, code:str, status:int`
* Последовательность из 2-х элементов: `object:json-like, status:int`

Например:

Содержимое одного из модулей пакета (допустим `mycontroller.py`):

```python
class MyController(object):

    @staticmethod
    def sample_request(request, param1, param2, param3):
        '''
        Функция будет вызвана при обращении по любому из указанных в route адресу в сочетании с любым из указанных в
        methods методе.

        1. Обрабатываемые http-методы. Не обязателен.
        Если не указать этот параметр, будут обработаны все известные методы.
        Указать, но оставить пустым - НЕПРАВИЛЬНО. Возникнет ошибка регистрации.
        :methods: post, get

        2. Пути
        Все пути должны быть уникальными на уровне сервиса (в т.ч. и с учетом переменных, т.е. разное название переменных,
        расположенных одинаково не считается уникальным). Кроме путей, "начинающихся с". Такие пути будут всегда обработаны
        в последнюю очередь, если не было найдено других совпадений.

        2.1 Абсолютный путь.
        Метод будет вызван при полном совпаденни этого пути.
        :route: /api/v1/sample

        2.2 Путь с переменными.
        Части пути между / могут быть переменными (т.е. это шаблон пути).
        Чобы указать переменную, надо заключить слово в <>.
        Все переменные из пути должны присутствовать в параметрах процедуры в том же порядке, что и в пути,
        после первой переменной request, совпадение имен переменных пути и процедуры не обязательно.
        :route: /api/v1/req/<param1>/test/<param2>/<param3>

        2.3 Начинается с.
        Можно указать начальную часть пути. Это будет что-то вроде шаблона для пути по-умолчанию.
        Такой метод будет обработан для всех путей, начинающихся с указанного, если не было найдено других совпадений.
        Процедура обработчик должна принимать 2 параметра. Вторым параметром ей будет передана
        оставшаяся часть реального url, после той части, что совпала (все, что вместо * в реальном url).
        :route: /api/v1/file/*
        '''

        # return Response(200, 'OK', body={'code': 'success'})
        # return {'code': 'success'}, 'OK', 200
        # return {'code': 'success'}, 200
        return {'code': 'success'}
```

Класс-контроллер регистрируем в вызовом `Router().register_class(MyController)`

## Способ регистрации 2: Через классы-контроллеры, сразу пакетом

Модули с классами-контроллерами размещаем внутри пакета. Классы контроллеров импортируем в `__init__.py` пакета (my_package).
`from .mycontroller import MyController`
а при инициализации сервера написать
`Router().collect_package(my_package)`

## Способ регистрации 3: Через собственный список

Класс Router позволяет регитсрировать все методы из списка последовательностей из 3-х элементов: путь, список методов, функция обработчик.
Делается методом `Router().collect(List[Tuple[str, List[str], callable]])`

## Способ регистрации 4: Регистрация непосредственно метода обработчика

Для этого используем метод Router().add