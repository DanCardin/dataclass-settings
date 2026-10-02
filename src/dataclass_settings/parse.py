from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class Parse:
    """Map a raw loaded value before it reaches the class constructor.

    Annotate a field with one or more `Parse` objects (like `annotated-types`
    markers). Each is applied, in order, to the value produced by the loaders.

    Example:
        >>> from typing import Annotated
        >>> flag = Parse(lambda v: v.lower() in {"1", "true", "yes"})
        >>> Flag = Annotated[bool, flag]
    """

    func: Callable[[Any], Any]

    def __call__(self, value: Any) -> Any:
        return self.func(value)
