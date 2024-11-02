import typing


class SetBuilder:

    def __init__(self, *expressions: str, **values: typing.Any) -> None:
        self._set_expressions = []
        self._set_values = {}
        if expressions:
            self.set(*expressions, **values)

    def set(self, *expression: str, **values: typing.Any) -> 'SetBuilder':
        self._set_expressions.extend(expression)
        self._set_values.update(values)
        return self

    @staticmethod
    def _get_alias(name: str) -> str:
        return f'%({name})s'

    def field(self, field: str, value: typing.Any) -> 'SetBuilder':
        """
        Добавляет поле, создавая алиас по названию и добавляя значение с ключом алиаса
        Напр:
        >>> self.field('status', MyStatus.Completed)
        эквивалентно
        >>> self.set('status = %(status)s', status=MyStatus.Completed)
        """

        alias = self._get_alias(field)
        self.set(f'{field}={alias}', **{field: value})
        return self

    def fields(self, *fields: str, **values: typing.Any) -> 'SetBuilder':
        """
        Автоматически создает алиас для параметра вставки по переданному названию поля
        Например:
        >>> self.fields('status', 'count', status='completed', count=2)
        эквивалентно
        >>> self.set('status=%(status)s', 'count=%(count)s', status='completed', count=2)
        """

        exps = []
        for field in fields:
            alias = self._get_alias(field)
            exps.append(f'{field}={alias}')
        self.set(*exps, **values)
        return self

    @property
    def values(self) -> typing.Dict[str, typing.Any]:
        return self._set_values

    def build(self) -> str:
        return ','.join(self._set_expressions)

    def __str__(self) -> str:
        return self.build()
