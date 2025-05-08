# Dataclasses/Pydantic/Attrs

All of the documentation uses `dataclasses` specifically, because it is built
into the standard library since python 3.7.

With that said, any dataclass-like class description pattern should be able to
be supported with relatively little effort. Today `dataclass-settings` ships
with adapters for
[dataclasses](https://docs.python.org/3/library/dataclasses.html),
[Pydantic](https://pydantic-docs.helpmanual.io/), and
[attrs](https://www.attrs.org).
[msgspec models](https://jcristharif.com/msgspec/).

## Pydantic

Pydantic models will generally be the most well supported and most flexible
option. This stems from the fact that they infer the type parsing of input
values from the annotated types on the fields.

This also applies to pydantic's `dataclasses` module.

```{note}
At this time, it **seems** as though pydantic 1.x does not retain the original
Annotated type information, which is required to support this API.
```

## Attrs

Attrs will likely work next-best, because it has an optional `converters`, which
does construction-time casting of the input arguments. While not as
automatic/integrated as pydantic, it can work just as well.

## Dataclasses

Dataclasses primarily suffer from lack of a native API for casting input values.
As such, this library performs **very** basic mapping of annotated types, where
the output type can be constructed from a raw input string.

For example, `int`, `float`, `Decimal`, `bool`, `str`, etc. For anything more
complex, dataclasses will probably not be the most productive choice (at least
until/if [PEP-712](https://peps.python.org/pep-0712/) is accepted/merged)

## Msgspec
Msgspec models are supported as of v0.4.0.

