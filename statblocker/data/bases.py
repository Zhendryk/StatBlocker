from __future__ import annotations
from enum import Enum
from typing import Protocol


class StatblockComponent(Protocol):

    @property
    def hb_v3_markdown(self) -> str: ...


class StatblockEnum(Enum):

    @property
    def display_name(self) -> str:
        return " ".join([token.capitalize() for token in self.name.split("_")])

    @classmethod
    def from_name(cls, name: str) -> StatblockEnum:
        for e in cls:
            if name.lower() == e.name.lower():
                return e
        raise ValueError(f"Invalid {cls.__name__}: {name}")

    @classmethod
    def from_display_name(cls, name: str) -> StatblockEnum:
        for e in cls:
            if e.name.lower() == "_".join([c for c in name.split(" ")]).lower():
                return e
        raise ValueError(f"Invalid {cls.__name__}: {name}")

    @classmethod
    def from_partial_name(cls, name: str) -> StatblockEnum:
        for e in cls:
            if (
                "_".join([c for c in name.split(" ")])
                .lower()
                .startswith(e.name.lower())
            ):
                return e
        raise ValueError(f"Invalid partial {cls.__name__}: {name}")

    @classmethod
    def is_valid_display_name(cls, name: str) -> bool:
        return "_".join([c for c in name.split(" ")]).lower() in [
            e.name.lower() for e in cls
        ]
