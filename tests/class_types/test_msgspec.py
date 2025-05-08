from decimal import Decimal

import pytest
from msgspec import Struct
from typing_extensions import Annotated

from dataclass_settings import Env, load_settings
from tests.utils import env_setup


def test_missing_required():
    class Config(Struct):
        foo: Annotated[str, Env("FOO")]

    with env_setup({}), pytest.raises(TypeError):
        load_settings(Config)


def test_has_required_required():
    class Config(Struct):
        foo: Annotated[str, Env("FOO")]
        ignoreme: str = "asdf"

    with env_setup({"FOO": "1", "VALUE": "two"}):
        config = load_settings(Config)

    assert config == Config(foo="1", ignoreme="asdf")


def test_nested():
    class Sub(Struct):
        foo: Annotated[str, Env("FOO")]

    class Config(Struct):
        sub: Sub

    with env_setup({"FOO": "3"}):
        config = load_settings(Config)

    assert config == Config(sub=Sub(foo="3"))


def test_map_int():
    class Config(Struct):
        foo: Annotated[int, Env("FOO")]

    with env_setup({"FOO": "3"}):
        config = load_settings(Config)

    assert config == Config(foo=3)


def test_map_decimal():
    class Config(Struct):
        foo: Annotated[Decimal, Env("FOO")]

    with env_setup({"FOO": "3"}):
        config = load_settings(Config)

    assert config == Config(foo=Decimal("3"))
