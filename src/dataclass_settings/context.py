from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from dataclass_settings.loaders import Loader


@dataclass
class Context:
    path: list[str] = field(default_factory=list)
    field_name: str | None = None
    state: dict[type[Loader], Any] = field(default_factory=dict)

    nested_delimiter: bool | str = False
    infer_names: bool = False
    record_history: bool = False

    _loaded_values: dict[str, list[str]] = field(default_factory=dict)

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

    def load_state(self, loader: type[Loader], args: Any | None = None):
        state = loader.init(*(args or ()))
        if state is not None:
            self.state[loader] = state

    def get_state(self, loader: Loader):
        return self.state.get(type(loader))

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
