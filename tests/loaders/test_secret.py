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

from dataclass_settings import Secret, load_settings
from tests.utils import env_setup


@attr_dataclass
class AttrRequired:
    foo: Annotated[int, Secret("foo")]
    ignoreme: str = "asdf"


@dataclass
class DataclassRequired:
    foo: Annotated[int, Secret("foo")]
    ignoreme: str = "asdf"


class MsgspecRequired(Struct):
    foo: Annotated[int, Secret("foo")]
    ignoreme: str = "asdf"


class PydanticRequired(BaseModel):
    foo: Annotated[int, Secret("foo")]
    ignoreme: str = "asdf"


@pydantic_dataclass
class PDataclassRequired:
    foo: Annotated[int, Secret("foo")]
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


@attr_dataclass
class AttrNestedBar:
    value: Annotated[str, Secret("value")]
    meow: Annotated[str, Secret("meow")] = "meow"
    default: Annotated[str, Secret("meow", "uhh")] = "ok"


@attr_dataclass
class AttrNested:
    foo: Annotated[int, Secret("foo")]
    bar: AttrNestedBar
    ignoreme: str = "asdf"


@dataclass
class DataclassNestedBar:
    value: Annotated[str, Secret("value")]
    meow: Annotated[str, Secret("meow")] = "meow"
    default: Annotated[str, Secret("meow", "uhh")] = "ok"


@dataclass
class DataclassNested:
    foo: Annotated[int, Secret("foo")]
    bar: DataclassNestedBar
    ignoreme: str = "asdf"


class MsgspecNestedBar(Struct):
    value: Annotated[str, Secret("value")]
    meow: Annotated[str, Secret("meow")] = "meow"
    default: Annotated[str, Secret("meow", "uhh")] = "ok"


class MsgspecNested(Struct):
    foo: Annotated[int, Secret("foo")]
    bar: MsgspecNestedBar
    ignoreme: str = "asdf"


class PydanticNestedBar(BaseModel):
    value: Annotated[str, Secret("value")]
    meow: Annotated[str, Secret("meow")] = "meow"
    default: Annotated[str, Secret("meow", "uhh")] = Field(default="ok")


class PydanticNested(BaseModel):
    foo: Annotated[int, Secret("foo")]
    bar: PydanticNestedBar
    ignoreme: str = "asdf"


@pydantic_dataclass
class PDataclassNestedBar:
    value: Annotated[str, Secret("value")]
    meow: Annotated[str, Secret("meow")] = "meow"
    default: Annotated[str, Secret("meow", "uhh")] = "ok"


@pydantic_dataclass
class PDataclassNested:
    foo: Annotated[int, Secret("foo")]
    bar: PDataclassNestedBar
    ignoreme: str = "asdf"


@pytest.mark.parametrize(
    "config_class, config_class_nested",
    [
        (AttrNested, AttrNestedBar),
        (DataclassNested, DataclassNestedBar),
        (MsgspecNested, MsgspecNestedBar),
        (PydanticNested, PydanticNestedBar),
        (PDataclassNested, PDataclassNestedBar),
    ],
)
def test_nested_object(config_class, config_class_nested):
    with env_setup(
        files={
            "/run/secrets/foo": "1",
            "/run/secrets/value": "two",
            "/run/secrets/uhh": "3",
        }
    ):
        config = load_settings(config_class)

    assert config == config_class(
        foo=1,
        bar=config_class_nested(value="two", meow="meow", default="3"),
        ignoreme="asdf",
    )


@attr_dataclass
class AttrsBar:
    value: Annotated[int, Secret("value")]


@attr_dataclass
class AttrsFoo:
    bar: AttrsBar


@attr_dataclass
class AttrsDelimiter:
    foo: AttrsFoo


@dataclass
class DataclassBar:
    value: Annotated[int, Secret("value")]


@dataclass
class DataclassFoo:
    bar: DataclassBar


@dataclass
class DataclassDelimiter:
    foo: DataclassFoo


class MsgspecBar(Struct):
    value: Annotated[int, Secret("value")]


class MsgspecFoo(Struct):
    bar: MsgspecBar


class MsgspecDelimiter(Struct):
    foo: MsgspecFoo


class PydanticBar(BaseModel):
    value: Annotated[int, Secret("value")]


class PydanticFoo(BaseModel):
    bar: PydanticBar


class PydanticDelimiter(BaseModel):
    foo: PydanticFoo


@pydantic_dataclass
class PydanticBarDataclass:
    value: Annotated[int, Secret("value")]


@pydantic_dataclass
class PydanticFooDataclass:
    bar: PydanticBarDataclass


@pydantic_dataclass
class PydanticDelimiterDataclass:
    foo: PydanticFooDataclass


