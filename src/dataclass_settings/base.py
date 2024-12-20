from __future__ import annotations

import logging
from typing import Any, ClassVar, TypeVar

from dataclass_settings import class_inspect
from dataclass_settings.context import Context
from dataclass_settings.loader import LoaderTypes
from dataclass_settings.loaders import Env, Secret, Toml

log = logging.getLogger("dataclass_settings")


T = TypeVar("T")


def load_settings(
    source_cls: type[T],
    *,
    loaders: LoaderTypes = (Env, Secret, Toml),
    extra_loaders: LoaderTypes = (),
    nested_delimiter: bool | str = False,
    infer_names: bool = False,
    emit_history: bool = False,
) -> T:
    """Load settings from a supported source class.

    Arguments:
        source_cls: The root object to load settings for.
        loaders: The set of loaders to use to load settings.
        extra_loaders: Additional loaders to use. Distinct from `loaders`
            in that this option will not affect the set of default loaders.
        nested_delimiter: Defaults to `False`. When `True`, "_" is used as
            the delimiter. When a string is provided, that is used as the
            delimiter.
        infer_names: Defaults to `False`. When `True`, it informs loaders
            to infer the name of the setting from the name of the field (
            akin to pydantic-settings' default). When disabled, most loaders
            will require an explicit name.
        emit_history: Defaults to `False`. When `True`, records the provenance
            of loaded secrets (evaluated names and values for each field) and
            log them in the event of a loading failure.
    """
    context = Context(
        nested_delimiter=nested_delimiter,
        infer_names=infer_names,
        record_history=emit_history,
    )

    context.resolve_loaders(loaders, extra_loaders)

    result = (
        collect(
            source_cls,
            context=context,
            nested_delimiter=nested_delimiter,
        )
        or {}
    )

    try:
        return source_cls(**result)
    except Exception:
        if emit_history:
            log.warning(context.generate_load_history())
        raise


def collect(
    source_cls: type,
    *,
    context: Context,
    nested_delimiter: bool | str = False,
) -> dict[str, Any] | None:
    loaders = context.loaders

    result = {}
    for field in class_inspect.fields(source_cls):
        if field.type_view.fallback_origin is ClassVar:
            continue

        field_context = context.enter(field.name)

        value: str | dict[str, Any] | None = None

        nested_type = field.get_nested_type()
        if nested_type:
            value = collect(
                nested_type,
                context=field_context,
                nested_delimiter=nested_delimiter,
            )
        else:
            for loader in field.get_loaders(loaders):
                state = context.get_state(loader)
                value = loader.load(field_context, state)
                if value is not None:
                    break

        if value is not None:
            try:
                mapped_value = field.map_value(value)
            except Exception:  # noqa: S110
                pass
            else:
                result[field.name] = mapped_value

    return result
