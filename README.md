# dataclass-settings

[![Actions Status](https://github.com/DanCardin/dataclass-settings/actions/workflows/test.yml/badge.svg)](https://github.com/dancardin/dataclass-settings/actions)
[![Coverage Status](https://coveralls.io/repos/github/DanCardin/dataclass-settings/badge.svg?branch=main)](https://coveralls.io/github/DanCardin/dataclass-settings?branch=main)
[![Documentation Status](https://readthedocs.org/projects/dataclass-settings/badge/?version=latest)](https://dataclass-settings.readthedocs.io/en/latest/?badge=latest)

- [Full documentation here](https://dataclass-settings.readthedocs.io/en/latest/).
- [Bundled Loaders](https://dataclass-settings.readthedocs.io/en/latest/loaders.html).

`dataclass-settings` intends to work with any
[PEP-681](https://peps.python.org/pep-0681/)-compliant dataclass-like object,
including but not limited to:

- [Pydantic models](https://pydantic-docs.helpmanual.io/) (v1/v2),
- [dataclasses](https://docs.python.org/3/library/dataclasses.html)
- [attrs classes](https://www.attrs.org/en/stable/).

`dataclass-settings` owes its existence
[pydantic-settings](https://github.com/pydantic/pydantic-settings), in that
pydantic-settings will be a benchmark for `dataclass-settings`'s featureset.
However it was bourne out of frustration with pydantic-setting's approach to
implementing that featureset.

## Example

```python
from __future__ import annotations
from dataclass_settings import load_settings, Env, Secret
from pydantic import BaseModel


class Example(BaseModel):
    env: Annotated[str, Env("ENVIRONMENT")] = "local"
    dsn: Annotated[str, Env("DSN"), Secret('dsn')] = "dsn://"

    sub_config: SubConfig


class SubConfig(BaseModel):
    nested: Annotated[int, Env("NESTED")] = "4"


example: Example = load_settings(Example)

# or, if you want `nested` to be `SUB_CONFIG_NESTED`
example: Example = load_settings(Example, nested_delimiter='_')
```

## vs Pydantic Settings

### Simplicity

- `pydantic-settings` alters how you go about defining your normal pydantic
  models. You need to switch (some of the) base classes, you need to configure
  the magical `model_config = SettingsConfigDict(...)` object, etc.

  The model becomes inherently entangled with the settings-loading library.

- `dataclass-settings` attaches targeted Annotations metadata to a vanilla
  pydantic model. You can **choose** to not use `load_settings` (for example, in
  tests), and construct the model instance however you'd like.

### Clarity

- `pydantic-settings` makes it really, really difficult to intuit what the
  concrete environment varibale that's going to be loaded for a given field is
  **actually** going to be. Based on my own experience, and from perusing their
  issue tracker, it seems like this is not an uncommon experience.

  The combination of field name, `SettingsConfigDict` settings, casing,
  `alias`/`validation_alias`/`serialization_alias`, and relative position of the
  env var in the greater config all contribute to it being a **task** to deduce
  which concrete name will be used when loading.

- `dataclass-settings` by **default** requires an explicit, concrete name, which
  maps directly to the value being loaded (`Env('FOO')` loads `FOO`, for sure!)

  If you want to opt into a less explcict, more inferred setup (like
  pydantic-settings), you can do so by utilizing the `nested_delimiter='_'` and
  `infer_name=True` arguments.

### Typing

- `pydantic-settings` does not play **super** well with type checkers,
  necessitating the use of a mypy plugin for it to not emit type errors into
  user code.

  The code recommended in their documentation for namespacing settings, looks
  like:

  ```python
  class Settings(BaseSettings):
      more_settings: SubModel = SubModel()
  ```

  This only type-checks with mypy (after using the plugin), but not
  pyright/pylance. Additionally, this **actually** evaluates the `SubModel`
  constructor during module parsing!

  These issues seem(?) to be inherent to the strategy of subclassing
  `BaseModel`, and building in its logic into the object construction process

- `dataclass-settings` sidesteps this problem by decoupling the definition of
  the settings from the loading of settings.

  As such, you're more able to define the model, exactly as you would have with
  vanilla pydantic:

  ```python
  class Settings(BaseModel):
      more_settings: SubModel
  ```

  Internally, the `load_settings` function handles the work of constructing the
  requisite input structure pydantic expects to construct the whole object tree.

### Compatibility

- `pydantic-settings`'s `BaseSettings` inherits from pydantic's `BaseModel`. And
  thus can only function against pydantic models, as the name would imply.

- `dataclass-settings`'s primary entrypoint is a function that accepts a
  supportable type. As such, it can theoretically support any type that has a
  well defined object structure, like all of `pydantic`, `dataclasses`, and
  `attrs`.

  Practically, `pydantic` has the most robust system for parsing/validating a
  json-like structure into the models, so it's probably to be the most flexible
  anyways. But for many simple cases, particuarly those without nesting, or that
  only deal in simple types (like int, float, str, etc); then dataclasses/attrs
  can certainly provide a similar experience.

### Flexibility

- At time of writing, `pydantic-settings`'s strategy around "loaders", i.e.
  supportable settings sources is relatively inflexible. Their issue tracker
  contains a decent number of requests for a more flexible way of defining
  settings priorities among different loaders, or even using different settings
  from within a loader.

  This, at least, doesn't seem to be an inherent issue to the library
  necessarily. Just that at present, their API appears to try to reuse
  pydantic's `Field` and `alias` mechanisms to infer the settings for all
  loaders.

- `dataclass-settings` instead annotates each field individually, with the
  loaders that field should use. That means you can have different priorities
  (or entirely different loaders!) per field.
