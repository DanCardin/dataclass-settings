from dataclasses import dataclass
from decimal import Decimal

import pytest
from typing_extensions import Annotated

from dataclass_settings import Env, load_settings
from tests.utils import env_setup


def test_missing_required():
    @dataclass
    class Config:
        foo: Annotated[str, Env("FOO")]

    with env_setup({}), pytest.raises(TypeError):
        load_settings(Config)


def test_has_required_required():
    @dataclass
    class Config:
        foo: Annotated[str, Env("FOO")]
        ignoreme: str = "asdf"

    with env_setup({"FOO": "1", "VALUE": "two"}):
        config = load_settings(Config)

    assert config == Config(foo="1", ignoreme="asdf")


def test_nested():
    @dataclass
    class Sub:
        foo: Annotated[str, Env("FOO")]

    @dataclass
    class Config:
        sub: Sub

    with env_setup({"FOO": "3"}):
        config = load_settings(Config)

    assert config == Config(sub=Sub(foo="3"))


def test_map_int():
    @dataclass
    class Config:
        foo: Annotated[int, Env("FOO")]

    with env_setup({"FOO": "3"}):
        config = load_settings(Config)

    assert config == Config(foo=3)


def test_map_decimal():
    @dataclass
    class Config:
        foo: Annotated[Decimal, Env("FOO")]

    with env_setup({"FOO": "3"}):
        config = load_settings(Config)

    assert config == Config(foo=Decimal("3"))
