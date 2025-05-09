import textwrap
from dataclasses import dataclass
from dataclasses import field as dataclass_field
from typing import List, Union

import pytest
from attr import dataclass as attr_dataclass
from attrs import field as attr_field
from msgspec import Struct
from msgspec import field as msgspec_field
from pydantic import BaseModel, Field, ValidationError
from pydantic.dataclasses import dataclass as pydantic_dataclass
from typing_extensions import Annotated

from dataclass_settings import Env, load_settings
from tests.utils import env_setup


@attr_dataclass
class AttrConfig:
    foo: Annotated[int, Env("FOO")]
    ignoreme: str = "asdf"


@dataclass
class DataclassConfig:
    foo: Annotated[int, Env("FOO")]
    ignoreme: str = "asdf"


class MsgspecConfig(Struct):
    foo: Annotated[int, Env("FOO")]
    ignoreme: str = "asdf"


class PydanticConfig(BaseModel):
    foo: Annotated[int, Env("FOO")]
    ignoreme: str = "asdf"


@pydantic_dataclass
class PDataclassConfig:
    foo: Annotated[int, Env("FOO")]
    ignoreme: str = "asdf"


@pytest.mark.parametrize(
    "config_class, exc_class",
    [
        (AttrConfig, TypeError),
        (DataclassConfig, TypeError),
        (MsgspecConfig, TypeError),
        (PydanticConfig, ValidationError),
        (PDataclassConfig, ValidationError),
    ],
)
def test_missing_required(config_class, exc_class):
    with env_setup({}), pytest.raises(exc_class):
        load_settings(config_class)


@pytest.mark.parametrize(
    "config_class",
    [
        AttrConfig,
        DataclassConfig,
        MsgspecConfig,
        PydanticConfig,
        PDataclassConfig,
    ],
)
def test_has_required_required(config_class):
    with env_setup({"FOO": "1", "VALUE": "two"}):
        config = load_settings(config_class)

    assert config == config_class(foo=1, ignoreme="asdf")


@attr_dataclass
class AttrConfigFallback:
    foo: Annotated[int, Env("FOO")]
    default: Annotated[str, Env("MEOW", "UHH")] = "ok"


@dataclass
class DataclassConfigFallback:
    foo: Annotated[int, Env("FOO")]
    default: Annotated[str, Env("MEOW", "UHH")] = "ok"


class MsgspecConfigFallback(Struct):
    foo: Annotated[int, Env("FOO")]
    default: Annotated[str, Env("MEOW", "UHH")] = "ok"


class PydanticConfigFallback(BaseModel):
    foo: Annotated[int, Env("FOO")]
    default: Annotated[str, Env("MEOW", "UHH")] = "ok"


@pydantic_dataclass
class PDataclassConfigFallback:
    foo: Annotated[int, Env("FOO")]
    default: Annotated[str, Env("MEOW", "UHH")] = "ok"


@pytest.mark.parametrize(
    "config_class",
    [
        AttrConfigFallback,
        DataclassConfigFallback,
        MsgspecConfigFallback,
        PydanticConfigFallback,
        PDataclassConfigFallback,
    ],
)
def test_fallback(config_class):
    with env_setup({"FOO": "1", "VALUE": "two", "UHH": "3"}):
        config = load_settings(config_class)

    assert config == config_class(foo=1, default="3")


@attr_dataclass
class AttrConfigNestedBar:
    value: Annotated[str, Env("VALUE")]
    meow: Annotated[str, Env("MEOW")] = "meow"
    default: Annotated[str, Env("MEOW", "UHH")] = "ok"


@attr_dataclass
class AttrConfigNested:
    foo: Annotated[int, Env("FOO")]
    bar: AttrConfigNestedBar
    ignoreme: str = "asdf"


@dataclass
class DataclassConfigNestedBar:
    value: Annotated[str, Env("VALUE")]
    meow: Annotated[str, Env("MEOW")] = "meow"
    default: Annotated[str, Env("MEOW", "UHH")] = "ok"


