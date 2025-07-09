from dataclasses import dataclass, field
from statblocker.data.bases import StatblockComponent
from typing import override
from statblocker.data.enums import Sense


@dataclass
class Senses(StatblockComponent):
    values: dict[Sense, int] = field(default_factory=dict)

    def __getstate__(self):
        # Convert enum keys to string names for JSON compatibility
        return {"values": {k.name: v for k, v in self.values.items()}}

    def __setstate__(self, state):
        # Convert keys back to enums during deserialization
        self.values = {Sense[k]: v for k, v in state["values"].items()}

    @property
    def display_str(self) -> str:
        sorted_senses = sorted(self.values.keys(), key=lambda x: x.name.lower())
        strs = [
            f"{s.name.capitalize()} {self.values[s]} ft."
            for s in sorted_senses
            if s in self.values
        ]
        return ", ".join(strs) if strs else ""

    @override
    @property
    def hb_v3_markdown(self) -> str:
        raise RuntimeError(
            "This is a calculated value and should be called from StatBlock."
        )
