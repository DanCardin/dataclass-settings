from __future__ import annotations

import dataclasses
from enum import Enum
from typing import Any, Callable, Tuple, Type

import typing_inspect
from typing_extensions import Annotated, Self, get_args, get_origin, get_type_hints

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
    pydantic_v1 = "pydantic_v1"
    pydantic_dataclass = "pydantic_dataclass"
    attrs = "attrs"

    @classmethod
    def from_cls(cls, obj: type) -> ClassTypes:
        if hasattr(obj, "__pydantic_fields__"):
            return cls.pydantic_dataclass

        if dataclasses.is_dataclass(obj):
            return cls.dataclass

        try:
            import pydantic
        except ImportError:  # pragma: no cover
            pass
        else:
            try:
                is_base_model = isinstance(obj, type) and issubclass(
                    obj, pydantic.BaseModel
                )
            except TypeError:
                is_base_model = False

            if is_base_model:
                if pydantic.__version__.startswith("1."):
                    return cls.pydantic_v1
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
    mapper: Callable[..., Any] | None = None

    @classmethod
    def from_dataclass(cls, typ: Type, type_hints: dict[str, Type]) -> list[Self]:
        fields = []
        for f in typ.__dataclass_fields__.values():
            annotation = get_type(type_hints[f.name])

            annotation, args = get_annotation_args(annotation)

            field = cls(
                name=f.name,
                type=annotation,
                annotations=args,
                mapper=annotation,
            )
            fields.append(field)
        return fields

    @classmethod
    def from_pydantic(cls, typ: Type, type_hints: dict[str, Type]) -> list[Self]:
        fields = []
        for name, f in typ.model_fields.items():
            annotation = get_type(type_hints[name])
            mapper = annotation if detect(annotation) else None

            field = cls(
                name=name,
                type=annotation,
                annotations=tuple(f.metadata),
                mapper=mapper,
            )
            fields.append(field)
        return fields

    @classmethod
    def from_pydantic_v1(cls, typ: Type, type_hints: dict[str, Type]) -> list[Self]:
        fields = []
        for name, f in typ.__fields__.items():
            annotation = get_type(type_hints[name])
            annotation, args = get_annotation_args(annotation)

            mapper = annotation if detect(annotation) else None

            field = cls(
                name=name,
                type=annotation,
                annotations=args,
                mapper=mapper,
            )
            fields.append(field)
        return fields

    @classmethod
    def from_pydantic_dataclass(
        cls, typ: Type, type_hints: dict[str, Type]
    ) -> list[Self]:
        fields = []

        for name, f in typ.__pydantic_fields__.items():
            annotation = get_type(type_hints[name])
            mapper = annotation if detect(annotation) else None

            field = cls(
                name=name,
                type=annotation,
                annotations=tuple(f.metadata),
                mapper=mapper,
            )
            fields.append(field)
        return fields

    @classmethod
    def from_attrs(cls, typ: Type, type_hints: dict[str, Type]) -> list[Self]:
        fields = []

        for f in typ.__attrs_attrs__:
            annotation = get_type(type_hints[f.name])
            annotation, args = get_annotation_args(annotation)

            field = cls(
                name=f.name,
                type=annotation,
                annotations=args,
                mapper=annotation,
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
        if not self.mapper:
            return value

        if isinstance(value, str):
            return self.mapper(value)

        return self.mapper(**value)


def fields(cls: type):
    class_type = ClassTypes.from_cls(cls)

    type_hints = get_type_hints(cls, include_extras=True)
    if class_type == ClassTypes.dataclass:
        return Field.from_dataclass(cls, type_hints)

    if class_type == ClassTypes.pydantic:
        return Field.from_pydantic(cls, type_hints)

    if class_type == ClassTypes.pydantic_v1:
        return Field.from_pydantic_v1(cls, type_hints)

    if class_type == ClassTypes.pydantic_dataclass:
        return Field.from_pydantic_dataclass(cls, type_hints)

    if class_type == ClassTypes.attrs:
        return Field.from_attrs(cls, type_hints)

    raise NotImplementedError()  # pragma: no cover


def get_type(typ):
    if typing_inspect.is_optional_type(typ):
        return get_args(typ)[0]
    return typ


def get_annotation_args(annotation) -> Tuple[Type, Tuple[Any, ...]]:
    args: Tuple[Any, ...] = ()
    if get_origin(annotation) is Annotated:
        args = get_args(annotation)
        annotation, *_args = args
        args = tuple(_args)

    return annotation, args