@dataclass
class DataclassConfigNested:
    foo: Annotated[int, Env("FOO")]
    bar: DataclassConfigNestedBar
    ignoreme: str = "asdf"


class MsgspecConfigNestedBar(Struct):
    value: Annotated[str, Env("VALUE")]
    meow: Annotated[str, Env("MEOW")] = "meow"
    default: Annotated[str, Env("MEOW", "UHH")] = "ok"


class MsgspecConfigNested(Struct):
    foo: Annotated[int, Env("FOO")]
    bar: MsgspecConfigNestedBar
    ignoreme: str = "asdf"


class PydanticConfigNestedBar(BaseModel):
    value: Annotated[str, Env("VALUE")]
    meow: Annotated[str, Env("MEOW")] = "meow"
    default: Annotated[str, Env("MEOW", "UHH")] = Field(default="ok")


class PydanticConfigNested(BaseModel):
    foo: Annotated[int, Env("FOO")]
    bar: PydanticConfigNestedBar
    ignoreme: str = "asdf"


@pydantic_dataclass
class PDataclassConfigNestedBar:
    value: Annotated[str, Env("VALUE")]
    meow: Annotated[str, Env("MEOW")] = "meow"
    default: Annotated[str, Env("MEOW", "UHH")] = "ok"


@pydantic_dataclass
class PDataclassConfigNested:
    foo: Annotated[int, Env("FOO")]
    bar: PDataclassConfigNestedBar
    ignoreme: str = "asdf"


@pytest.mark.parametrize(
    "config_class, config_class_nested",
    [
        (AttrConfigNested, AttrConfigNestedBar),
        (DataclassConfigNested, DataclassConfigNestedBar),
        (MsgspecConfigNested, MsgspecConfigNestedBar),
        (PydanticConfigNested, PydanticConfigNestedBar),
        (PDataclassConfigNested, PDataclassConfigNestedBar),
    ],
)
def test_nested_object(config_class, config_class_nested):
    with env_setup({"FOO": "1", "VALUE": "two", "UHH": "3"}):
        config = load_settings(config_class)

    assert config == config_class(
        foo=1,
        bar=config_class_nested(value="two", meow="meow", default="3"),
        ignoreme="asdf",
    )


@attr_dataclass
class AttrsBar:
    value: Annotated[int, Env("VALUE")]


@attr_dataclass
class AttrsFoo:
    bar: AttrsBar


@dataclass
class AttrsConfigDelimiter:
    foo: AttrsFoo


@dataclass
class DataclassBar:
    value: Annotated[int, Env("VALUE")]


@dataclass
class DataclassFoo:
    bar: DataclassBar


@dataclass
class DataclassConfigDelimiter:
    foo: DataclassFoo


class MsgspecBar(Struct):
    value: Annotated[int, Env("VALUE")]


class MsgspecFoo(Struct):
    bar: MsgspecBar


class MsgspecConfigDelimiter(Struct):
    foo: MsgspecFoo


class PydanticBar(BaseModel):
    value: Annotated[int, Env("VALUE")]


class PydanticFoo(BaseModel):
    bar: PydanticBar


class PydanticConfigDelimiter(BaseModel):
    foo: PydanticFoo


@pydantic_dataclass
class PydanticBarDataclass:
    value: Annotated[int, Env("VALUE")]


@pydantic_dataclass
class PydanticFooDataclass:
    bar: PydanticBarDataclass


@dataclass
class PydanticConfigDelimiterDataclass:
    foo: PydanticFooDataclass


@pytest.mark.parametrize(
    "config_class, foo, bar",
    [
        (AttrsConfigDelimiter, AttrsFoo, AttrsBar),
        (DataclassConfigDelimiter, DataclassFoo, DataclassBar),
        (MsgspecConfigDelimiter, MsgspecFoo, MsgspecBar),
        (PydanticConfigDelimiter, PydanticFoo, PydanticBar),
        (PydanticConfigDelimiterDataclass, PydanticFooDataclass, PydanticBarDataclass),
    ],
)
def test_nested_delimiter(config_class, foo, bar):
    with env_setup({"FOO__BAR__VALUE": "15"}):
        config = load_settings(config_class, nested_delimiter="__")
    assert config == config_class(foo=foo(bar=bar(value=15)))


