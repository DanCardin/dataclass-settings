# Annotations

`dataclass-settings` loaders evaluated in the order they're found on the
annotation of each field in a supported dataclass-like class.

## No Annotation

A field without an annotation is ignored. Such fields must have a class-level
default, or otherwise not be required in the class constructor.

```python
from pydantic import BaseModel

class Example(BaseModel):
    foo: str = "foo"
```

## `Annotated` field

A field annotated with `typing.Annotated` or `typing_extensions.Annotated` will
be searched for compatible [Loader](dataclass_settings.loaders.Loader) objects.

Each identified loader will be evaluated in the order they're defined for that
field. The first non-`None` value returned by a loader will end the chain and
that value will be used.

If no loader returns a non-`None` value, that field will not be sent to the
class's constructor.

As such, every field that should be allowed to be omitted should have a
class-level default, or otherwise not be required in the class constructor.

```python
from typing import Annotated
from pydantic import BaseModel
from dataclass_settings import Env, Secret

class Example(BaseModel):
    foo: Annotated[str, Env('FOO'), Secret('foo')] = "foo"
```

```{note}
You can use as many `Loader`s as you'd like, even repeating the same loader
more than once!
```

## Nested Classes

A field with a type annotation of a class that is a
[supported kind of class](./class_compatibility.md) will be recursed into, and
evaluated similarly to the root class.

```python
from __future__ import annotations
from typing import Annotated
from pydantic import BaseModel
from dataclass_settings import Env, Secret

class Example(BaseModel):
    sub_example: SubExample


class SubExample(BaseModel):
    foo: Annotated[str, Env('FOO')] = "foo"
```

````{note}
"Optional class fields" are specifically handled to avoid requiring fields where
they're clearly not intended to be required.

For example:

```python
class Example(BaseModel):
    sub_example: SubExample | None = None
```

In this case, if `SubExample` **cannot** be loaded, then it will be omitted,
and resolved as `None` due to the class-level `None` default.
````
