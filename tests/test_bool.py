from dataclasses import dataclass

import pytest
from attr import dataclass as attr_dataclass
from msgspec import Struct
from pydantic import BaseModel
from pydantic.dataclasses import dataclass as pydantic_dataclass
from typing_extensions import Annotated

from dataclass_settings import Env, Parse, load_settings
from tests.utils import env_setup

TRUTHY_STRINGS = ["1", "true", "t", "yes", "y", "on"]
FALSY_STRINGS = ["0", "false", "f", "no", "n", "off"]


def parse_bool(value: str) -> bool:
    lowered = value.lower()
    if lowered in TRUTHY_STRINGS:
        return True
    if lowered in FALSY_STRINGS:
        return False
    raise ValueError(f"Invalid bool: {value!r}")


Bool = Annotated[bool, Parse(parse_bool)]


@attr_dataclass
class AttrBool:
    no_default_true: Annotated[Bool, Env("NO_DEFAULT_TRUE")]
    no_default_false: Annotated[Bool, Env("NO_DEFAULT_FALSE")]
    default_false: Annotated[Bool, Env("DEFAULT_FALSE")] = False
    default_true: Annotated[Bool, Env("DEFAULT_TRUE")] = True


@dataclass
class DataclassBool:
    no_default_true: Annotated[Bool, Env("NO_DEFAULT_TRUE")]
    no_default_false: Annotated[Bool, Env("NO_DEFAULT_FALSE")]
    default_false: Annotated[Bool, Env("DEFAULT_FALSE")] = False
    default_true: Annotated[Bool, Env("DEFAULT_TRUE")] = True


class MsgspecBool(Struct):
    no_default_true: Annotated[Bool, Env("NO_DEFAULT_TRUE")]
    no_default_false: Annotated[Bool, Env("NO_DEFAULT_FALSE")]
    default_false: Annotated[Bool, Env("DEFAULT_FALSE")] = False
    default_true: Annotated[Bool, Env("DEFAULT_TRUE")] = True


class PydanticBool(BaseModel):
    no_default_true: Annotated[Bool, Env("NO_DEFAULT_TRUE")]
    no_default_false: Annotated[Bool, Env("NO_DEFAULT_FALSE")]
    default_false: Annotated[Bool, Env("DEFAULT_FALSE")] = False
    default_true: Annotated[Bool, Env("DEFAULT_TRUE")] = True


@pydantic_dataclass
class PDataclassBool:
    no_default_true: Annotated[Bool, Env("NO_DEFAULT_TRUE")]
    no_default_false: Annotated[Bool, Env("NO_DEFAULT_FALSE")]
    default_false: Annotated[Bool, Env("DEFAULT_FALSE")] = False
    default_true: Annotated[Bool, Env("DEFAULT_TRUE")] = True


@pytest.mark.parametrize(
    "config_class",
    [
        AttrBool,
        DataclassBool,
        MsgspecBool,
        PydanticBool,
        PDataclassBool,
    ],
)
@pytest.mark.parametrize("true_str", TRUTHY_STRINGS)
@pytest.mark.parametrize("false_str", FALSY_STRINGS)
def test_bool_loading(config_class, true_str, false_str):
    with env_setup(
        {
            "DEFAULT_FALSE": "true",
            "DEFAULT_TRUE": "false",
            "NO_DEFAULT_TRUE": true_str,
            "NO_DEFAULT_FALSE": false_str,
        }
    ):
        config = load_settings(config_class)

    assert config.default_false is True
    assert config.default_true is False
    assert config.no_default_true is True
    assert config.no_default_false is False


def test_parse_error_propagates():
    with env_setup({"NO_DEFAULT_TRUE": "maybe", "NO_DEFAULT_FALSE": "no"}):
        with pytest.raises(ValueError, match="Invalid bool: 'maybe'"):
            load_settings(DataclassBool)
