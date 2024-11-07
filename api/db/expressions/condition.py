import typing

from .composite import CompositeExpression, CompositeANDExpression, CompositeORExpression


class ConditionExpression:

    def __init__(self, condition: typing.Optional[typing.Union[CompositeExpression, str]] = None, **values: typing.Any):
        self.values = values or dict()
        self._negated = False

        if not isinstance(condition, CompositeExpression):
            self.condition = CompositeANDExpression(condition)
        else:
            self.condition = condition

    def __str__(self) -> str:
        return self.build()

    def __len__(self) -> int:
        return len(self.condition) if self.condition else 0

    def and_x(
        self, *expressions: typing.Union[CompositeExpression, 'ConditionExpression', str], **values: typing.Any
    ) -> 'ConditionExpression':
        if isinstance(self.condition, CompositeANDExpression):
            self.condition.add(*expressions)
        else:
            self.condition = CompositeANDExpression(self.condition, *expressions)

        for expression in expressions:
            if isinstance(expression, ConditionExpression):
                self.values.update(expression.values)

        self.values.update(values)
        return self

    def or_x(
        self, *expressions: typing.Union[CompositeExpression, 'ConditionExpression', str], **values: typing.Any
    ) -> 'ConditionExpression':
        if isinstance(self.condition, CompositeORExpression):
            self.condition.add(*expressions)
        else:
            self.condition = CompositeORExpression(self.condition, *expressions)

        for expression in expressions:
            if isinstance(expression, ConditionExpression):
                self.values.update(expression.values)

        self.values.update(values)
        return self

    def __invert__(self):
        self._negated = not self._negated
        return self

    def build(self) -> str:
        cond_str = str(self.condition or '')
        if cond_str and self._negated:
            cond_str = f'NOT({cond_str})'

        return cond_str or 'TRUE'
