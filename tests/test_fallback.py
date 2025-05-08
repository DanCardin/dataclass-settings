from pydantic import BaseModel
from typing_extensions import Annotated

from dataclass_settings import Env, Secret, load_settings
from tests.utils import env_setup


def test_falls_back_to_lower_priority_env():
    class Config(BaseModel):
        foo: Annotated[int, Env("FOO"), Env("BAR")]

    with env_setup(env={"BAR": "4"}):
        config = load_settings(Config)
        assert config == Config(foo=4)


def test_falls_back_to_other_loader():
    class Config(BaseModel):
        foo: Annotated[str, Env("FOO"), Secret("bar")]

    with env_setup(files={"/run/secrets/bar": "one!"}):
        config = load_settings(Config)
        assert config == Config(foo="one!")
