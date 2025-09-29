from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import PurePath
from typing import Any, Sequence

from typing_extensions import Self

from dataclass_settings.context import Context
from dataclass_settings.loader import (
    DictState,
    Loader,
    PathLike,
    coerce_pathlike_sequence,
)

DEFAULT_PATH = PurePath("/run/secrets")


@dataclass
class SecretState(DictState):
    dir: Sequence[PurePath] = (DEFAULT_PATH,)


@dataclass(init=False)
class Secret(Loader):
    names: tuple[str, ...] = ()
    dir: Sequence[PurePath] | None = None

    def __init__(self, *names: str, dir: Sequence[PathLike] | None = None):
        self.names = names

        if dir is None:
            self.dir = None
        else:
            self.dir = coerce_pathlike_sequence(dir, DEFAULT_PATH)

    def load(self, context: Context, state: SecretState) -> Any:
        field_name = context.name

        names = self.names
        if not names and context.infer_names:
            names = (field_name,)

        if not names:
            field = ".".join([*context.path, field_name])
            raise ValueError(
                f"Secret instance for `{field}` supplies no name and `infer_names` is enabled"
            )

        dirs = self.dir or state.dir

        for name in names:
            final_name = context.get_name(name)

            for dir in dirs:
                path = dir / final_name

                if path in state.value:
                    return state.value[path]

                if os.path.exists(path):
                    with open(path) as f:
                        value = f.read()
                        state.value[path] = value
                        return value

        return None

    def with_name(self, *names: str) -> Self:
        return self.__class__(*names, dir=self.dir)

    def with_dir(self, *dir: str) -> Self:
        return self.__class__(*self.names, dir=dir)

    @classmethod
    def load_with(cls, *, dir: Sequence[PathLike] | None = None) -> SecretState:
        return SecretState(cls, dir=coerce_pathlike_sequence(dir, DEFAULT_PATH))
