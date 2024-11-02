from __future__ import annotations

import enum
import typing


class CompositeExpressionType(str, enum.Enum):
    AND = 'AND'
    OR = 'OR'

    def __str__(self):
        return self.value


class CompositeExpression:

    def __init__(
        self, type: CompositeExpressionType, *expressions: typing.Union[CompositeExpression, str],
    ):

        self.type = type
        self.expressions: typing.List[typing.Union[CompositeExpression, str]] = []

        if expressions:
            self.add(*expressions)

    def __str__(self) -> str:
        return self.build()

    def __len__(self) -> int:
        return len(self.expressions)

    def add(self, *expressions: typing.Union[CompositeExpression, str]) -> 'CompositeExpression':
        self.expressions += (expression for expression in expressions if expression and expression is not self)
        return self

    def build(self) -> str:
        if len(self.expressions) == 1:
            return str(self.expressions[0])

        return f'({f" {self.type} ".join(map(str, self.expressions))})'


class CompositeANDExpression(CompositeExpression):

    def __init__(self, *expressions: typing.Union[CompositeExpression, str]):
        super().__init__(CompositeExpressionType.AND, *expressions)


class CompositeORExpression(CompositeExpression):

    def __init__(self, *expressions: typing.Union[CompositeExpression, str]):
        super().__init__(CompositeExpressionType.OR, *expressions)
