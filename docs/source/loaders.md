# Loaders

A "loader" is defined as a class which implements the
[dataclass_settings.Loader](dataclass_settings.loaders.Loader) protocol. i.e. a
type with a method `load(context: Context)`.

## Builtins

The library ships with a few loaders. Additional 1st party loaders will be accepted,
particularly if they require no external dependencies to implement. Any candidate
loader which requires additional dependencies (for example, `AWS Secrets Manager`, which
would imply `boto3`) **will** be added as optional extras.

### `Env`
`Env` as the name suggests, loads environment variable values.

```python
from __future__ import annotations
from dataclass_settings import load_settings, Env, Secret
from dataclasses import dataclass

@dataclass
class Example:
    env: Annotated[str, Env("ENVIRONMENT")] = "local"
    dsn: Annotated[str, Env("DSN"), Secret('dsn')] = "dsn://"

    sub_config: SubConfig


@dataclass
class SubConfig:
    nested: Annotated[int, Env("NESTED")] = "4"


example: Example = load_settings(Example)

# or, if you want `nested` to be `SUB_CONFIG_NESTED`
example: Example = load_settings(Example, nested_delimiter='_')
```


```{eval-rst}
.. autoapimodule:: dataclass_settings.loaders
   :members: Env
   :noindex:
```


### `Secret`
`Secret` point to files which contain the "secret" value in question. 
This is commonly used in containers/Docker where the location containing the
secret is being mounted into the container at runtime.

The default root location is `/run/secrets`.

```python
from __future__ import annotations
from dataclass_settings import load_settings, Secret
from dataclasses import dataclass

@dataclass
class Example:
    password: Annotated[str, Secret("password")]

example: Example = load_settings(Example)
```

````{note}
Note, if the root location of your secrets is not the default one, or it changes
based on runtime characteristics (running with Docker Secrets, versus inside k8s)
it may be inconvenient to individually annotate each item.

It is possible to centralize such configuration and decouple it from the static
definitions of those secrets.

```python
@dataclass
class Example:
    password: Annotated[str, Secret("password")]


dir = "/run/secrets"
if in_k8s:
    dir = dir="/foo/bar"

loader = Secret.load_with(dir=dir)
example: Example = load_settings(Example, extra_loaders=loader)
```
````


````{note}
`Secret` accepts both multiple secret names, as well as multiple root locations.
For example `Secret("password", "pass", dir=("/run/secrets", "/foo/bar"))`.
They will be searched in order until the first value which resolves.
````

```{eval-rst}
.. autoapimodule:: dataclass_settings.loaders
   :members: Secret
   :noindex:
```


### `Toml`
`Toml` loads values from a toml file. The `key` uses toml's nested naming syntax
to target deeply nested keys.

```python
from __future__ import annotations
from dataclass_settings import load_settings, Toml
from dataclasses import dataclass

## pyproject.toml
# [project]
# name = "dataclass-settings"

@dataclass
class Example:
    password: Annotated[str, Toml("project.name", file='pyproject.toml')]

example: Example = load_settings(Example)
```

Similarly to `Secret`, the loader can be centrally specified in order to target
the same file across a single invocation.

```python
from __future__ import annotations
from dataclass_settings import load_settings, Toml
from dataclasses import dataclass

## pyproject.toml
# [project]
# name = "dataclass-settings"

@dataclass
class Example:
    password: Annotated[str, Toml("project.name")]

loader = Toml.load_with(file="pyproject.toml")
example: Example = load_settings(Example, extra_loaders=loader)
```


## Custom/External Loaders

Defining your own loader is relatively simple:

```python
from typing import Annotated
from pydantic import BaseModel
from dataclass_settings import Loader, load_settings, Context

class FooLoader(Loader):
  prefix: str

  def load(self, context: Context):
    """Adds a prefix str to the end of the field name."""
    return self.prefix + context.field_name


class Config(BaseModel):
  foo: Annotated[str, FooLoader('pref_')]



config: Config = load_settings(Config, extra_loaders=[FooLoader])
assert config == Config(foo='pref_foo')
```

A loader can accept any input values required to look up the setting value in
question.

The [Context](dataclass_settings.context.Context) object contains additional
information about the loading context, such as:

- `context.field_name`: The name of the field being loaded
- `context.path`: The path from the root object to the currently loaded object
- `context.get_name`: Automatically conjoins the `path` and `name` (using
  `nested_delimiter`) if appropriate
- `context.get_state`: Returns loader-specific state.

### `Loader.init`

If your loader requires caching state some state between multiple `load` calls
(such as the above "AWS Secrets Manager" example, where you might want to cache
the `boto3.Session` object), you will need to define an `init`
staticmethod/classmethod.

The return value of that function will be recorded into the `Context`, and
`context.get_state(self)` from inside a `Lodder` instance will return that
state.

```python
from dataclass_settings import Loader, load_settings

class Foo(Loader):
    prefix: str

    @staticmethod
    def init():
        return {'woah': True}

    def load(self, context: Context):
        state = context.get_state(self)
        assert state == {'woah': True}
        ...
```
