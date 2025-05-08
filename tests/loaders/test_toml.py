from pathlib import Path

import pytest
from pydantic import BaseModel, ValidationError
from typing_extensions import Annotated

from dataclass_settings import Toml, load_settings
from tests.utils import env_setup, skip_under


@skip_under(3, 11, reason="Requires tomllib")
def test_missing_required():
    class Config(BaseModel):
        foo: Annotated[
            int,
            Toml(
                Path(__file__).parent.parent.parent / "pyproject.toml",
                "tool.poetry.asdf",
            ),
        ]

    with env_setup({}), pytest.raises(ValidationError):
        load_settings(Config)


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
