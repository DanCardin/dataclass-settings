from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar, Union

from typing_extensions import Annotated

from dataclass_settings import Env, load_settings
from tests.utils import env_setup


@dataclass
class Dataclass:
    foo: ClassVar[int] = 5
    baz: Annotated[Union[int, None], Env("FOO")] = None


def test_ignores_classvar():
    with env_setup({}):
        result = load_settings(Dataclass)
    assert result.foo == 5
    assert result.baz is None

    with env_setup({"FOO": "5"}):
        result = load_settings(Dataclass)
    assert result.foo == 5
    assert result.baz == 5
