from __future__ import annotations

import dataclasses
from enum import Enum
from typing import Any, Callable, Type

import typing_inspect
from typing_extensions import Self, get_args, get_origin

from dataclass_settings.loaders import Loader

__all__ = [
    "fields",
    "detect",
]


def detect(cls: type) -> bool:
    try:
        return bool(ClassTypes.from_cls(cls))
    except ValueError:
        return False


class ClassTypes(Enum):
    dataclass = "dataclass"
    pydantic = "pydantic"
    pydantic_dataclass = "pydantic_dataclass"
    attrs = "attrs"

    @classmethod
    def from_cls(cls, obj: type) -> ClassTypes:
        if hasattr(obj, "__pydantic_fields__"):
            return cls.pydantic_dataclass

        if dataclasses.is_dataclass(obj):
            return cls.dataclass

        try:
            from pydantic import BaseModel
        except ImportError:  # pragma: no cover
            pass
        else:
            if isinstance(obj, type) and issubclass(obj, BaseModel):
                return cls.pydantic

        if hasattr(obj, "__attrs_attrs__"):
            return cls.attrs

        raise ValueError(  # pragma: no cover
            f"'{cls}' is not a currently supported base class. "
            "Must be one of: dataclass, pydantic, or attrs class."
        )


@dataclasses.dataclass
class Field:
    name: str
    type: type
    annotations: tuple[Any, ...]
    mapper: Callable[..., Any]

    @classmethod
    def from_dataclass(cls, typ: Type) -> list[Self]:
        fields = []
        for f in typ.__dataclass_fields__.values():
            field = cls(
                name=f.name,
                type=get_origin(f.type) or f.type,
                annotations=get_args(f.type) or (),
                mapper=f.type,
            )
            fields.append(field)
        return fields

    @classmethod
    def from_pydantic(cls, typ: Type) -> list[Self]:
        fields = []
        for name, f in typ.model_fields.items():
            field = cls(
                name=name,
                type=f.annotation,
                annotations=tuple(f.metadata),
                mapper=get_type(f.annotation),
            )
            fields.append(field)
        return fields

    @classmethod
    def from_pydantic_dataclass(cls, typ: Type) -> list[Self]:
        fields = []
        for name, f in typ.__pydantic_fields__.items():
            field = cls(
                name=name,
                type=f.annotation,
                annotations=tuple(f.metadata),
                mapper=get_type(f.annotation),
            )
            fields.append(field)
        return fields

    @classmethod
    def from_attrs(cls, typ: Type) -> list[Self]:
        fields = []
        for f in typ.__attrs_attrs__:
            field = cls(
                name=f.name,
                type=get_origin(f.type) or f.type,
                annotations=get_args(f.type) or (),
                mapper=f.type,
            )
            fields.append(field)
        return fields

    def get_loaders(self, loaders: tuple[Type[Loader], ...]):
        for m in self.annotations:
            if isinstance(m, loaders):
                yield m

    def get_nested_type(self) -> Type | None:
        if typing_inspect.is_union_type(self.type):
            args = typing_inspect.get_args(self.type)
        else:
            args = [self.type]

        unsupported_args = []
        try:
            supported_arg = next(arg for arg in args if detect(arg))
        except StopIteration:
            supported_arg = None

        for arg in args:
            if arg is not supported_arg and detect(arg):
                unsupported_args.append(arg)

        if unsupported_args:
            raise ValueError("Can only react to one thing a time", unsupported_args)

        return supported_arg

    def map_value(self, value: str | dict[str, Any]):
        if isinstance(value, str):
            return self.mapper(value)
        return self.mapper(**value)


def fields(cls: type):
    class_type = ClassTypes.from_cls(cls)
    if class_type == ClassTypes.dataclass:
        return Field.from_dataclass(cls)

    if class_type == ClassTypes.pydantic:
        return Field.from_pydantic(cls)

    if class_type == ClassTypes.pydantic_dataclass:
        return Field.from_pydantic_dataclass(cls)

    if class_type == ClassTypes.attrs:
        return Field.from_attrs(cls)

    raise NotImplementedError()  # pragma: no cover


def get_type(typ):
    if typing_inspect.is_optional_type(typ):
        return get_args(typ)[0]
    return typ
