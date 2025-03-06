from __future__ import annotations

import os
from dataclasses import dataclass, replace
from functools import partial
from pathlib import PurePath
from typing import Any, ClassVar, Sequence, cast, override

from typing_extensions import Self

from dataclass_settings.context import Context
from dataclass_settings.loader import Loader, LoaderState

PathLike = PurePath | str | Sequence[PurePath | str]

DEFAULT_PATH = PurePath("/run/secrets")


@dataclass(init=False)
class Secret(Loader):
    names: tuple[str, ...]
    dir: Sequence[PurePath] | None = None

    def __init__(self, *names: str, dir: PathLike | None = None):
        self.names = names

        if dir is None:
            self.dir = None
        else:
            self.dir = coerce_path_like(dir)

    def load(self, context: Context) -> Any:
        field_name = cast(str, context.field_name)
        if not self.names and not context.infer_names:
            field = ".".join([*context.path, field_name])
            raise ValueError(
                f"Env instance for `{field}` supplies no `env_var` and `infer_names` is enabled"
            )

        dirs = cast(Sequence[PurePath], self.dir)

        names = [field_name] if context.infer_names else self.names
        for name in names:
            final_name = context.get_name(name)

            for dir in dirs:
                path = dir / final_name

                if os.path.exists(path):
                    with open(path) as f:
                        return f.read()

        return None

    @classmethod
    def with_dir(cls, *dir: str) -> partial[Self]:
        return partial(cls, dir=dir)

    @classmethod
    def load_with(
        cls,
        *,
        dir: PathLike | None = None,
    ) -> SecretState:
        return SecretState.new(dir)


def coerce_path_like(dir: PathLike) -> Sequence[PurePath]:
    if isinstance(dir, str):
        dir = PurePath(dir)

    if isinstance(dir, Sequence):
        return tuple(PurePath(d) for d in dir if isinstance(dir, str))

    return (dir,)


@dataclass
class SecretState(LoaderState[Secret]):
    dir: Sequence[PurePath] = (DEFAULT_PATH,)

    loader_type: ClassVar = Secret

    @classmethod
    def new(cls, dir: PathLike | None = None) -> Self:
        if dir is None:
            dir = cls.dir
        return cls(coerce_path_like(dir))

    @override
    def apply(self, loader_type: Secret) -> Secret:
        return replace(loader_type, dir=loader_type.dir or self.dir)
