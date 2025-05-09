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


@attr_dataclass
class AttrMissingRequired:
    asdf: Annotated[
        str, Toml(Path(__file__).parent.parent.parent / "pyproject.toml", "asdf")
    ]


@dataclass
class DataclassMissingRequired:
    asdf: Annotated[
        str, Toml(Path(__file__).parent.parent.parent / "pyproject.toml", "asdf")
    ]


class MsgspecMissingRequired(Struct):
    asdf: Annotated[
        str, Toml(Path(__file__).parent.parent.parent / "pyproject.toml", "asdf")
    ]


class PydanticMissingRequired(BaseModel):
    asdf: Annotated[
        str, Toml(Path(__file__).parent.parent.parent / "pyproject.toml", "asdf")
    ]


@pydantic_dataclass
class PDataclassMissingRequired:
    asdf: Annotated[
        str, Toml(Path(__file__).parent.parent.parent / "pyproject.toml", "asdf")
    ]


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
    foo: Annotated[
        str,
        Toml(
            Path(__file__).parent.parent.parent / "pyproject.toml", "tool.poetry.name"
        ),
    ]
    license: Annotated[
        str,
        Toml(
            Path(__file__).parent.parent.parent / "pyproject.toml",
            "tool.poetry.license",
        ),
    ]
    ignoreme: str = "asdf"


@dataclass
class DataclassRequired:
    foo: Annotated[
        str,
        Toml(
            Path(__file__).parent.parent.parent / "pyproject.toml", "tool.poetry.name"
        ),
    ]
    license: Annotated[
        str,
        Toml(
            Path(__file__).parent.parent.parent / "pyproject.toml",
            "tool.poetry.license",
        ),
    ]
    ignoreme: str = "asdf"


class MsgspecRequired(Struct):
    foo: Annotated[
        str,
        Toml(
            Path(__file__).parent.parent.parent / "pyproject.toml", "tool.poetry.name"
        ),
    ]
    license: Annotated[
        str,
        Toml(
            Path(__file__).parent.parent.parent / "pyproject.toml",
            "tool.poetry.license",
        ),
    ]
    ignoreme: str = "asdf"


class PydanticRequired(BaseModel):
    foo: Annotated[
        str,
        Toml(
            Path(__file__).parent.parent.parent / "pyproject.toml",
            "tool.poetry.name",
        ),
    ]
    license: Annotated[
        str,
        Toml(
            Path(__file__).parent.parent.parent / "pyproject.toml",
            "tool.poetry.license",
        ),
    ]
    ignoreme: str = "asdf"


@pydantic_dataclass
class PDataclassRequired:
    foo: Annotated[
        str,
        Toml(
            Path(__file__).parent.parent.parent / "pyproject.toml",
            "tool.poetry.name",
        ),
    ]
    license: Annotated[
        str,
        Toml(
            Path(__file__).parent.parent.parent / "pyproject.toml",
            "tool.poetry.license",
        ),
    ]
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
        foo="dataclass-settings", ignoreme="asdf", license="Apache-2.0"
    )


@attr_dataclass
class AttrMissingOptionelInferred:
    tool: Annotated[int, Toml(Path(__file__).parent.parent.parent / "pyproject.toml")]
    ignoreme: str = "asdf"


@dataclass
class DataclassMissingOptionelInferred:
    tool: Annotated[int, Toml(Path(__file__).parent.parent.parent / "pyproject.toml")]
    ignoreme: str = "asdf"


class MsgspecMissingOptionelInferred(Struct):
    tool: Annotated[int, Toml(Path(__file__).parent.parent.parent / "pyproject.toml")]
    ignoreme: str = "asdf"


class PydanticMissingOptionelInferred(BaseModel):
    tool: Annotated[int, Toml(Path(__file__).parent.parent.parent / "pyproject.toml")]
    ignoreme: str = "asdf"


@pydantic_dataclass
class PDataclassMissingOptionelInferred:
    tool: Annotated[int, Toml(Path(__file__).parent.parent.parent / "pyproject.toml")]
    ignoreme: str = "asdf"


@skip_under(3, 11, reason="Requires tomllib")
@pytest.mark.parametrize(
    "config_class",
    [
        AttrMissingOptionelInferred,
        DataclassMissingOptionelInferred,
        MsgspecMissingOptionelInferred,
        PydanticMissingOptionelInferred,
        PDataclassMissingOptionelInferred,
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
        tool: Annotated[int, Toml(empty_toml, "tool.poetry.asdf")]

    with env_setup({}), pytest.raises(exc_class):
        load_settings(Config)