@pytest.mark.parametrize(
    "config_class, foo, bar",
    [
        (AttrsDelimiter, AttrsFoo, AttrsBar),
        (DataclassDelimiter, DataclassFoo, DataclassBar),
        (MsgspecDelimiter, MsgspecFoo, MsgspecBar),
        (PydanticDelimiter, PydanticFoo, PydanticBar),
        (PydanticDelimiterDataclass, PydanticFooDataclass, PydanticBarDataclass),
    ],
)
def test_nested_delimiter(config_class, foo, bar):
    with env_setup(files={"/run/secrets/foo__bar__value": "15"}):
        config = load_settings(config_class, nested_delimiter="__")

    assert config == config_class(foo=foo(bar=bar(value=15)))


@attr_dataclass
class AttrNonEnvFields:
    value1: Annotated[int, Secret("value")]
    value2: str = "foo"
    value3: List[str] = attr_field(default=["foo"])


@dataclass
class DataclassNonEnvFields:
    value1: Annotated[int, Secret("value")]
    value2: str = "foo"
    value3: List[str] = dataclass_field(default_factory=lambda: ["foo"])


class MsgspecNonEnvFields(Struct):
    value1: Annotated[int, Secret("value")]
    value2: str = "foo"
    value3: List[str] = msgspec_field(default_factory=lambda: ["foo"])


class PydanticNonEnvFields(BaseModel):
    value1: Annotated[int, Secret("value")]
    value2: str = "foo"
    value3: List[str] = ["foo"]


@pydantic_dataclass
class PDataclassNonEnvFields:
    value1: Annotated[int, Secret("value")]
    value2: str = "foo"
    value3: List[str] = dataclass_field(default_factory=lambda: ["foo"])


@pytest.mark.parametrize(
    "config_class",
    [
        AttrNonEnvFields,
        DataclassNonEnvFields,
        MsgspecNonEnvFields,
        PydanticNonEnvFields,
        PDataclassNonEnvFields,
    ],
)
def test_ignore_non_env_fields(config_class):
    with env_setup(files={"/run/secrets/value": "15"}):
        config = load_settings(config_class, nested_delimiter="__")

    assert config == config_class(value1=15, value2="foo", value3=["foo"])


class ArbitraryNestedFoo(BaseModel):
    value: Annotated[int, Secret("value")]


@attr_dataclass
class AttrOptionalNested:
    foo: Union[ArbitraryNestedFoo, None] = None


@dataclass
class DataclassOptionalNested:
    foo: Union[ArbitraryNestedFoo, None] = None


class MsgspecOptionalNested(Struct):
    foo: Union[ArbitraryNestedFoo, None] = None


class PydanticOptionalNested(BaseModel):
    foo: Union[ArbitraryNestedFoo, None] = None


@pydantic_dataclass
class PDataclassOptionalNested:
    foo: Union[ArbitraryNestedFoo, None] = None


@pytest.mark.parametrize(
    "config_class",
    [
        AttrOptionalNested,
        DataclassOptionalNested,
        MsgspecOptionalNested,
        PydanticOptionalNested,
        PDataclassOptionalNested,
    ],
)
def test_optional_nested_object(config_class):
    with env_setup():
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
    with env_setup():
        config = load_settings(config_class)

    assert config == config_class()


@attr_dataclass
class AttrsFooU: ...


@attr_dataclass
class AttrsBarU: ...


@attr_dataclass
class AttrsUnion:
    foo: Union[AttrsFooU, AttrsBarU]


@dataclass
class DataclassFooU: ...


@dataclass
class DataclassBarU: ...


@dataclass
class DataclassUnion:
    foo: Union[DataclassFooU, DataclassBarU]


class MsgspecFooU(Struct): ...


class MsgspecBarU(Struct): ...


class MsgspecUnion(Struct):
    foo: Union[MsgspecFooU, MsgspecBarU]


class PydanticFooU(BaseModel): ...


class PydanticBarU(BaseModel): ...


class PydanticUnion(BaseModel):
    foo: Union[PydanticFooU, PydanticBarU]


@pydantic_dataclass
class PDataclassFooU: ...


@pydantic_dataclass
class PDataclassBarU: ...


@pydantic_dataclass
class PDataclassUnion:
    foo: Union[PDataclassFooU, PDataclassBarU]


@pytest.mark.parametrize(
    "config_class",
    [AttrsUnion, DataclassUnion, MsgspecUnion, PydanticUnion, PDataclassUnion],
)
def test_union_of_supportable_class_types(config_class):
    with env_setup(), pytest.raises(ValueError):
        load_settings(config_class)


@attr_dataclass
class AttrsFooInfer:
    nested: Annotated[str, Secret()]


@attr_dataclass
class AttrsInferName:
    foo: AttrsFooInfer
    bar: Annotated[int, Secret()]


@dataclass
class DataclassFooInfer:
    nested: Annotated[str, Secret()]


@dataclass
class DataclassInferName:
    foo: DataclassFooInfer
    bar: Annotated[int, Secret()]


class MsgspecFooInfer(Struct):
    nested: Annotated[str, Secret()]


