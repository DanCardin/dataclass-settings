from __future__ import annotations

from dataclasses import dataclass

from attr import dataclass as attr_dataclass
from pydantic import BaseModel
from pydantic.dataclasses import dataclass as pydantic_dataclass

from dataclass_settings import load_settings


class PydanticConfig(BaseModel):
    foo: PydanticFoo


class PydanticFoo(BaseModel):
    foo: int = 0


def test_pydantic():
    config = load_settings(PydanticConfig)
    assert config == PydanticConfig(foo=PydanticFoo(foo=0))


@dataclass
class DataclassConfig:
    foo: DataclassFoo


@dataclass
class DataclassFoo:
    foo: int = 0


def test_dataclass():
    config = load_settings(DataclassConfig)
    assert config == DataclassConfig(foo=DataclassFoo(foo=0))


@pydantic_dataclass
class PDataclassConfig:
    foo: PDataclassFoo


@pydantic_dataclass
class PDataclassFoo:
    foo: int = 0


def test_pydantic_dataclass():
    config = load_settings(PDataclassConfig)
    assert config == PDataclassConfig(foo=PDataclassFoo(foo=0))


@attr_dataclass
class AttrConfig:
    foo: AttrFoo


@attr_dataclass
class AttrFoo:
    foo: int = 0


def test_attr_dataclass():
    config = load_settings(AttrConfig)
    assert config == AttrConfig(foo=AttrFoo(foo=0))
