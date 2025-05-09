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
class AttrRequired:
    foo: Annotated[
        int,
        Toml(
            Path(__file__).parent.parent.parent / "pyproject.toml", "tool.poetry.asdf"
        ),
    ]


@dataclass
class DataclassRequired:
    foo: Annotated[
        int,
        Toml(
            Path(__file__).parent.parent.parent / "pyproject.toml", "tool.poetry.asdf"
        ),
    ]


class MsgspecRequired(Struct):
    foo: Annotated[
        int,
        Toml(
            Path(__file__).parent.parent.parent / "pyproject.toml", "tool.poetry.asdf"
        ),
    ]


class PydanticRequired(BaseModel):
    foo: Annotated[
        int,
        Toml(
            Path(__file__).parent.parent.parent / "pyproject.toml",
            "tool.poetry.asdf",
        ),
    ]


@pydantic_dataclass
class PDataclassRequired:
    foo: Annotated[
        int,
        Toml(
            Path(__file__).parent.parent.parent / "pyproject.toml",
            "tool.poetry.asdf",
        ),
    ]


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


@skip_under(3, 11, reason="Requires tomllib")
def test_has_required_required():
    class Config(BaseModel):
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

    config = load_settings(Config)
    assert config == Config(
        foo="dataclass-settings", ignoreme="asdf", license="Apache-2.0"
    )


@skip_under(3, 11, reason="Requires tomllib")
def test_missing_optional_inferred_name():
    class Config(BaseModel):
        tool: Annotated[
            int, Toml(Path(__file__).parent.parent.parent / "pyproject.toml")
        ]
        ignoreme: str = "asdf"

    with pytest.raises(ValueError) as e:
        load_settings(Config)
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
