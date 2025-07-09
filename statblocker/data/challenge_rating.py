from __future__ import annotations
from typing import override
from dataclasses import dataclass
from statblocker.data.constants import CR_EXPERIENCE_POINTS, CR_AC


@dataclass
class ChallengeRating:

    rating: int | float
    has_lair: bool = False

    @property
    def proficiency_bonus(self) -> int:
        if self.rating >= 0 and self.rating <= 4:
            return 2
        elif self.rating >= 5 and self.rating <= 8:
            return 3
        elif self.rating >= 9 and self.rating <= 12:
            return 4
        elif self.rating >= 13 and self.rating <= 16:
            return 5
        elif self.rating >= 17 and self.rating <= 20:
            return 6
        elif self.rating >= 21 and self.rating <= 24:
            return 7
        elif self.rating >= 25 and self.rating <= 28:
            return 8
        elif self.rating >= 29 and self.rating <= 30:
            return 9
        raise NotImplementedError

    @property
    def lair_rating(self) -> int | float:
        return self.rating + 1

    @property
    def experience_points(self) -> int:
        return CR_EXPERIENCE_POINTS[self.rating]

    @property
    def lair_xp(self) -> int:
        return CR_EXPERIENCE_POINTS[self.lair_rating]

    @property
    def armor_class(self) -> int:
        return CR_AC[self.rating]

    @property
    def lair_armor_class(self) -> int:
        return CR_AC[self.lair_rating]

    @property
    def display_str(self) -> str:
        if isinstance(self.rating, float):
            numerator, denominator = self.rating.as_integer_ratio()
            if denominator == 1:
                if self.has_lair:
                    return f"{numerator} (XP {self.experience_points:,}, or {self.lair_xp:,} in lair; PB +{self.proficiency_bonus})"
                return f"{numerator} (XP {self.experience_points:,}; PB +{self.proficiency_bonus})"
            if self.has_lair:
                return f"{numerator}/{denominator} (XP {self.experience_points:,}, or {self.lair_xp:,} in lair; PB +{self.proficiency_bonus})"
            return f"{numerator}/{denominator} (XP {self.experience_points:,}; PB +{self.proficiency_bonus})"
        elif self.has_lair:
            return f"{self.rating} (XP {self.experience_points:,}, or {self.lair_xp:,} in lair; PB +{self.proficiency_bonus})"
        return f"{self.rating} (XP {self.experience_points:,}; PB +{self.proficiency_bonus})"

    @override
    @property
    def hb_v3_markdown(self) -> str:
        return f"**CR** :: {self.display_str}"
