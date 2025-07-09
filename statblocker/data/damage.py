from dataclasses import dataclass, field
from statblocker.data.dice import Dice
from statblocker.data.enums import DamageType, Ability
from statblocker.data.ability_scores import AbilityScores


@dataclass
class Damage:
    dice: Dice
    damage_type: DamageType
    proficiency_bonus: int
    bonus: int = field(default=0)
    tie_to_ability_score: bool = field(default=False)
    ability_scores: AbilityScores | None = field(default=None)
    attack_stat: Ability | None = field(default=None)
    conditional: str | None = field(default=None)

    def __post_init__(self) -> None:
        if len(self.dice) > 1:
            raise NotImplementedError
        if self.tie_to_ability_score and (
            self.ability_scores is None or self.attack_stat is None
        ):
            raise ValueError
        self.num_dice = list(self.dice.dice.values())[0]
        self.die_type = list(self.dice.dice.keys())[0]
        if self.conditional:
            self.conditional = self.conditional.replace("if", "").strip().rstrip(".")

    @property
    def total_bonus(self) -> int:
        if self.tie_to_ability_score:
            return (
                self.ability_scores._calculate_modifier(
                    self.ability_scores.scores[self.attack_stat]
                )
                + self.proficiency_bonus
                + self.bonus
            )
        return self.proficiency_bonus + self.bonus

    @property
    def hb_v3_markdown(self) -> str:
        standard_str = f"{self.dice.average_value + self.total_bonus} ({self.num_dice}{self.die_type.name.lower()} + {self.total_bonus}) {self.damage_type.name.capitalize()} damage"
        if self.conditional:
            return f"{standard_str} if {self.conditional}"
        return standard_str
