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
    return bool(ClassTypes.from_cls(cls))


@dataclasses.dataclass
class Field:
    name: str
    type: type
    annotations: tuple[Any, ...]
    mapper: Callable[..., Any] | None = None

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


@dataclasses.dataclass
class DataclassField(Field):
    @classmethod
    def collect(cls, typ: type, type_hints: dict[str, Type]) -> list[Self]:
        fields = []
        for f in typ.__dataclass_fields__.values():  # type: ignore
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


@dataclasses.dataclass
class AttrsField(Field):
    @classmethod
    def collect(cls, typ: type, type_hints: dict[str, Type]) -> list[Self]:
        fields = []

        for f in typ.__attrs_attrs__:  # type: ignore
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


@dataclasses.dataclass
class MsgspecField(Field):
    @classmethod
    def collect(cls, typ: type, type_hints: dict[str, Type]) -> list[Self]:
        import msgspec

        fields = []
        for f in msgspec.structs.fields(typ):
            annotation = get_type(type_hints[f.name])
            annotation, args = get_annotation_args(annotation)

            def splat_mapper(**value):
                return msgspec.convert(value, annotation)

            mapper = splat_mapper if detect(annotation) else annotation

            field = cls(
                name=f.name,
                type=annotation,
                annotations=args,
                mapper=mapper,
            )
            fields.append(field)
        return fields


@dataclasses.dataclass
class PydanticV1Field(Field):
    @classmethod
    def collect(cls, typ, type_hints: dict[str, Type]) -> list[Self]:
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


@dataclasses.dataclass
class PydanticV2Field(Field):
    @classmethod
    def collect(cls, typ: type, type_hints: dict[str, Type]) -> list[Self]:
        fields = []
        for name, f in typ.model_fields.items():  # type: ignore
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


@dataclasses.dataclass
class PydanticV2DataclassField(Field):
    @classmethod
    def collect(cls, typ: type, type_hints: dict[str, Type]) -> list[Self]:
        fields = []

        for name, f in typ.__pydantic_fields__.items():  # type: ignore
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


def fields(cls: type):
    class_type = ClassTypes.from_cls(cls)
    if class_type is None:  # pragma: no cover
        raise ValueError(
            f"'{cls.__qualname__}' is not a currently supported kind of class. "
            "Must be one of: dataclass, pydantic, or attrs class."
        )

    type_hints = get_type_hints(cls, include_extras=True)
    return class_type.value.collect(cls, type_hints)


class ClassTypes(Enum):
    attrs = AttrsField
    dataclass = DataclassField
    pydantic_v1 = PydanticV1Field
    pydantic_v2 = PydanticV2Field
    pydantic_v2_dataclass = PydanticV2DataclassField
    msgspec = MsgspecField

    @classmethod
    def from_cls(cls, obj: type) -> ClassTypes | None:
        if hasattr(obj, "__pydantic_fields__"):
            return cls.pydantic_v2_dataclass

        if dataclasses.is_dataclass(obj):
            return cls.dataclass

        if hasattr(obj, "__struct_config__"):
            assert obj.__struct_config__.__class__.__module__.startswith("msgspec")
            return cls.msgspec

        try:
            import pydantic
            from pydantic import BaseModel
        except ImportError:  # pragma: no cover
            pass
        else:
            try:
                is_base_model = isinstance(obj, type) and issubclass(obj, BaseModel)
            except TypeError:  # pragma: no cover
                is_base_model = False

            if is_base_model:
                if pydantic.__version__.startswith("1."):
                    return cls.pydantic_v1
                return cls.pydantic_v2

        if hasattr(obj, "__attrs_attrs__"):
            return cls.attrs

        return None


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
