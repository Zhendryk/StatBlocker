from typing import override
from dataclasses import dataclass, field
from statblocker.data.enums import SpeedType
from statblocker.data.bases import StatblockComponent


@dataclass
class Speed(StatblockComponent):
    values: dict[SpeedType, int] = field(
        default_factory=lambda: {
            SpeedType.WALK: 30,
            SpeedType.CLIMB: 0,
            SpeedType.SWIM: 0,
            SpeedType.FLY: 0,
            SpeedType.FLY_HOVER: 0,
            SpeedType.BURROW: 0,
        }
    )

    def __getstate__(self):
        # Convert enum keys to string names for JSON compatibility
        return {"values": {k.name: v for k, v in self.values.items()}}

    def __setstate__(self, state):
        # Convert keys back to enums during deserialization
        self.values = {SpeedType[k]: v for k, v in state["values"].items()}

    @override
    @property
    def display_str(self) -> str:
        return ", ".join(
            [
                stype.display_str(self.values[stype])
                for stype in SpeedType
                if stype in self.values
            ]
        )

    @override
    @property
    def hb_v3_markdown(self) -> str:
        return f"**Speed** :: {self.display_str}"