@attr_dataclass
class AttrConfigNonEnvFields:
    value1: Annotated[int, Env("VALUE")]
    value2: str = "foo"
    value3: List[str] = attr_field(default=["foo"])


@dataclass
class DataclassConfigNonEnvFields:
    value1: Annotated[int, Env("VALUE")]
    value2: str = "foo"
    value3: List[str] = dataclass_field(default_factory=lambda: ["foo"])


class MsgspecConfigNonEnvFields(Struct):
    value1: Annotated[int, Env("VALUE")]
    value2: str = "foo"
    value3: List[str] = msgspec_field(default_factory=lambda: ["foo"])


class PydanticConfigNonEnvFields(BaseModel):
    value1: Annotated[int, Env("VALUE")]
    value2: str = "foo"
    value3: List[str] = ["foo"]


@pydantic_dataclass
class PDataclassConfigNonEnvFields:
    value1: Annotated[int, Env("VALUE")]
    value2: str = "foo"
    value3: List[str] = dataclass_field(default_factory=lambda: ["foo"])


@pytest.mark.parametrize(
    "config_class",
    [
        AttrConfigNonEnvFields,
        DataclassConfigNonEnvFields,
        MsgspecConfigNonEnvFields,
        PydanticConfigNonEnvFields,
        PDataclassConfigNonEnvFields,
    ],
)
def test_ignore_non_env_fields(config_class):
    with env_setup({"VALUE": "15"}):
        config = load_settings(config_class, nested_delimiter="__")

    assert config == config_class(value1=15, value2="foo", value3=["foo"])


class Foo(BaseModel):
    value: Annotated[int, Env("VALUE")]


@attr_dataclass
class AttrsOptionalNested:
    foo: Union[Foo, None] = None


@dataclass
class DataclassOptionalNested:
    foo: Union[Foo, None] = None


class MsgspecOptionalNested(Struct):
    foo: Union[Foo, None] = None


class PydanticOptionalNested(BaseModel):
    foo: Union[Foo, None] = None


@pydantic_dataclass
class PydanticOptionalNestedDataclass:
    foo: Union[Foo, None] = None


@pytest.mark.parametrize(
    "config_class",
    [
        AttrsOptionalNested,
        DataclassOptionalNested,
        MsgspecOptionalNested,
        PydanticOptionalNested,
        PydanticOptionalNestedDataclass,
    ],
)
def test_optional_nested_object(config_class):
    with env_setup({}):
        config = load_settings(config_class, nested_delimiter="__")

    assert config == config_class(foo=None)


@attr_dataclass
class AttrsAnnotationSkipped:
    foo: Annotated[str, ""] = ""


@dataclass
class DataclassAnnotationSkipped:
    foo: Annotated[str, ""] = ""


class MsgspecAnnotationSkipped(Struct):
    foo: Annotated[str, ""] = ""


class PydanticAnnotationSkipped(BaseModel):
    foo: Annotated[str, ""] = ""


@pydantic_dataclass
class PydanticAnnotationSkippedDataclass:
    foo: Annotated[str, ""] = ""


@pytest.mark.parametrize(
    "config_class",
    [
        AttrsAnnotationSkipped,
        DataclassAnnotationSkipped,
        MsgspecAnnotationSkipped,
        PydanticAnnotationSkipped,
        PydanticAnnotationSkippedDataclass,
    ],
)
def test_arbitrary_annotation_skipped(config_class):
    with env_setup({}):
        config = load_settings(config_class)

    assert config == config_class()


def test_union_of_supportable_class_types():
    class Foo(BaseModel): ...

    class Bar(BaseModel): ...

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
