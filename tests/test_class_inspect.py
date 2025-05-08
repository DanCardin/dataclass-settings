from pydantic import BaseModel

from dataclass_settings import load_settings


def test_successful_validation_of_fully_default_subobjects():
    class Foo(BaseModel):
        foo: int = 0

    class Config(BaseModel):
        foo: Foo

    config = load_settings(Config)
    assert config == Config(foo=Foo(foo=0))
