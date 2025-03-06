from __future__ import annotations

from typing import Any, ClassVar, Generic, Sequence, TypeVar, runtime_checkable

from typing_extensions import Protocol, assert_never

from dataclass_settings.context import Context


@runtime_checkable
class Loader(Protocol):
    def load(self, context: Context) -> Any:
        assert_never()  # type: ignore

    @classmethod
    def load_with(cls) -> LoaderState: ...


T = TypeVar("T", bound=Loader)


@runtime_checkable
class LoaderState(Protocol, Generic[T]):
    loader_type: ClassVar[type]

    def apply(self, loader_type: T) -> T: ...


LoaderType = type[Loader] | LoaderState
LoaderTypes = Sequence[LoaderType]
