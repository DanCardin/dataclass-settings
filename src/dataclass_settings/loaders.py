from __future__ import annotations

import os
from dataclasses import dataclass
from functools import partial
from pathlib import Path, PurePath
from typing import Any, Mapping, Sequence, cast, runtime_checkable

from typing_extensions import Protocol, Self, assert_never

from dataclass_settings.context import Context


@runtime_checkable
class Loader(Protocol):
    @staticmethod
    def init() -> Any:  # pragma: no cover
        """Return any state necessary to be shared across instances of the loader."""
        return

    @classmethod
    def partial(cls, **kwargs):
        return partial(cls, **kwargs)

    def load(self, context: Context) -> Any:
        assert_never()  # type: ignore


@dataclass(init=False)
class Env(Loader):
    env_vars: tuple[str, ...]

    def __init__(self, *env_vars: str):
        self.env_vars = env_vars

    @staticmethod
    def init() -> Any:
        return os.environ

    def load(self, context: Context) -> Any:
        state = context.get_state(self) or {}

        field_name = cast(str, context.field_name)
        if not self.env_vars and not context.infer_names:
            field = ".".join([*context.path, field_name])
            raise ValueError(
                f"Env instance for `{field}` supplies no `env_var` and `infer_names` is enabled"
            )

        env_vars = [field_name] if context.infer_names else self.env_vars
        for env_var in env_vars:
            name = context.get_name(env_var)
            final_env_var = name.upper()

            value = state.get(final_env_var)
            context.record_loaded_value(self, name, value)

            if value is not None:
                return value

        return None


@dataclass(init=False)
class Secret(Loader):
    names: tuple[str, ...]
    dir: Sequence[str] = ("/run/secrets",)

    def __init__(self, *names: str, dir: str | Sequence[str] = dir):
        self.names = names

        if isinstance(dir, str):
            self.dir = (dir,)
        else:
            self.dir = dir

    @staticmethod
    def init(dir: Sequence[str] | None = None) -> Sequence[str] | None:
        return dir

    def load(self, context: Context) -> Any:
        field_name = cast(str, context.field_name)
        if not self.names and not context.infer_names:
            field = ".".join([*context.path, field_name])
            raise ValueError(
                f"Env instance for `{field}` supplies no `env_var` and `infer_names` is enabled"
            )

        dirs = cast(Sequence[str] | None, context.get_state(self))
        if not dirs:
            dirs = self.dir

        names = [field_name] if context.infer_names else self.names
        for name in names:
            final_name = context.get_name(name)

            for dir in dirs:
                path = os.path.join(dir, final_name)

                if os.path.exists(path):
                    with open(path) as f:
                        return f.read()

        return None

    @classmethod
    def with_dir(cls, *dir: str) -> partial[Self]:
        return partial(cls, dir=dir)

    @classmethod
    def load_as(
        cls,
        *,
        dir: Sequence[str] | str,
    ) -> dict[type[Loader], Sequence[Any] | Mapping[str, Any]]:
        if isinstance(dir, str):
            dir = (dir,)

        return {cls: {"dir": dir}}


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
                return None

        return file_context
