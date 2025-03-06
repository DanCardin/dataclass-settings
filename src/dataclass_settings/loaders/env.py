from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, cast, ClassVar
from typing_extensions import Self

from dataclass_settings.context import Context
from dataclass_settings.loader import Loader

EnvLike = dict[str, str]


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


@dataclass
class EnvState(LoaderState[Env]):
    env: EnvLike

    loader_type: ClassVar = Env

    @classmethod
    def new(cls, env: dict[str, str]) -> Self:
        if dir is None:
            dir = cls.dir
        return cls(coerce_path_like(dir))

    @override
    def apply(self, loader_type: Secret) -> Secret:
        return replace(loader_type, dir=loader_type.dir or self.dir)
