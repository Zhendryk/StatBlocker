from dataclasses import dataclass, field
from typing import override
from statblocker.data.bases import StatblockComponent
from statblocker.data.enums import Language, LanguageProficiency


@dataclass
class Languages(StatblockComponent):
    values: dict[Language, LanguageProficiency] = field(default_factory=dict)
    telepathy: tuple[bool, int] = (False, 0)

    def __getstate__(self):
        # Convert enum keys to string names for JSON compatibility
        return {
            "values": {k.name: v.name for k, v in self.values.items()},
            "telepathy": self.telepathy,
        }

    def __setstate__(self, state):
        # Convert keys back to enums during deserialization
        self.values = {
            Language[k]: LanguageProficiency[v] for k, v in state["values"].items()
        }
        self.telepathy = state["telepathy"]

    @property
    def display_str(self) -> str:
        sorted_spoken_languages = sorted(
            [l for l, lp in self.values.items() if lp == LanguageProficiency.SPEAKS],
            key=lambda x: x.name.lower(),
        )
        sorted_spoken_languages_strs = [l.display_name for l in sorted_spoken_languages]
        sorted_understood_languages = sorted(
            [
                l
                for l, lp in self.values.items()
                if lp == LanguageProficiency.UNDERSTANDS
            ],
            key=lambda x: x.name.lower(),
        )
        sorted_understood_languages_strs = [
            f"Understands {l.display_name} but can't speak"
            for l in sorted_understood_languages
        ]
        languages_str = ", ".join(
            [*sorted_spoken_languages_strs, *sorted_understood_languages_strs]
        )
        if self.telepathy[0]:
            return (
                f"{languages_str}; telepathy {self.telepathy[1]} ft."
                if languages_str
                else f"telepathy {self.telepathy[1]} ft."
            )
        return languages_str

    @override
    @property
    def hb_v3_markdown(self) -> str:
        if not self.values:
            return ""
        return f"**Languages** :: {self.display_str}"
