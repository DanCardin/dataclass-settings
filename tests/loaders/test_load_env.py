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
class AttrRequired:
    foo: Annotated[int, Env("FOO")]
    ignoreme: str = "asdf"


@dataclass
class DataclassRequired:
    foo: Annotated[int, Env("FOO")]
    ignoreme: str = "asdf"


class MsgspecRequired(Struct):
    foo: Annotated[int, Env("FOO")]
    ignoreme: str = "asdf"


class PydanticRequired(BaseModel):
    foo: Annotated[int, Env("FOO")]
    ignoreme: str = "asdf"


@pydantic_dataclass
class PDataclassRequired:
    foo: Annotated[int, Env("FOO")]
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
    with env_setup({}), pytest.raises(exc_class):
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
    with env_setup({"FOO": "1", "VALUE": "two"}):
        config = load_settings(config_class)

    assert config == config_class(foo=1, ignoreme="asdf")


@attr_dataclass
class AttrFallback:
    foo: Annotated[int, Env("FOO")]
    default: Annotated[str, Env("MEOW", "UHH")] = "ok"


@dataclass
class DataclassFallback:
    foo: Annotated[int, Env("FOO")]
    default: Annotated[str, Env("MEOW", "UHH")] = "ok"


class MsgspecFallback(Struct):
    foo: Annotated[int, Env("FOO")]
    default: Annotated[str, Env("MEOW", "UHH")] = "ok"


class PydanticFallback(BaseModel):
    foo: Annotated[int, Env("FOO")]
    default: Annotated[str, Env("MEOW", "UHH")] = "ok"


@pydantic_dataclass
class PDataclassFallback:
    foo: Annotated[int, Env("FOO")]
    default: Annotated[str, Env("MEOW", "UHH")] = "ok"


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
    with env_setup({"FOO": "1", "VALUE": "two", "UHH": "3"}):
        config = load_settings(config_class)

    assert config == config_class(foo=1, default="3")


@attr_dataclass
class AttrNestedBar:
    value: Annotated[str, Env("VALUE")]
    meow: Annotated[str, Env("MEOW")] = "meow"
    default: Annotated[str, Env("MEOW", "UHH")] = "ok"


@attr_dataclass
class AttrNested:
    foo: Annotated[int, Env("FOO")]
    bar: AttrNestedBar
    ignoreme: str = "asdf"


@dataclass
class DataclassNestedBar:
    value: Annotated[str, Env("VALUE")]
    meow: Annotated[str, Env("MEOW")] = "meow"
    default: Annotated[str, Env("MEOW", "UHH")] = "ok"


@dataclass
class DataclassNested:
    foo: Annotated[int, Env("FOO")]
    bar: DataclassNestedBar
    ignoreme: str = "asdf"


class MsgspecNestedBar(Struct):
    value: Annotated[str, Env("VALUE")]
    meow: Annotated[str, Env("MEOW")] = "meow"
    default: Annotated[str, Env("MEOW", "UHH")] = "ok"


class MsgspecNested(Struct):
    foo: Annotated[int, Env("FOO")]
    bar: MsgspecNestedBar
    ignoreme: str = "asdf"


class PydanticNestedBar(BaseModel):
    value: Annotated[str, Env("VALUE")]
    meow: Annotated[str, Env("MEOW")] = "meow"
    default: Annotated[str, Env("MEOW", "UHH")] = Field(default="ok")


class PydanticNested(BaseModel):
    foo: Annotated[int, Env("FOO")]
    bar: PydanticNestedBar
    ignoreme: str = "asdf"


@pydantic_dataclass
class PDataclassNestedBar:
    value: Annotated[str, Env("VALUE")]
    meow: Annotated[str, Env("MEOW")] = "meow"
    default: Annotated[str, Env("MEOW", "UHH")] = "ok"


@pydantic_dataclass
class PDataclassNested:
    foo: Annotated[int, Env("FOO")]
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


@attr_dataclass
class AttrsDelimiter:
    foo: AttrsFoo


@dataclass
class DataclassBar:
    value: Annotated[int, Env("VALUE")]


@dataclass
class DataclassFoo:
    bar: DataclassBar


@dataclass
class DataclassDelimiter:
    foo: DataclassFoo


class MsgspecBar(Struct):
    value: Annotated[int, Env("VALUE")]


class MsgspecFoo(Struct):
    bar: MsgspecBar


class MsgspecDelimiter(Struct):
    foo: MsgspecFoo


class PydanticBar(BaseModel):
    value: Annotated[int, Env("VALUE")]


class PydanticFoo(BaseModel):
    bar: PydanticBar


class PydanticDelimiter(BaseModel):
    foo: PydanticFoo


@pydantic_dataclass
class PydanticBarDataclass:
    value: Annotated[int, Env("VALUE")]


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
    with env_setup({"FOO__BAR__VALUE": "15"}):
        config = load_settings(config_class, nested_delimiter="__")
    assert config == config_class(foo=foo(bar=bar(value=15)))


@attr_dataclass
class AttrNonEnvFields:
    value1: Annotated[int, Env("VALUE")]
    value2: str = "foo"
    value3: List[str] = attr_field(default=["foo"])


@dataclass
class DataclassNonEnvFields:
    value1: Annotated[int, Env("VALUE")]
    value2: str = "foo"
    value3: List[str] = dataclass_field(default_factory=lambda: ["foo"])


