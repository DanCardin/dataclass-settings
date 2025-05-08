from __future__ import annotations

from decimal import Decimal

import pytest
from pydantic import BaseModel, ValidationError
from typing_extensions import Annotated

from dataclass_settings import Env, load_settings
from tests.utils import env_setup


class MissingRequiredConfig(BaseModel):
    foo: Annotated[str, Env("FOO")]


def test_missing_required():
    with env_setup({}), pytest.raises(ValidationError):
        load_settings(MissingRequiredConfig)


def test_has_required_required():
    class Config(BaseModel):
        foo: Annotated[str, Env("FOO")]
        ignoreme: str = "asdf"

    with env_setup({"FOO": "1", "VALUE": "two"}):
        config = load_settings(Config)

    assert config == Config(foo="1", ignoreme="asdf")


class NestedSub(BaseModel):
    foo: Annotated[str, Env("FOO")]


class NestedConfig(BaseModel):
    sub: NestedSub


def test_nested():
    with env_setup({"FOO": "3"}):
        config = load_settings(NestedConfig)

    assert config == NestedConfig(sub=NestedSub(foo="3"))


def test_map_int():
    class Config(BaseModel):
        foo: Annotated[int, Env("FOO")]

    with env_setup({"FOO": "3"}):
        config = load_settings(Config)

    assert config == Config(foo=3)


def test_map_decimal():
    class Config(BaseModel):
        foo: Annotated[Decimal, Env("FOO")]

    with env_setup({"FOO": "3"}):
        config = load_settings(Config)

    assert config == Config(foo=Decimal("3"))


def test_bool_mapping():
    class Config(BaseModel):
        foo: Annotated[bool, Env("FOO")]

    with env_setup({"FOO": "True"}):
        config = load_settings(Config)

    assert config == Config(foo=True)

    with env_setup({"FOO": "False"}):
        config = load_settings(Config)

    assert config == Config(foo=False)
