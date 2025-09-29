from dataclasses import dataclass
from pathlib import Path

import pytest
from attr import dataclass as attr_dataclass
from msgspec import Struct
from pydantic import BaseModel, ValidationError
from pydantic.dataclasses import dataclass as pydantic_dataclass
from typing_extensions import Annotated

from dataclass_settings import Toml, load_settings
from tests.utils import env_setup, skip_under

pyproject = Path(__file__).parent.parent.parent / "pyproject.toml"


@attr_dataclass
class AttrMissingRequired:
    asdf: Annotated[str, Toml("asdf", file=pyproject)]


@dataclass
class DataclassMissingRequired:
    asdf: Annotated[str, Toml("asdf", file=pyproject)]


class MsgspecMissingRequired(Struct):
    asdf: Annotated[str, Toml("asdf", file=pyproject)]


class PydanticMissingRequired(BaseModel):
    asdf: Annotated[str, Toml("asdf", file=pyproject)]


@pydantic_dataclass
class PDataclassMissingRequired:
    asdf: Annotated[str, Toml("asdf", file=pyproject)]


@skip_under(3, 11, reason="Requires tomllib")
@pytest.mark.parametrize(
    "config_class, exc_class",
    [
        (AttrMissingRequired, TypeError),
        (DataclassMissingRequired, TypeError),
        (MsgspecMissingRequired, TypeError),
        (PydanticMissingRequired, ValidationError),
        (PDataclassMissingRequired, ValidationError),
    ],
)
def test_missing_required(config_class, exc_class):
    with env_setup({}), pytest.raises(exc_class):
        load_settings(config_class)


@attr_dataclass
class AttrRequired:
    foo: Annotated[str, Toml("project.name", file=pyproject)]
    license: Annotated[str, Toml("project.license.file", file=pyproject)]
    ignoreme: str = "asdf"


@dataclass
class DataclassRequired:
    foo: Annotated[str, Toml("project.name", file=pyproject)]
    license: Annotated[str, Toml("project.license.file", file=pyproject)]
    ignoreme: str = "asdf"


class MsgspecRequired(Struct):
    foo: Annotated[str, Toml("project.name", file=pyproject)]
    license: Annotated[str, Toml("project.license.file", file=pyproject)]
    ignoreme: str = "asdf"


class PydanticRequired(BaseModel):
    foo: Annotated[str, Toml("project.name", file=pyproject)]
    license: Annotated[str, Toml("project.license.file", file=pyproject)]
    ignoreme: str = "asdf"


@pydantic_dataclass
class PDataclassRequired:
    foo: Annotated[str, Toml("project.name", file=pyproject)]
    license: Annotated[str, Toml("project.license.file", file=pyproject)]
    ignoreme: str = "asdf"


@skip_under(3, 11, reason="Requires tomllib")
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
    config = load_settings(config_class)
    assert config == config_class(
        foo="dataclass-settings", ignoreme="asdf", license="LICENSE"
    )


@attr_dataclass
class AttrMissingOptionalInferred:
    tool: Annotated[str, Toml(file=pyproject)]
    ignoreme: str = "asdf"


@dataclass
class DataclassMissingOptionalInferred:
    tool: Annotated[str, Toml(file=pyproject)]
    ignoreme: str = "asdf"


class MsgspecMissingOptionalInferred(Struct):
    tool: Annotated[str, Toml(file=pyproject)]
    ignoreme: str = "asdf"


class PydanticMissingOptionalInferred(BaseModel):
    tool: Annotated[str, Toml(file=pyproject)]
    ignoreme: str = "asdf"


@pydantic_dataclass
class PDataclassMissingOptionalInferred:
    tool: Annotated[str, Toml(file=pyproject)]
    ignoreme: str = "asdf"


@skip_under(3, 11, reason="Requires tomllib")
@pytest.mark.parametrize(
    "config_class",
    [
        AttrMissingOptionalInferred,
        DataclassMissingOptionalInferred,
        MsgspecMissingOptionalInferred,
        PydanticMissingOptionalInferred,
        PDataclassMissingOptionalInferred,
    ],
)
def test_missing_optional_inferred_name(config_class):
    with pytest.raises(ValueError) as e:
        load_settings(config_class)
    assert (
        str(e.value)
        == "Toml instance for `tool` supplies no `key` and `infer_names` is enabled"
    )


@skip_under(3, 11, reason="Requires tomllib")
@pytest.mark.parametrize(
    "config_class, exc_class", [(BaseModel, ValidationError), (Struct, TypeError)]
)
def test_empty_toml(config_class, exc_class, tmp_path: Path):
    empty_toml = tmp_path / "empty.toml"
    empty_toml.write_text("")

    class Config(config_class):
        tool: Annotated[int, Toml("project.asdf", file=empty_toml)]

    with env_setup({}), pytest.raises(exc_class):
        load_settings(Config)


@skip_under(3, 11, reason="Requires tomllib")
def test_toml_int(tmp_path: Path):
    toml_file = tmp_path / "config.toml"
    toml_file.write_text("[postgres]\nport = 42")

    class Config(Struct):
        postgres_port: Annotated[int, Toml("postgres.port", file=toml_file)]
        postgres: Annotated[dict[str, int], Toml("postgres", file=toml_file)]

    config = load_settings(Config)
    assert config.postgres_port == 42
    assert config.postgres == {"port": 42}


@skip_under(3, 11, reason="Requires tomllib")
def test_load_with():
    @dataclass
    class Example:
        name: Annotated[str, Toml("project.name")]

    loader = Toml.load_with(file="pyproject.toml")
    example: Example = load_settings(Example, extra_loaders=loader)
    assert example == Example(name="dataclass-settings")
