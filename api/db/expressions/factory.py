import typing

from .set import SetBuilder
from .composite import CompositeANDExpression, CompositeORExpression, CompositeExpression
from .condition import ConditionExpression


def and_x(*expressions: typing.Union[CompositeExpression, str]) -> CompositeANDExpression:
    return CompositeANDExpression(*expressions)


def or_x(*expressions: typing.Union[CompositeExpression, str]) -> CompositeORExpression:
    return CompositeORExpression(*expressions)


def condition() -> ConditionExpression:
    return ConditionExpression()


def set(*expressions: str, **values: typing.Any) -> SetBuilder:
    return SetBuilder(*expressions, **values)
