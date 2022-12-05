from __future__ import annotations
import dataclasses
from typing import Self

import esper

@dataclasses.dataclass
class Component(object):
    """
    Base class for all components.
    """

    pass

    @classmethod
    def merge(cls, old: Self, new: Self) -> Self:
        args = []
        for field in dataclasses.fields(old):
            if hasattr(new, field.name):
                args.append(getattr(new, field.name))
            else:
                args.append(getattr(old, field.name))
        return cls(*args)