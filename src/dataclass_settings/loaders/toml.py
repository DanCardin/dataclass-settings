from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePath
from typing import Any

from dataclass_settings.context import Context
from dataclass_settings.loader import DictState, Loader


@dataclass
class TomlState(DictState):
    file: str | PurePath | None = None


@dataclass
class Toml(Loader[TomlState]):
    key: str | None = None
    file: str | PurePath | None = None

    def load(self, context: Context, state: TomlState) -> Any:
        import tomllib

        field_name = context.name
        if not self.key and not context.infer_names:
            field = ".".join([*context.path, field_name])
            raise ValueError(
                f"Toml instance for `{field}` supplies no `key` and `infer_names` is enabled"
            )

        key = self.key or field_name

        file = self.file or state.file
        if file is None:
            raise ValueError("Toml loader requires a `file` argument")

        file = Path(file)
        if file not in state.value:
            file_content = file.read_text()
            state.value[file] = tomllib.loads(file_content)

        file_context = state.value[file]
        context.record_loaded_value(self, str(self.file), file_context)

        for segment in key.split("."):
            try:
                file_context = file_context[segment]
            except KeyError:
                return None

        return file_context

    @classmethod
    def load_with(cls, file: str | PurePath | None = None) -> TomlState:
        return TomlState(cls, file=file)
