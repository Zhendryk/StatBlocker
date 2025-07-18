from __future__ import annotations
import math
import jsonpickle
from dataclasses import dataclass, field
from statblocker.data.dice import Dice
from statblocker.data.enums import (
    Alignment,
    CreatureType,
    Habitat,
    Size,
    Treasure,
    Proficiency,
    Condition,
    DamageType,
    Ability,
)
from statblocker.data.ability_scores import AbilityScores, modifier_display_str
from statblocker.data.challenge_rating import ChallengeRating
from statblocker.data.speed import Speed
from statblocker.data.senses import Senses
from statblocker.data.languages import Languages
from statblocker.data.skills import Skills
from statblocker.data.action import (
    Trait,
    Action,
    BonusAction,
    Reaction,
    LegendaryAction,
)


@dataclass
class StatBlock:
    # Basic Information
    name: str
    epithet: str
    description: str
    # Environmental details (Outside of statblock)
    habitat: list[Habitat]
    treasure: list[Treasure]
    # Creature biology and behavior
    size: list[Size]
    creature_type: CreatureType
    tags: list[str]
    alignment: Alignment
    # Combat highlights
    armor_class: int
    # NOTE: Hit Points are derived from AbilityScores and ChallengeRating
    speed: Speed
    # NOTE: Initiative is derived from AbilityScores
    # Ability scores
    ability_scores: AbilityScores
    # Additional details
    skills: Skills
    vulnerabilities: list[DamageType]
    resistances: list[DamageType]
    immunities: list[Condition | DamageType]
    gear: list[str]
    senses: Senses
    languages: Languages
    challenge_rating: ChallengeRating
    # Combat abilities
    traits: list[Trait]
    actions: list[Action]
    bonus_actions: list[BonusAction]
    reactions: list[Reaction]
    legendary_actions: list[LegendaryAction]
    # Optional data
    is_swarm: bool = field(default=False)
    num_legendary_resistances: int | None = field(default=None)
    legendary_resistances_lair_bonus: int | None = field(default=None)
    num_legendary_actions: int | None = field(default=None)
    legendary_actions_lair_bonus: int | None = field(default=None)

    @property
    def habitat_str(self) -> str:
        if not self.habitat:
            self.habitat = [Habitat.ANY]
        return ", ".join(
            sorted([h.display_name for h in self.habitat], key=lambda x: x.lower())
        )

    @property
    def treasure_str(self) -> str:
        if not self.treasure:
            self.treasure = [Treasure.NONE]
        return ", ".join(
            sorted([t.display_name for t in self.treasure], key=lambda x: x.lower())
        )

    @property
    def habitat_and_treasure_hb_v3_markdown(self) -> str:
        return f"{{{{habitat **Habitat:** {self.habitat_str}; **Treasure:** {self.treasure_str}}}}}"

    @property
    def size_str(self) -> str:
        match len(self.size):
            case 0:
                return ""
            case 1:
                return self.size[0].display_name
            case _:
                ordered_sizes = sorted([s for s in self.size], key=lambda x: x.value)
                ordered_sizes_str = ", ".join([s.display_name for s in ordered_sizes])
                split = ordered_sizes_str.rsplit(", ", 1)
                all_but_last = split[0]
                last = split[1]
                return f"{all_but_last} or {last}"

    @property
    def tags_str(self) -> str:
        if not self.tags:
            return ""
        return f"({', '.join(sorted(self.tags, key=lambda x: x.lower()))})"

    @property
    def alignment_str(self) -> str:
        if not self.alignment:
            return Alignment.UNALIGNED.name.capitalize()
        return self.alignment.display_name

    @property
    def subheader_hb_v3_markdown(self) -> str:
        return f"*{self.size_str} {self.creature_type.display_name}{f' {self.tags_str}' if self.tags_str else ''}, {self.alignment_str}*"

    @property
    def ac_str(self) -> str:
        return str(self.armor_class) if self.armor_class else "—"

    @property
    def hit_points_str(self) -> str:
        if self.size:
            if self.challenge_rating.rating < 1:
                hp = math.ceil(30 * math.sqrt(self.challenge_rating.rating))
            elif (
                self.challenge_rating.rating >= 1 and self.challenge_rating.rating <= 19
            ):
                hp = math.ceil(15 * (self.challenge_rating.rating + 1))
            else:
                hp = math.ceil(45 * (self.challenge_rating.rating - 13))
            max_size = Size(max(sz.value for sz in self.size))
            hit_dice = Dice.closest_to(hp, max_size, self.ability_scores)
            # TODO: Should this return a list of str, one for each size?
            return hit_dice.hit_points(self.ability_scores)
        return ""

    @property
    def initiative(self) -> int:
        return self.ability_scores.dexterity_modifier

    @property
    def initiative_str(self) -> str:
        return f"{modifier_display_str(self.initiative)} ({self.ability_scores.dexterity_score})"

    @property
    def ac_hb_v3_markdown(self) -> str:
        return f"**AC** :: {self.ac_str}"

    @property
    def hit_points_hb_v3_markdown(self) -> str:
        return f"**HP** :: {self.hit_points_str}"

    @property
    def initiative_hb_v3_markdown(self) -> str:
        return f"**Initiative** :: {self.initiative_str}"

    @property
    def skills_hb_v3_markdown(self) -> str:
        if not self.skills.values:
            return ""
        sorted_skills = sorted(self.skills.values.keys(), key=lambda x: x.name.lower())
        skill_strs = []
        for skill in sorted_skills:
            proficiency = self.skills.values[skill]
            bonus = {
                Proficiency.NORMAL: 0,
                Proficiency.PROFICIENT: self.challenge_rating.proficiency_bonus,
                Proficiency.EXPERTISE: self.challenge_rating.proficiency_bonus * 2,
            }.get(proficiency, 0)
            skill_strs.append(
                f"{skill.display_name} {modifier_display_str(self.ability_scores.get_skill_modifier(skill, bonus))}"
            )
        skills_str = ", ".join(skill_strs)
        return f"**Skills** :: {skills_str}"

    @property
    def vulnerabilities_hb_v3_markdown(self) -> str:
        if not self.vulnerabilities:
            return ""
        sorted_strs = ", ".join(
            [
                v.display_name
                for v in sorted(
                    self.vulnerabilities, key=lambda x: x.display_name.lower()
                )
            ]
        )
        return f"**Vulnerabilities** :: {sorted_strs}"

    @property
    def resistances_hb_v3_markdown(self) -> str:
        if not self.resistances:
            return ""
        sorted_strs = ", ".join(
            [
                r.display_name
                for r in sorted(self.resistances, key=lambda x: x.display_name.lower())
            ]
        )
        return f"**Resistances** :: {sorted_strs}"

    @property
    def immunities_hb_v3_markdown(self) -> str:
        if not self.immunities:
            return ""
        sorted_damage_types = sorted(
            [i.display_name for i in self.immunities if isinstance(i, DamageType)],
            key=lambda x: x.lower(),
        )
        sorted_conditions = sorted(
            [i.display_name for i in self.immunities if isinstance(i, Condition)],
            key=lambda x: x.lower(),
        )
        sorted_dmg_str = ", ".join(sorted_damage_types) if sorted_damage_types else ""
        sorted_cond_str = ", ".join(sorted_conditions) if sorted_conditions else ""
        if not sorted_damage_types and not sorted_conditions:
            return ""
        return f"**Immunities** :: {sorted_dmg_str}{'; ' if sorted_dmg_str and sorted_cond_str else ''}{sorted_cond_str}"

    @property
    def gear_hb_v3_markdown(self) -> str:
        return ""  # TODO: Implement me

    @property
    def senses_hb_v3_markdown(self) -> str:
        senses_str = self.senses.display_str
        passive_perception = (
            10
            + self.ability_scores.wisdom_modifier
            + self.challenge_rating.proficiency_bonus
        )
        if senses_str:
            return (
                f"**Senses** :: {senses_str}; Passive Perception {passive_perception}"
            )
        return f"**Senses** :: Passive Perception {passive_perception}"

    @property
    def traits_hb_v3_markdown(self) -> str:
        if not self.traits:
            return ""
        traits_str = "\n\n".join([trait.hb_v3_markdown for trait in self.traits])
        return f"### Traits\n{traits_str}"

    @property
    def actions_hb_v3_markdown(self) -> str:
        if not self.actions:
            return ""
        actions_str = "\n\n".join([action.hb_v3_markdown for action in self.actions])
        return f"### Actions\n{actions_str}"

    @property
    def bonus_actions_hb_v3_markdown(self) -> str:
        if not self.bonus_actions:
            return ""
        bonus_actions_str = "\n\n".join(
            [ba.hb_v3_markdown for ba in self.bonus_actions]
        )
        return f"### Bonus Actions\n{bonus_actions_str}"

    @property
    def reactions_hb_v3_markdown(self) -> str:
        if not self.reactions:
            return ""
        reactions_str = "\n\n".join(
            [reaction.hb_v3_markdown for reaction in self.reactions]
        )
        return f"### Reactions\n{reactions_str}"

    @property
    def legendary_actions_hb_v3_markdown(self) -> str:
        if (
            not self.legendary_actions
            or self.num_legendary_actions is None
            or self.legendary_actions_lair_bonus is None
        ):
            return ""
        la_uses_txt = f"{self.num_legendary_actions}" + (
            f" ({self.num_legendary_actions + self.legendary_actions_lair_bonus} in Lair)"
            if self.legendary_actions_lair_bonus is not None
            else ""
        )
        short_monster_name = self.name.split(" ")[-1]
        flavor_text = f"_Legendary Action Uses: {la_uses_txt}. Immediately after another creature's turn, the {short_monster_name} can expend a use to take one of the following actions. The {short_monster_name} regains all expended uses at the start of each of its turns._\n{{color:gray}}\n"
        legendary_actions_str = "\n\n".join(
            [la.hb_v3_markdown for la in self.legendary_actions]
        )
        return f"### Legendary Actions\n{flavor_text}{legendary_actions_str}"

    def to_json(self) -> str:
        return jsonpickle.encode(self, indent=2, unpicklable=True)

    @classmethod
    def from_json(cls, json_str: str) -> StatBlock:
        return jsonpickle.decode(json_str)

    def hb_v3_markdown(self, wide: bool = False) -> str:
        markdown_str = (
            f"## {self.name}\n"
            f"*{self.epithet}*\n"
            f"{self.habitat_and_treasure_hb_v3_markdown if self.habitat_and_treasure_hb_v3_markdown else ''}\n"
        )
        markdown_str += (
            f"{self.description if self.description else '<DESCRIPTION HERE>'}\n\n"
        )
        markdown_str += (
            f"{{{{monster,frame{",wide" if wide else ""}\n"
            f"## {self.name}\n"
            f"{self.subheader_hb_v3_markdown}\n"
            "\n"
            f"{self.ac_hb_v3_markdown}\n"
            f"{self.hit_points_hb_v3_markdown}\n"
            f"{self.speed.hb_v3_markdown}\n"
            "\n"
            f"{self.initiative_hb_v3_markdown}\n"
            "\n"
            f"{self.ability_scores.hb_v3_markdown}\n"
            "\n"
        )
        if self.skills_hb_v3_markdown:
            markdown_str += f"{self.skills_hb_v3_markdown}\n"
        if self.vulnerabilities_hb_v3_markdown:
            markdown_str += f"{self.vulnerabilities_hb_v3_markdown}\n"
        if self.resistances_hb_v3_markdown:
            markdown_str += f"{self.resistances_hb_v3_markdown}\n"
        if self.immunities_hb_v3_markdown:
            markdown_str += f"{self.immunities_hb_v3_markdown}\n"
        if self.gear_hb_v3_markdown:
            markdown_str += f"{self.gear_hb_v3_markdown}\n"
        if self.senses_hb_v3_markdown:
            markdown_str += f"{self.senses_hb_v3_markdown}\n"
        if self.languages.hb_v3_markdown:
            markdown_str += f"{self.languages.hb_v3_markdown}\n"
        if self.challenge_rating.hb_v3_markdown:
            markdown_str += f"{self.challenge_rating.hb_v3_markdown}\n"
        markdown_str += "\n"
        if self.traits_hb_v3_markdown:
            markdown_str += f"{self.traits_hb_v3_markdown}\n"
        if self.actions_hb_v3_markdown:
            markdown_str += f"{self.actions_hb_v3_markdown}\n"
        if self.bonus_actions_hb_v3_markdown:
            markdown_str += f"{self.bonus_actions_hb_v3_markdown}\n"
        if self.reactions_hb_v3_markdown:
            markdown_str += f"{self.reactions_hb_v3_markdown}\n"
        if self.legendary_actions_hb_v3_markdown:
            markdown_str += f"{self.legendary_actions_hb_v3_markdown}\n"
        markdown_str += "}}\n"
        return markdown_str
