import json

from typing import Any, Literal
from pydantic import BaseModel
from pydantic.main import IncEx


class ModelMixin:

    _json_fields: set[str]

    @classmethod
    def __get_json_fields(cls) -> set[str]:
        if issubclass(cls, BaseModel):
            # Приватные атрибуты для классов-наследников pydantic.BaseModel будут экземплярами класса ModelPrivateAttr,
            # поэтому значение получаем так:
            return cls._json_fields.get_default() or set()
        else:
            return cls._json_fields or set()

    @classmethod
    def make(cls, data: dict[str, Any]):
        for k in cls.__get_json_fields():
            if k in data:
                if isinstance(data[k], str):
                    data[k] = json.loads(data[k])

        return cls(**data)

    def dump(
        self,
        *,
        mode: Literal['json', 'python'] | str = 'python',
        include: IncEx | None = None,
        exclude: IncEx | None = None,
        context: Any | None = None,
        by_alias: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        round_trip: bool = False,
        warnings: bool | Literal['none', 'warn', 'error'] = True,
        serialize_as_any: bool = False,
    ) -> dict[str, Any]:
        json_fields = self.__get_json_fields()

        data = self.model_dump(
            mode=mode,
            include=include,
            exclude=exclude,
            context=context,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            round_trip=round_trip,
            warnings=warnings,
            serialize_as_any=serialize_as_any
        )

        for k in json_fields:
            if data[k] is not None and not isinstance(data[k], str):
                data[k] = json.dumps(data[k])

        return data
