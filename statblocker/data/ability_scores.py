import math
from dataclasses import dataclass
from typing import override
from statblocker.data.enums import Ability, Proficiency, Skill
from statblocker.data.bases import StatblockComponent

STAT_STR_TO_ABILITY: dict[str, Ability] = {
    "STR": Ability.STRENGTH,
    "DEX": Ability.DEXTERITY,
    "CON": Ability.CONSTITUTION,
    "INT": Ability.INTELLIGENCE,
    "WIS": Ability.WISDOM,
    "CHA": Ability.CHARISMA,
}


def calculate_ability_modifier(score: int) -> int:
    """Calculates the ability score modifier."""
    return math.floor(float((score - 10) / 2))


def modifier_display_str(modifier: int) -> str:
    """Returns a string representation of the modifier."""
    if modifier >= 0:
        return f"+{modifier}"
    return str(modifier)  # Negative modifiers are already formatted correctly


@dataclass
class AbilityScores(StatblockComponent):
    proficiency_bonus: int
    scores: dict[Ability, int]
    proficiency_levels: dict[Ability, Proficiency]

    def __getstate__(self):
        # Convert enum keys to string names for JSON compatibility
        return {
            "proficiency_bonus": self.proficiency_bonus,
            "scores": {k.name: v for k, v in self.scores.items()},
            "proficiency_levels": {
                k.name: v.name for k, v in self.proficiency_levels.items()
            },
        }

    def __setstate__(self, state):
        # Convert keys back to enums during deserialization
        self.proficiency_bonus = state["proficiency_bonus"]
        self.scores = {Ability[k]: v for k, v in state["scores"].items()}
        self.proficiency_levels = {
            Ability[k]: Proficiency[v] for k, v in state["proficiency_levels"].items()
        }

    def _calculate_save(self, ability: Ability) -> int:
        modifier = calculate_ability_modifier(self.scores.get(ability, 10))
        prof_bonus = {
            Proficiency.NORMAL: 0,
            Proficiency.PROFICIENT: self.proficiency_bonus,
            Proficiency.EXPERTISE: self.proficiency_bonus * 2,
        }.get(self.proficiency_levels.get(ability, Proficiency.NORMAL), 0)
        return modifier + prof_bonus

    def get_skill_modifier(self, skill: Skill, bonus: int = 0) -> int:
        return (
            calculate_ability_modifier(self.scores.get(skill.associated_ability, 10))
            + bonus
        )

    @property
    def strength_score(self) -> int:
        return self.scores.get(Ability.STRENGTH, 10)

    @property
    def strength_modifier(self) -> int:
        return calculate_ability_modifier(self.strength_score)

    @property
    def strength_save(self) -> int:
        return self._calculate_save(Ability.STRENGTH)

    @property
    def is_str_proficient(self) -> bool:
        return (
            self.proficiency_levels.get(Ability.STRENGTH, Proficiency.NORMAL)
            == Proficiency.PROFICIENT
        )

    @property
    def dexterity_score(self) -> int:
        return self.scores.get(Ability.DEXTERITY, 10)

    @property
    def dexterity_modifier(self) -> int:
        return calculate_ability_modifier(self.dexterity_score)

    @property
    def dexterity_save(self) -> int:
        return self._calculate_save(Ability.DEXTERITY)

    @property
    def is_dex_proficient(self) -> bool:
        return (
            self.proficiency_levels.get(Ability.DEXTERITY, Proficiency.NORMAL)
            == Proficiency.PROFICIENT
        )

    @property
    def constitution_score(self) -> int:
        return self.scores.get(Ability.CONSTITUTION, 10)

    @property
    def constitution_modifier(self) -> int:
        return calculate_ability_modifier(self.constitution_score)

    @property
    def constitution_save(self) -> int:
        return self._calculate_save(Ability.CONSTITUTION)

    @property
    def is_con_proficient(self) -> bool:
        return (
            self.proficiency_levels.get(Ability.CONSTITUTION, Proficiency.NORMAL)
            == Proficiency.PROFICIENT
        )

    @property
    def intelligence_score(self) -> int:
        return self.scores.get(Ability.INTELLIGENCE, 10)

    @property
    def intelligence_modifier(self) -> int:
        return calculate_ability_modifier(self.intelligence_score)

    @property
    def intelligence_save(self) -> int:
        return self._calculate_save(Ability.INTELLIGENCE)

    @property
    def is_int_proficient(self) -> bool:
        return (
            self.proficiency_levels.get(Ability.INTELLIGENCE, Proficiency.NORMAL)
            == Proficiency.PROFICIENT
        )

    @property
    def wisdom_score(self) -> int:
        return self.scores.get(Ability.WISDOM, 10)

    @property
    def wisdom_modifier(self) -> int:
        return calculate_ability_modifier(self.wisdom_score)

    @property
    def wisdom_save(self) -> int:
        return self._calculate_save(Ability.WISDOM)

    @property
    def is_wis_proficient(self) -> bool:
        return (
            self.proficiency_levels.get(Ability.WISDOM, Proficiency.NORMAL)
            == Proficiency.PROFICIENT
        )

    @property
    def charisma_score(self) -> int:
        return self.scores.get(Ability.CHARISMA, 10)

    @property
    def charisma_modifier(self) -> int:
        return calculate_ability_modifier(self.charisma_score)

    @property
    def charisma_save(self) -> int:
        return self._calculate_save(Ability.CHARISMA)

    @property
    def is_cha_proficient(self) -> bool:
        return (
            self.proficiency_levels.get(Ability.CHARISMA, Proficiency.NORMAL)
            == Proficiency.PROFICIENT
        )

    @property
    def saving_throws(self) -> dict[Ability, Proficiency]:
        return {
            ability: self.proficiency_levels.get(ability, Proficiency.NORMAL)
            for ability in Ability
        }

    @property
    def display_str(self) -> str:
        return ", ".join(
            [
                f"{ability.display_name}:{score}"
                for ability, score in self.scores.items()
            ]
        )

    @property
    def hb_v3_markdown(self) -> str:
        return (
            "|   |   | MOD | SAVE |   |   | MOD | SAVE |   |   | MOD | SAVE |\n"
            "|:--|:-:|:---:|:----:|:--|:-:|:---:|:----:|:--|:-:|:---:|:----:|\n"
            f"| STR | {self.strength_score} | {modifier_display_str(self.strength_modifier)} | {modifier_display_str(self.strength_save)} | DEX | {self.dexterity_score} | {modifier_display_str(self.dexterity_modifier)} | {modifier_display_str(self.dexterity_save)} | CON | {self.constitution_score} | {modifier_display_str(self.constitution_modifier)} | {modifier_display_str(self.constitution_save)} |\n"
            f"| INT | {self.intelligence_score} | {modifier_display_str(self.intelligence_modifier)} | {modifier_display_str(self.intelligence_save)} | WIS | {self.wisdom_score} | {modifier_display_str(self.wisdom_modifier)} | {modifier_display_str(self.wisdom_save)} | CHA | {self.charisma_score} | {modifier_display_str(self.charisma_modifier)} | {modifier_display_str(self.charisma_save)} |\n"
        )

    def calculate_stat_operation(
        self,
        stat: str,
        operation: str,
        sign: str | None = None,
        bonus: int | None = None,
    ) -> int:
        ability = STAT_STR_TO_ABILITY[stat]
        ability_mod = calculate_ability_modifier(self.scores.get(ability, 10))
        calced_bonus = 0
        if sign and bonus is not None:
            match sign:
                case "+":
                    calced_bonus = abs(bonus)
                case "-":
                    calced_bonus = -abs(bonus)
                case _:
                    raise NotImplementedError
        match operation:
            case "ATK":
                return self.proficiency_bonus + ability_mod + calced_bonus
            case "SAVE":
                return self._calculate_save(ability) + calced_bonus
            case "SPELLSAVE":
                return 8 + self.proficiency_bonus + ability_mod
            case _:
                pass
