from dataclasses import dataclass, field
from statblocker.data.bases import StatblockComponent
from typing import override
from statblocker.data.enums import Skill, Proficiency


@dataclass
class Skills(StatblockComponent):
    values: dict[Skill, Proficiency] = field(default_factory=dict)

    def __getstate__(self):
        # Convert enum keys to string names for JSON compatibility
        return {"values": {k.name: v.name for k, v in self.values.items()}}

    def __setstate__(self, state):
        # Convert keys back to enums during deserialization
        self.values = {Skill[k]: Proficiency[v] for k, v in state["values"].items()}

    @override
    @property
    def hb_v3_markdown(self) -> str:
        raise RuntimeError(
            "This is a calculated value for Skills, and cannot be called from here"
        )
