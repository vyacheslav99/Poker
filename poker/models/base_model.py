import json


class BaseModel:

    def __init__(self, filename=None, **kwargs):
        if filename:
            self.load(filename)
        else:
            self.set(**kwargs)

    def set(self, **kwargs):
        """
        Задает значения публичных полей по набору переданных аргументов. Лишние игнорирует

        :param kwargs: набор параметров для установки значений
        """

        for k, v in kwargs.items():
            if hasattr(self, k) and not k.startswith(self.__class__.__name__):
                setattr(self, k, v)

    def from_dict(self, obj):
        """
        Задает значения публичных полей из словаря (аналогично методу set). Лишние игнорирует

        :param dict obj: Словарь параметров
        """

        self.set(**obj)

    def load(self, filename):
        """
        Загрузка параметров из файла формата json

        :param str filename: Путь к файлу
        """

        with open(filename, 'r') as f:
            self.from_dict(json.load(f))

    def loads(self, json_str):
        """
        Загрузка параметров из строки json

        :param str json_str: строка формата json
        """

        self.from_dict(json.loads(json_str))

    def as_dict(self):
        """
        Возвращает все публичные поля в виде словаря

        :return: dict
        """

        return {k: getattr(self, k) for k in dir(self) if not k.startswith('_') and not callable(getattr(self, k))}

    def save(self, filename):
        """
        Сохранение параметров в файл, в формате json

        :param str filename: путь к файлу
        """

        with open(filename, 'w') as f:
            json.dump(self.as_dict(), f)
