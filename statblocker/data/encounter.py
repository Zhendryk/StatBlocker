from __future__ import annotations
import math
from enum import auto
from collections.abc import Sequence
from functools import cached_property
from dataclasses import dataclass, field
from monster_forge.dnd.enums import DNDEnum
from monster_forge.dnd.constants import CR_EXPERIENCE_POINTS


class EncounterSize(DNDEnum):
    SINGLETON = auto()
    SMALL = auto()
    MEDIUM = auto()
    LARGE = auto()
    SWARM = auto()

    @property
    def num_creatures(self) -> int:
        match self:
            case EncounterSize.SINGLETON:
                return 1
            case EncounterSize.SMALL:
                # return randint(2, 4)
                return 3
            case EncounterSize.MEDIUM:
                # return randint(5, 8)
                return 6
            case EncounterSize.LARGE:
                # return randint(9, 12)
                return 10
            case EncounterSize.SWARM:
                # return randint(13, 20)
                return 15
            case _:
                raise NotImplementedError


class EncounterDifficulty(DNDEnum):
    LOW = auto()
    MODERATE = auto()
    HIGH = auto()

    def experience_points_budget(
        self, avg_party_level: int, num_players: int = 1
    ) -> int:
        xp_budget_per_player = ENCOUNTER_DIFFICULTY_XP_BUDGET[self].get(
            avg_party_level, 0
        )
        total_xp_budget_for_encounter = xp_budget_per_player * num_players
        return total_xp_budget_for_encounter


ENCOUNTER_DIFFICULTY_XP_BUDGET: dict[EncounterDifficulty, dict[int, int]] = {
    EncounterDifficulty.LOW: {
        1: 50,
        2: 100,
        3: 150,
        4: 250,
        5: 500,
        6: 600,
        7: 750,
        8: 1000,
        9: 1300,
        10: 1600,
        11: 1900,
        12: 2200,
        13: 2600,
        14: 2900,
        15: 3300,
        16: 3800,
        17: 4500,
        18: 5000,
        19: 5500,
        20: 6400,
    },
    EncounterDifficulty.MODERATE: {
        1: 75,
        2: 150,
        3: 225,
        4: 375,
        5: 750,
        6: 1000,
        7: 1300,
        8: 1700,
        9: 2000,
        10: 2300,
        11: 2900,
        12: 3700,
        13: 4200,
        14: 4900,
        15: 5400,
        16: 6100,
        17: 7200,
        18: 8700,
        19: 10700,
        20: 13200,
    },
    EncounterDifficulty.HIGH: {
        1: 100,
        2: 200,
        3: 400,
        4: 500,
        5: 1100,
        6: 1400,
        7: 1700,
        8: 2100,
        9: 2600,
        10: 3100,
        11: 4100,
        12: 4700,
        13: 5400,
        14: 6200,
        15: 7800,
        16: 9800,
        17: 11700,
        18: 14200,
        19: 17200,
        20: 22000,
    },
}


@dataclass
class Encounter:
    size: EncounterSize | None = field(default=None)
    difficulty: EncounterDifficulty | None = field(default=None)
    num_pcs: int | None = field(default=None)
    avg_party_level: int | None = field(default=None)
    player_levels: Sequence[int] = field(default_factory=list)

    def __post_init__(self) -> None:
        pass
        # if not self.player_levels:
        #     assert self.num_pcs is not None
        #     assert self.avg_party_level is not None
        # else:
        #     assert self.player_levels is not None

    @cached_property
    def calced_avg_party_level(self) -> int:
        if self.player_levels:
            return math.floor(sum(self.player_levels) / self.num_players)
        return self.avg_party_level

    @cached_property
    def calced_num_players(self) -> int:
        if self.player_levels:
            return len(self.player_levels)
        return self.num_pcs

    @cached_property
    def num_monsters(self) -> int:
        return self.size.num_creatures

    @cached_property
    def monster_cr(self) -> int | float:
        total_xp_budget = self.difficulty.experience_points_budget(
            self.calced_avg_party_level, num_players=self.calced_num_players
        )
        xp_per_monster = total_xp_budget / self.num_monsters
        distances = [
            (cr, abs(xp_per_monster - cr_table_xp_value))
            for cr, cr_table_xp_value in CR_EXPERIENCE_POINTS.items()
        ]
        min_dist = min(distances, key=lambda x: x[1])
        monster_cr = next((cr for cr, dist in distances if dist == min_dist[1]), None)
        if monster_cr is None:
            raise RuntimeError
        return monster_cr
