from typing import List, Union

import pytest
from dataclass_settings import Secret, load_settings
from pydantic import BaseModel, Field, ValidationError
from typing_extensions import Annotated

from tests.utils import env_setup


def test_missing_required():
    class Config(BaseModel):
        foo: Annotated[int, Secret("foo")]

    with env_setup(), pytest.raises(ValidationError):
        load_settings(Config)


def test_has_required_required():
    class Config(BaseModel):
        foo: Annotated[int, Secret("foo")]
        ignoreme: str = "asdf"

    with env_setup(files={"/run/secrets/foo": "1"}):
        config = load_settings(Config)

    assert config == Config(foo=1, ignoreme="asdf")


def test_fallback():
    class Config(BaseModel):
        foo: Annotated[int, Secret("foo")]
        default: Annotated[str, Secret("meow", "uhh")] = Field(default="ok")

    with env_setup(files={"/run/secrets/foo": "1", "/run/secrets/uhh": "3"}):
        config = load_settings(Config)

    assert config == Config(foo=1, default="3")


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


def test_common_dir():
    my_secret = Secret.with_dir("/foo/bar")

    class Foo(BaseModel):
        nested: Annotated[str, my_secret()]

    class Config(BaseModel):
        foo: Foo
        bar: Annotated[int, my_secret()]

    with env_setup(files={"/foo/bar/bar": "2", "/foo/bar/foo_nested": "nest!"}):
        config = load_settings(Config, nested_delimiter="_", infer_names=True)

    assert config == Config(bar=2, foo=Foo(nested="nest!"))


def test_dir_fallback():
    class Foo(BaseModel):
        nested: Annotated[str, Secret(dir=("/asdf", "/foo/bar"))]

    my_secret = Secret.with_dir("/asdf", "/foo/bar")

    class Config(BaseModel):
        foo: Foo
        bar: Annotated[int, my_secret()]

    with env_setup(files={"/foo/bar/foo_nested": "nest!", "/asdf/bar": "2"}):
        config = load_settings(Config, nested_delimiter="_", infer_names=True)

    assert config == Config(bar=2, foo=Foo(nested="nest!"))


def test_dir_configured_at_loader():
    class Foo(BaseModel):
        nested: Annotated[str, Secret()]

    class Config(BaseModel):
        foo: Foo
        bar: Annotated[int, Secret()] = 3

    with env_setup(files={"/foo/bar/foo_nested": "nest!", "/bar/baz/bar": "2"}):
        config = load_settings(
            Config,
            nested_delimiter="_",
            infer_names=True,
            loader_args=Secret.load_as(dir=("/foo/bar", "/bar/baz")),
        )

    assert config == Config(bar=2, foo=Foo(nested="nest!"))

    with env_setup(files={"/foo/bar/foo_nested": "nest!", "/bar/baz/bar": "2"}):
        config = load_settings(
            Config,
            nested_delimiter="_",
            infer_names=True,
            loader_args=Secret.load_as(dir="/foo/bar"),
        )

    assert config == Config(bar=3, foo=Foo(nested="nest!"))
