# Loaders

A "loader" is defined as a class which implements the
[dataclass_settings.Loader](dataclass_settings.loaders.Loader) protocol. i.e. a
type with a method `load(context: Context)`.

The library ships with a few loaders:

- `Env`: Loads environment variables
- `Secrets`: Loads file contents (defaults to `/run/secrets/...`, which ensures
  compatibility with Docker Secrets)
- `Toml`: Loads values from a toml file

Additional 1st party loaders will be accepted, but any loader which requires
additional dependencies (for example, `AWS Secrets Manager` would imply `boto3`)
**will** be added as optional extras

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
