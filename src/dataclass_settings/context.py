from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Sequence, cast

from dataclass_settings.loader import Loader, LoaderState, LoaderType, LoaderTypes, T


@dataclass
class Context:
    path: list[str] = field(default_factory=list)
    field_name: str | None = None
    state: dict[type[Loader], LoaderState | None] = field(default_factory=dict)

    nested_delimiter: bool | str = False
    infer_names: bool = False
    record_history: bool = False

    _loaded_values: dict[str, list[str]] = field(default_factory=dict)

    @property
    def name(self):
        return cast(str, self.field_name)

    @property
    def loaders(self) -> tuple[type[Loader], ...]:
        return tuple(self.state.keys())

    def enter(self, name: str):
        path = [*self.path]
        if self.field_name is not None:
            path.append(self.field_name)

        return replace(self, path=path, field_name=name)

    def get_name(self, name: str) -> str:
        if self.nested_delimiter:
            nested_delimiter = (
                self.nested_delimiter if isinstance(self.nested_delimiter, str) else "_"
            )
            return nested_delimiter.join([*self.path, name])
        return name

    def resolve_loaders(self, *loaders_: LoaderTypes):
        seen: set[type[Loader]] = set()

        loaders: Sequence[LoaderType] = [
            loader
            for possible_loader_sequence in loaders_
            for loader in (
                possible_loader_sequence
                if isinstance(possible_loader_sequence, Sequence)
                else [possible_loader_sequence]
            )
        ]

        for loader in loaders:
            if isinstance(loader, LoaderState):
                loader_type = loader.loader_type
                state: LoaderState | None = loader
            elif issubclass(loader, Loader):
                loader_type = loader
                state = loader.load_with()
            else:
                raise TypeError(f"Unexpected loader type: {loader!r}")

            if loader_type not in seen:
                seen.add(loader_type)

            self.state[loader_type] = state

    def get_state(self, loader: Loader[T]) -> T:
        return cast(T, self.state[type(loader)])

    def record_loaded_value(self, loader: Loader, name: str, value: Any):
        if not self.record_history:
            return

        message = (
            f"Used `{loader.__class__.__name__}` to read '{name}', found '{value}'."
        )
        if value is None:
            message += " Skipping."

        full_path = ".".join([*self.path, cast(str, self.field_name)])
        self._loaded_values.setdefault(full_path, []).append(message)

    def generate_load_history(self):
        result = []
        for name, attempts in self._loaded_values.items():
            result.append(f"{name}:")
            for attempt in attempts:
                result.append(f" - {attempt}")
            result.append("")
        return "\n".join(result)
