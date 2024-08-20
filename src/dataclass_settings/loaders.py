from __future__ import annotations

import os
from dataclasses import dataclass
from functools import partial
from typing import cast, runtime_checkable

from typing_extensions import Protocol, assert_never

from dataclass_settings.context import Context


@runtime_checkable
class Loader(Protocol):
    @staticmethod
    def init():
        """Return any state necessary to be shared across instances of the loader."""
        return

    @classmethod
    def partial(cls, **kwargs):
        return partial(cls, **kwargs)  # type: ignore

    def load(self, context: Context):
        assert_never()  # type: ignore


@dataclass(init=False)
class Env(Loader):
    env_vars: tuple[str, ...]

    def __init__(self, *env_vars: str):
        self.env_vars = env_vars

    @staticmethod
    def init():
        return os.environ

    def load(self, context: Context):
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
    dir: str = "/run/secrets"

    def __init__(self, *names: str, dir: str = dir):
        self.names = names
        self.dir = dir

    def load(self, context: Context):
        field_name = cast(str, context.field_name)
        if not self.names and not context.infer_names:
            field = ".".join([*context.path, field_name])
            raise ValueError(
                f"Env instance for `{field}` supplies no `env_var` and `infer_names` is enabled"
            )

        names = [field_name] if context.infer_names else self.names
        for name in names:
            final_name = context.get_name(name)
            path = os.path.join(self.dir, final_name)

            if os.path.exists(path):
                with open(path) as f:
                    return f.read()

        return None
