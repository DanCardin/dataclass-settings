from decimal import Decimal

import pytest
from attrs import define, field
from typing_extensions import Annotated

from dataclass_settings import Env, load_settings
from tests.utils import env_setup


def test_missing_required():
    @define
    class Config:
        foo: Annotated[str, Env("FOO")]

    with env_setup({}), pytest.raises(TypeError):
        load_settings(Config)


def test_has_required_required():
    @define
    class Config:
        foo: Annotated[str, Env("FOO")]
        ignoreme: str = "asdf"

    with env_setup({"FOO": "1", "VALUE": "two"}):
        config = load_settings(Config)

    assert config == Config(foo="1", ignoreme="asdf")


def test_nested():
    @define
    class Sub:
        foo: Annotated[str, Env("FOO")]

    @define
    class Config:
        sub: Sub

    with env_setup({"FOO": "3"}):
        config = load_settings(Config)

    assert config == Config(sub=Sub(foo="3"))


def test_map_int():
    @define
    class Config:
        foo: Annotated[int, Env("FOO")] = field(converter=int)

    with env_setup({"FOO": "3"}):
        config = load_settings(Config)

    assert config == Config(foo=3)


def test_map_decimal():
    @define
    class Config:
        foo: Annotated[Decimal, Env("FOO")] = field(converter=Decimal)

    with env_setup({"FOO": "3"}):
        config = load_settings(Config)

    assert config == Config(foo=Decimal("3"))
