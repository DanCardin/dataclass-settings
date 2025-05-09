from dataclasses import dataclass
from typing import List, Union

import pytest
from attr import dataclass as attr_dataclass
from msgspec import Struct
from pydantic import BaseModel, Field, ValidationError
from pydantic.dataclasses import dataclass as pydantic_dataclass
from typing_extensions import Annotated

from dataclass_settings import Secret, load_settings
from tests.utils import env_setup


@attr_dataclass
class AttrRequired:
    foo: Annotated[int, Secret("FOO")]
    ignoreme: str = "asdf"


@dataclass
class DataclassRequired:
    foo: Annotated[int, Secret("foo")]
    ignoreme: str = "asdf"


class MsgspecRequired(Struct):
    foo: Annotated[int, Secret("FOO")]
    ignoreme: str = "asdf"


class PydanticRequired(BaseModel):
    foo: Annotated[int, Secret("foo")]
    ignoreme: str = "asdf"


@pydantic_dataclass
class PDataclassRequired:
    foo: Annotated[int, Secret("FOO")]
    ignoreme: str = "asdf"


@pytest.mark.parametrize(
    "config_class, exc_class",
    [
        (AttrRequired, TypeError),
        (DataclassRequired, TypeError),
        (MsgspecRequired, TypeError),
        (PydanticRequired, ValidationError),
        (PDataclassRequired, ValidationError),
    ],
)
def test_missing_required(config_class, exc_class):
    with env_setup(), pytest.raises(exc_class):
        load_settings(config_class)


@pytest.mark.parametrize(
    "config_class",
    [
        AttrRequired,
        DataclassRequired,
        MsgspecRequired,
        PydanticRequired,
        PDataclassRequired,
    ],
)
def test_has_required_required(config_class):
    with env_setup(files={"/run/secrets/foo": "1"}):
        config = load_settings(config_class)

    assert config == config_class(foo=1, ignoreme="asdf")


@attr_dataclass
class AttrFallback:
    foo: Annotated[int, Secret("foo")]
    default: Annotated[str, Secret("meow", "uhh")] = "ok"


@dataclass
class DataclassFallback:
    foo: Annotated[int, Secret("foo")]
    default: Annotated[str, Secret("meow", "uhh")] = "ok"


class MsgspecFallback(Struct):
    foo: Annotated[int, Secret("foo")]
    default: Annotated[str, Secret("meow", "uhh")] = "ok"


class PydanticFallback(BaseModel):
    foo: Annotated[int, Secret("foo")]
    default: Annotated[str, Secret("meow", "uhh")] = Field(default="ok")


@pydantic_dataclass
class PDataclassFallback:
    foo: Annotated[int, Secret("foo")]
    default: Annotated[str, Secret("meow", "uhh")] = Field(default="ok")


@pytest.mark.parametrize(
    "config_class",
    [
        AttrFallback,
        DataclassFallback,
        MsgspecFallback,
        PydanticFallback,
        PDataclassFallback,
    ],
)
def test_fallback(config_class):
    with env_setup(files={"/run/secrets/foo": "1", "/run/secrets/uhh": "3"}):
        config = load_settings(config_class)

    assert config == config_class(foo=1, default="3")


def test_nested_object():
    class Bar(BaseModel):
        value: Annotated[str, Secret("value")]
        meow: Annotated[str, Secret("meow")] = "meow"
        default: Annotated[str, Secret("meow", "uhh")] = Field(default="ok")

    class Config(BaseModel):
        foo: Annotated[int, Secret("foo")]
        bar: Bar
        ignoreme: str = "asdf"

    with env_setup(
        files={
            "/run/secrets/foo": "1",
            "/run/secrets/value": "two",
            "/run/secrets/uhh": "3",
        }
    ):
        config = load_settings(Config)

    assert config == Config(
        foo=1, bar=Bar(value="two", meow="meow", default="3"), ignoreme="asdf"
    )


def test_nested_delimiter():
    class Bar(BaseModel):
        value: Annotated[int, Secret("value")]

    class Foo(BaseModel):
        bar: Bar

    class Config(BaseModel):
        foo: Foo

    with env_setup(files={"/run/secrets/foo__bar__value": "15"}):
        config = load_settings(Config, nested_delimiter="__")

    assert config == Config(foo=Foo(bar=Bar(value=15)))


def test_ignore_non_env_fields():
    class Config(BaseModel):
        value1: Annotated[int, Secret("value")]
        value2: str = "foo"
        value3: List[str] = ["foo"]

    with env_setup(files={"/run/secrets/value": "15"}):
        config = load_settings(Config, nested_delimiter="__")

    assert config == Config(value1=15, value2="foo", value3=["foo"])


def test_optional_nested_object():
    class Foo(BaseModel):
        value: Annotated[int, Secret("value")]

    class Config(BaseModel):
        foo: Union[Foo, None] = None

    with env_setup():
        config = load_settings(Config, nested_delimiter="__")

    assert config == Config(foo=None)


def test_arbitrary_annotation_skipped():
    class Config(BaseModel):
        foo: Annotated[str, ""] = ""

    with env_setup():
        config = load_settings(Config)

    assert config == Config()


def test_union_of_supportable_class_types():
    class Foo(BaseModel): ...

    class Bar(BaseModel): ...

    class Config(BaseModel):
        foo: Union[Foo, Bar]

    with env_setup(), pytest.raises(ValueError):
        load_settings(Config)


def test_partial():
    my_secret = Secret.partial(dir="/foo/bar")

    class Config(BaseModel):
        foo: Annotated[str, my_secret("foo")]

    with env_setup(files={"/foo/bar/foo": "one"}):
        config = load_settings(Config)
    assert config == Config(foo="one")


def test_infer_name():
    class Foo(BaseModel):
        nested: Annotated[str, Secret()]

    class Config(BaseModel):
        foo: Foo
        bar: Annotated[int, Secret()]

    with env_setup(files={"/run/secrets/bar": "2", "/run/secrets/foo_nested": "nest!"}):
        config = load_settings(Config, nested_delimiter="_", infer_names=True)

    assert config == Config(bar=2, foo=Foo(nested="nest!"))


def test_missing_infer_name_or_env_var():
    class Config(BaseModel):
        bar: Annotated[int, Secret()]

    with env_setup(), pytest.raises(ValueError) as e:
        load_settings(Config)

    assert (
        str(e.value)
        == "Env instance for `bar` supplies no `env_var` and `infer_names` is enabled"
    )
