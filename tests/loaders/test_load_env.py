import textwrap
from typing import List, Union

import pytest
from dataclass_settings import Env, load_settings
from pydantic import BaseModel, Field, ValidationError
from typing_extensions import Annotated

from tests.utils import env_setup


def test_missing_required():
    class Config(BaseModel):
        foo: Annotated[int, Env("FOO")]

    with env_setup({}), pytest.raises(ValidationError):
        load_settings(Config)


def test_has_required_required():
    class Config(BaseModel):
        foo: Annotated[int, Env("FOO")]
        ignoreme: str = "asdf"

    with env_setup({"FOO": "1", "VALUE": "two"}):
        config = load_settings(Config)

    assert config == Config(foo=1, ignoreme="asdf")


def test_fallback():
    class Config(BaseModel):
        foo: Annotated[int, Env("FOO")]
        default: Annotated[str, Env("MEOW", "UHH")] = Field(default="ok")

    with env_setup({"FOO": "1", "VALUE": "two", "UHH": "3"}):
        config = load_settings(Config)

    assert config == Config(foo=1, default="3")


def test_nested_object():
    class Bar(BaseModel):
        value: Annotated[str, Env("VALUE")]
        meow: Annotated[str, Env("MEOW")] = "meow"
        default: Annotated[str, Env("MEOW", "UHH")] = Field(default="ok")

    class Config(BaseModel):
        foo: Annotated[int, Env("FOO")]
        bar: Bar
        ignoreme: str = "asdf"

    with env_setup({"FOO": "1", "VALUE": "two", "UHH": "3"}):
        config = load_settings(Config)

    assert config == Config(
        foo=1, bar=Bar(value="two", meow="meow", default="3"), ignoreme="asdf"
    )


def test_nested_delimiter():
    class Bar(BaseModel):
        value: Annotated[int, Env("VALUE")]

    class Foo(BaseModel):
        bar: Bar

    class Config(BaseModel):
        foo: Foo

    with env_setup({"FOO__BAR__VALUE": "15"}):
        config = load_settings(Config, nested_delimiter="__")

    assert config == Config(foo=Foo(bar=Bar(value=15)))


def test_ignore_non_env_fields():
    class Config(BaseModel):
        value1: Annotated[int, Env("VALUE")]
        value2: str = "foo"
        value3: List[str] = ["foo"]

    with env_setup({"VALUE": "15"}):
        config = load_settings(Config, nested_delimiter="__")

    assert config == Config(value1=15, value2="foo", value3=["foo"])


def test_optional_nested_object():
    class Foo(BaseModel):
        value: Annotated[int, Env("VALUE")]

    class Config(BaseModel):
        foo: Union[Foo, None] = None

    with env_setup({}):
        config = load_settings(Config, nested_delimiter="__")

    assert config == Config(foo=None)


def test_arbitrary_annotation_skipped():
    class Config(BaseModel):
        foo: Annotated[str, ""] = ""

    with env_setup({}):
        config = load_settings(Config)

    assert config == Config()


def test_union_of_supportable_class_types():
    class Foo(BaseModel):
        ...

    class Bar(BaseModel):
        ...

    class Config(BaseModel):
        foo: Union[Foo, Bar]

    with env_setup({}), pytest.raises(ValueError):
        load_settings(Config)


def test_infer_name():
    class Foo(BaseModel):
        nested: Annotated[str, Env()]

    class Config(BaseModel):
        foo: Foo
        bar: Annotated[int, Env()]

    with env_setup({"BAR": "2", "FOO_NESTED": "nest!"}):
        config = load_settings(Config, nested_delimiter="_", infer_names=True)

    assert config == Config(bar=2, foo=Foo(nested="nest!"))


def test_missing_infer_name_or_env_var():
    class Config(BaseModel):
        bar: Annotated[int, Env()]

    with env_setup(), pytest.raises(ValueError) as e:
        load_settings(Config)

    assert (
        str(e.value)
        == "Env instance for `bar` supplies no `env_var` and `infer_names` is enabled"
    )


def test_setting_load_error(caplog):
    class Foo(BaseModel):
        nested: Annotated[str, Env()]
        bar: Annotated[str, Env()]

    class Config(BaseModel):
        foo: Foo

    with env_setup({"BAR": "one"}), pytest.raises(ValidationError):
        load_settings(Config, infer_names=True, emit_history=True)

    message = caplog.messages[0]
    assert message == textwrap.dedent(
        """\
        foo.nested:
         - Used `Env` to read 'nested', found 'None'. Skipping.

        foo.bar:
         - Used `Env` to read 'bar', found 'one'.
        """
    )
