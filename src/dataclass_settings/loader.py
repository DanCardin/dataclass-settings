from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import PurePath
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    MutableMapping,
    Sequence,
    TypeVar,
    Union,
)

from typing_extensions import assert_never

if TYPE_CHECKING:
    from dataclass_settings.context import Context


T = TypeVar("T")


@dataclass
class LoaderState(Generic[T]):
    loader_type: type[T]


@dataclass
class DictState(LoaderState[T]):
    value: MutableMapping[Any, Any] = field(default_factory=dict)


class Loader(Generic[T]):
    def load(self, context: Context, state: T) -> Any:
        assert_never()  # type: ignore

    @classmethod
    def load_with(cls, *args, **kwargs) -> T | None:
        return None


LoaderType = Union[type[Loader], LoaderState]
LoaderTypes = Union[LoaderType, Sequence[LoaderType]]
PathLike = Union[PurePath, str]


def coerce_pathlike(dir: PathLike | None, default: PurePath) -> PurePath:
    if dir is None:
        dir = default

    if isinstance(dir, str):
        dir = PurePath(dir)

    return dir


def coerce_pathlike_sequence(
    dir: PathLike | Sequence[PathLike] | None, default: PurePath
) -> Sequence[PurePath]:
    if dir is None:
        return (default,)

    if isinstance(dir, (PurePath, str)):
        return (coerce_pathlike(dir, default),)

    return tuple(PurePath(d) for d in dir)
