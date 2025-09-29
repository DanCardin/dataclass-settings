from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, MutableMapping, cast

from dataclass_settings.context import Context
from dataclass_settings.loader import DictState, Loader

EnvLike = MutableMapping[str, str]


@dataclass(init=False)
class Env(Loader):
    env_vars: tuple[str, ...]

    def __init__(self, *env_vars: str):
        self.env_vars = env_vars

    def load(self, context: Context, state: DictState) -> Any:
        field_name = context.name
        if not self.env_vars and not context.infer_names:
            field = ".".join([*context.path, field_name])
            raise ValueError(
                f"Env instance for `{field}` supplies no `env_var` and `infer_names` is enabled"
            )

        env_vars = [field_name] if context.infer_names else self.env_vars
        for env_var in env_vars:
            name = context.get_name(env_var)
            final_env_var = name.upper()

            value = state.value.get(final_env_var)
            context.record_loaded_value(self, name, value)

            if value is not None:
                return value

        return None

    @classmethod
    def load_with(cls, *, env: EnvLike | None = None) -> DictState:
        if env is None:
            env = cast(EnvLike, os.environ)

        return DictState(cls, env)
