from __future__ import annotations
from dataclasses import dataclass
from statblocker.data.enums import Die, RollType, Size
from statblocker.data.ability_scores import AbilityScores


@dataclass
class Dice:
    dice: dict[Die, int]

    @property
    def value(self) -> int:
        return sum([dt.roll(self.dice[dt]) for dt in self.dice])

    @property
    def average_value(self) -> int:
        return sum(
            [dt.roll(self.dice[dt], roll_type=RollType.AVERAGE) for dt in self.dice]
        )

    @property
    def max_value(self) -> int:
        return sum([dt.roll(self.dice[dt], roll_type=RollType.MAX) for dt in self.dice])

    @property
    def min_value(self) -> int:
        return sum([dt.roll(self.dice[dt], roll_type=RollType.MIN) for dt in self.dice])

    @property
    def range(self) -> range:
        return range(
            start=self.min_value, stop=self.max_value + 1
        )  # +1 because it is not inclusive of the upper bound

    def hit_points(self, ability_scores: AbilityScores) -> str:
        if len(self.dice) > 1:
            raise NotImplementedError
        die, cnt = self.dice.popitem()
        self.dice[die] = cnt
        total_hp = self.average_value + ability_scores.constitution_modifier * cnt
        bonus = ability_scores.constitution_modifier * cnt
        if bonus > 0:
            bonus_str = f" + {bonus}"
        elif bonus < 0:
            bonus_str = f" - {abs(bonus)}"
        else:
            bonus_str = ""
        return f"{total_hp} ({cnt}{die.name.lower()}{bonus_str})"

    @property
    def num_hit_dice(self) -> int:
        return sum(cnt for cnt in self.dice.values())

    @staticmethod
    def closest_to(
        hp: int, monster_size: Size, ability_scores: AbilityScores, max_range: int = 51
    ) -> Dice:
        distances = {
            i: abs(
                hp
                - (
                    Dice({monster_size.hit_die: i}).average_value
                    + (ability_scores.constitution_modifier * i)
                )
            )
            for i in range(max_range)
        }
        closest = min(distances, key=lambda k: distances[k])
        return Dice({monster_size.hit_die: closest})

    @staticmethod
    def calculate_avg_roll(
        num_dice: int, die_type: Die, sign: str, bonus: int = 0
    ) -> int:
        dice = Dice({die_type: num_dice})
        roll_bonus = bonus
        if bonus != 0:
            match sign:
                case "+":
                    roll_bonus = abs(bonus)
                case "-":
                    roll_bonus = -abs(bonus)
                case _:
                    raise NotImplementedError
        return dice.average_value + roll_bonus
