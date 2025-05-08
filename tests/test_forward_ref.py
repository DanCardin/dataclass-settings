from __future__ import annotations

from dataclass_settings import load_settings
from tests.utils import (
    AttrConfig,
    AttrFoo,
    DataclassConfig,
    DataclassFoo,
    PDataclassConfig,
    PDataclassFoo,
    PydanticConfig,
    PydanticFoo,
)


def test_pydantic():
    config = load_settings(PydanticConfig)
    assert config == PydanticConfig(foo=PydanticFoo(foo=0))


def test_dataclass():
    config = load_settings(DataclassConfig)
    assert config == DataclassConfig(foo=DataclassFoo(foo=0))


def test_pydantic_dataclass():
    config = load_settings(PDataclassConfig)
    assert config == PDataclassConfig(foo=PDataclassFoo(foo=0))


def test_attr_dataclass():
    config = load_settings(AttrConfig)
    assert config == AttrConfig(foo=AttrFoo(foo=0))
