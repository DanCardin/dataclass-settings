from __future__ import annotations

import sys
from dataclasses import dataclass

import pytest
from attr import dataclass as attr_dataclass
from msgspec import Struct
from pydantic import BaseModel, ValidationError
from pydantic.dataclasses import dataclass as pydantic_dataclass
from typing_extensions import Annotated

from dataclass_settings import Env, load_settings
from tests.utils import env_setup

if sys.version_info >= (3, 10):

    @attr_dataclass
    class Attr:
        foo: Annotated[int | None, Env("FOO")] = None

    @dataclass
    class Dataclass:
        foo: Annotated[int | None, Env("FOO")] = None

    class Msgspec(Struct):
        foo: Annotated[int | None, Env("FOO")] = None

    class Pydantic(BaseModel):
        foo: Annotated[int | None, Env("FOO")] = None

    @pydantic_dataclass
    class PDataclass:
        foo: Annotated[int | None, Env("FOO")] = None

    @pytest.mark.parametrize(
        "config_class, exc_class",
        [
            (Attr, TypeError),
            (Dataclass, TypeError),
            (Msgspec, TypeError),
            (Pydantic, ValidationError),
            (PDataclass, ValidationError),
        ],
    )
    def test_handles_312_syntax(config_class, exc_class):
        with env_setup({}):
            result = load_settings(config_class)
        assert result.foo is None

        with env_setup({"FOO": "5"}):
            result = load_settings(config_class)
        assert result.foo == 5