class MsgspecInferName(Struct):
    foo: MsgspecFooInfer
    bar: Annotated[int, Secret()]


class PydanticFooInfer(BaseModel):
    nested: Annotated[str, Secret()]


class PydanticInferName(BaseModel):
    foo: PydanticFooInfer
    bar: Annotated[int, Secret()]


@pydantic_dataclass
class PydanticFooInferDataclass:
    nested: Annotated[str, Secret()]


@pydantic_dataclass
class PydanticInferNameDataclass:
    foo: PydanticFooInferDataclass
    bar: Annotated[int, Secret()]


@pytest.mark.parametrize(
    "config_class, config_infer_name",
    [
        (AttrsInferName, AttrsFooInfer),
        (DataclassInferName, DataclassFooInfer),
        (MsgspecInferName, MsgspecFooInfer),
        (PydanticInferName, dict),
        (PydanticInferNameDataclass, dict),
    ],
)
def test_infer_name(config_class, config_infer_name):
    with env_setup(files={"/run/secrets/bar": "2", "/run/secrets/foo_nested": "nest!"}):
        config = load_settings(config_class, nested_delimiter="_", infer_names=True)

    assert config == config_class(bar=2, foo=config_infer_name(nested="nest!"))


@attr_dataclass
class AttrsMissingInfer:
    bar: Annotated[int, Secret()]


@dataclass
class DataclassMissingInfer:
    bar: Annotated[int, Secret()]


class MsgspecMissingInfer(Struct):
    bar: Annotated[int, Secret()]


class PydanticMissingInfer(BaseModel):
    bar: Annotated[int, Secret()]


@pydantic_dataclass
class PydanticMissingInferDataclass:
    bar: Annotated[int, Secret()]


@pytest.mark.parametrize(
    "config_class",
    [
        AttrsMissingInfer,
        DataclassMissingInfer,
        MsgspecMissingInfer,
        PydanticMissingInfer,
        PydanticMissingInferDataclass,
    ],
)
def test_missing_infer_name_or_env_var(config_class):
    with env_setup(), pytest.raises(ValueError) as e:
        load_settings(config_class)

    assert (
        str(e.value)
        == "Secret instance for `bar` supplies no name and `infer_names` is enabled"
    )


def test_common_dir_name_override():
    my_secret = Secret(dir="/foo/bar")

    class Foo(BaseModel):
        nested: Annotated[str, my_secret.with_name("meow")]

    class Config(BaseModel):
        foo: Foo
        bar: Annotated[int, my_secret]

    with env_setup(files={"/foo/bar/bar": "2", "/foo/bar/foo_meow": "nest!"}):
        config = load_settings(Config, nested_delimiter="_", infer_names=True)

    assert config == Config(bar=2, foo=Foo(nested="nest!"))


def test_dir_fallback():
    class Foo(BaseModel):
        nested: Annotated[str, Secret(dir=("/asdf", "/foo/bar"))]

    my_secret = Secret(dir=("/asdf", "/foo/bar"))

    class Config(BaseModel):
        foo: Foo
        bar: Annotated[int, my_secret]

    with env_setup(files={"/foo/bar/foo_nested": "nest!", "/asdf/bar": "2"}):
        config = load_settings(Config, nested_delimiter="_", infer_names=True)

    assert config == Config(bar=2, foo=Foo(nested="nest!"))


def test_dir_configured_at_loader_inferred_name():
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
            extra_loaders=Secret.load_with(dir=("/foo/bar", "/bar/baz")),
        )

    assert config == Config(bar=2, foo=Foo(nested="nest!"))

    with env_setup(files={"/foo/bar/foo_nested": "nest!", "/bar/baz/bar": "2"}):
        config = load_settings(
            Config,
            nested_delimiter="_",
            infer_names=True,
            extra_loaders=Secret.load_with(dir="/foo/bar"),
        )

    assert config == Config(bar=3, foo=Foo(nested="nest!"))


def test_dir_configured_at_loader():
    class Foo(BaseModel):
        nested: Annotated[str, Secret("asdf")]

    class Config(BaseModel):
        foo: Foo
        bar: Annotated[int, Secret("bart")]

    with env_setup(files={"/foo/bar/asdf": "nest!", "/bar/baz/bart": "2"}):
        config = load_settings(
            Config,
            extra_loaders=Secret.load_with(dir=("/foo/bar", "/bar/baz")),
        )

    assert config == Config(bar=2, foo=Foo(nested="nest!"))


def test_cached_load(capsys):
    class Config(BaseModel):
        foo: Annotated[int, Secret("bart")]
        bar: Annotated[int, Secret("bart")]

    with env_setup(files={"/run/secrets/bart": "1"}):
        config = load_settings(Config)

    assert config == Config(bar=1, foo=1)

    output_lines = capsys.readouterr().out.strip().split("\n")
    assert len(output_lines) == 1