class MsgspecNonEnvFields(Struct):
    value1: Annotated[int, Env("VALUE")]
    value2: str = "foo"
    value3: List[str] = msgspec_field(default_factory=lambda: ["foo"])


class PydanticNonEnvFields(BaseModel):
    value1: Annotated[int, Env("VALUE")]
    value2: str = "foo"
    value3: List[str] = ["foo"]


@pydantic_dataclass
class PDataclassNonEnvFields:
    value1: Annotated[int, Env("VALUE")]
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
    with env_setup({"VALUE": "15"}):
        config = load_settings(config_class, nested_delimiter="__")

    assert config == config_class(value1=15, value2="foo", value3=["foo"])


class AribitraryNestedFoo(BaseModel):
    value: Annotated[int, Env("VALUE")]


@attr_dataclass
class AttrsOptionalNested:
    foo: Union[AribitraryNestedFoo, None] = None


@dataclass
class DataclassOptionalNested:
    foo: Union[AribitraryNestedFoo, None] = None


class MsgspecOptionalNested(Struct):
    foo: Union[AribitraryNestedFoo, None] = None


class PydanticOptionalNested(BaseModel):
    foo: Union[AribitraryNestedFoo, None] = None


@pydantic_dataclass
class PydanticOptionalNestedDataclass:
    foo: Union[AribitraryNestedFoo, None] = None


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
    with env_setup({}), pytest.raises(ValueError):
        load_settings(config_class)


@attr_dataclass
class AttrsFooInfer:
    nested: Annotated[str, Env()]


@attr_dataclass
class AttrsInferName:
    foo: AttrsFooInfer
    bar: Annotated[int, Env()]


@dataclass
class DataclassFooInfer:
    nested: Annotated[str, Env()]


@dataclass
class DataclassInferName:
    foo: DataclassFooInfer
    bar: Annotated[int, Env()]


class MsgspecFooInfer(Struct):
    nested: Annotated[str, Env()]


class MsgspecInferName(Struct):
    foo: MsgspecFooInfer
    bar: Annotated[int, Env()]


class PydanticFooInfer(BaseModel):
    nested: Annotated[str, Env()]


class PydanticInferName(BaseModel):
    foo: PydanticFooInfer
    bar: Annotated[int, Env()]


@pydantic_dataclass
class PydanticFooInferDataclass:
    nested: Annotated[str, Env()]


@pydantic_dataclass
class PydanticInferNameDataclass:
    foo: PydanticFooInferDataclass
    bar: Annotated[int, Env()]


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
    with env_setup({"BAR": "2", "FOO_NESTED": "nest!"}):
        config = load_settings(config_class, nested_delimiter="_", infer_names=True)

    expected_result = config_class(bar=2, foo=config_infer_name(nested="nest!"))
    assert config == expected_result


@attr_dataclass
class AttrsMissingInfer:
    bar: Annotated[int, Env()]


@dataclass
class DataclassMissingInfer:
    bar: Annotated[int, Env()]


class MsgspecMissingInfer(Struct):
    bar: Annotated[int, Env()]


class PydanticMissingInfer(BaseModel):
    bar: Annotated[int, Env()]


@pydantic_dataclass
class PydanticMissingInferDataclass:
    bar: Annotated[int, Env()]


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
        == "Env instance for `bar` supplies no `env_var` and `infer_names` is enabled"
    )


@attr_dataclass
class AttrsFooError:
    nested: Annotated[str, Env()]
    bar: Annotated[str, Env()]


@attr_dataclass
class AttrsLoadError:
    foo: AttrsFooError


@dataclass
class DataclassFooError:
    nested: Annotated[str, Env()]
    bar: Annotated[str, Env()]


@dataclass
class DataclassLoadError:
    foo: DataclassFooError


class MsgspecFooError(Struct):
    nested: Annotated[str, Env()]
    bar: Annotated[str, Env()]


class MsgspecLoadError(Struct):
    foo: MsgspecFooError


class PydanticFooError(BaseModel):
    nested: Annotated[str, Env()]
    bar: Annotated[str, Env()]


class PydanticLoadError(BaseModel):
    foo: PydanticFooError


@pydantic_dataclass
class PydanticFooErrorDataclass:
    nested: Annotated[str, Env()]
    bar: Annotated[str, Env()]


@pydantic_dataclass
class PydanticLoadErrorDataclass:
    foo: PydanticFooErrorDataclass


@pytest.mark.parametrize(
    "config_class, error_cls",
    [
        (AttrsLoadError, TypeError),
        (DataclassLoadError, TypeError),
        (MsgspecLoadError, TypeError),
        (PydanticLoadError, ValidationError),
        (PydanticLoadErrorDataclass, ValidationError),
    ],
)
def test_setting_load_error(caplog, config_class, error_cls):
    with env_setup({"BAR": "one"}), pytest.raises(error_cls):
        load_settings(config_class, infer_names=True, emit_history=True)

    message = caplog.messages[0]
    assert message == textwrap.dedent(
        """\
        foo.nested:
         - Used `Env` to read 'nested', found 'None'. Skipping.

        foo.bar:
         - Used `Env` to read 'bar', found 'one'.
        """
    )
