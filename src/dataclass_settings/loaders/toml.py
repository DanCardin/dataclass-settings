from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePath
from typing import Any, cast

from dataclass_settings.context import Context
from dataclass_settings.loader import Loader


@dataclass
class Toml(Loader):
    file: str | PurePath
    key: str | None = None

    @staticmethod
    def init():
        return {}

    def load(self, context: Context) -> Any:
        field_name = cast(str, context.field_name)
        if not self.key and not context.infer_names:
            field = ".".join([*context.path, field_name])
            raise ValueError(
                f"Toml instance for `{field}` supplies no `key` and `infer_names` is enabled"
            )

        key = self.key or field_name

        import tomllib

        state = cast(dict, context.get_state(self))

        file = Path(self.file)
        if file not in state:
            file_content = file.read_text()
            state[file] = tomllib.loads(file_content)

        file_context = state[file]
        context.record_loaded_value(self, str(self.file), file_context)

        for segment in key.split("."):
            try:
                file_context = file_context[segment]
            except KeyError:
                continue

        return file_context
