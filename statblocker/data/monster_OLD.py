from __future__ import annotations
from dataclasses import dataclass, field
from monster_forge.dnd.dice import Dice
from monster_forge.dnd.ability_scores import AbilityScores
from monster_forge.dnd.challenge_rating import ChallengeRating
from monster_forge.dnd.enums import (
    Ability,
    Alignment,
    Condition,
    CreatureType,
    DamageType,
    Language,
    Proficiency,
    Resistance,
    Sense,
    Size,
    Skill,
    SpeedType,
)
from monster_forge.dnd.action import Action, Trait


@dataclass
class Monster:
    name: str | None = field(default=None)
    description: str | None = field(default=None)
    habitat: str | None = field(default=None)
    treasure: str | None = field(default=None)
    artwork_url: str | None = field(default=None)
    creature_type: CreatureType | None = field(default=None)
    alignment: Alignment | None = field(default=None)
    tags: list[str] = field(default_factory=list)
    hit_dice: Dice | None = field(default=None)
    size: Size | None = field(default=None)
    speed: dict[SpeedType, int] = field(
        default_factory=lambda: {
            SpeedType.WALKING: 30,
            SpeedType.SWIM: 0,
            SpeedType.FLY: 0,
            SpeedType.CLIMB: 0,
            SpeedType.BURROW: 0,
        }
    )
    ability_scores: AbilityScores = field(
        default_factory=lambda: AbilityScores({ability: 10 for ability in Ability})
    )
    skills: dict[Skill, Proficiency] = field(default_factory=dict)
    damage_resistances: dict[DamageType, Resistance] = field(default_factory=dict)
    saving_throws: dict[Ability, Proficiency] = field(
        default_factory=lambda: {ability: Proficiency.NORMAL for ability in Ability}
    )
    condition_resistances: dict[Condition, Resistance] = field(default_factory=dict)
    senses: dict[Sense, int] = field(default_factory=dict)
    languages: list[Language] = field(default_factory=list)
    telepathy: tuple[bool, int] | None = field(default=None)
    challenge_rating: ChallengeRating | None = field(default=None)
    traits: dict[str, Trait] = field(default_factory=dict)
    actions: dict[str, Action] = field(default_factory=dict)
    bonus_actions: dict[str, Action] = field(default_factory=dict)
    reactions: dict[str, Action] = field(default_factory=dict)
    legendary_actions: dict[str, Action] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.ac_tied_to_cr = True
        self.hp_tied_to_cr = True

    def _stat_display(self, stat: int | None) -> str:
        if stat is None:
            return ""
        return f"+{stat}" if stat >= 0 else str(stat)

    @property
    def in_lair(self) -> bool | None:
        if self.has_required_fields(["challenge_rating"]):
            return self.challenge_rating.in_lair
        return None

    @in_lair.setter
    def in_lair(self, value: bool) -> None:
        if self.has_required_fields(["challenge_rating"]):
            self.challenge_rating.in_lair = value

    @property
    def strength(self) -> int | None:
        if self.has_required_fields(["ability_scores"]):
            return self.ability_scores.scores[Ability.STRENGTH]
        return None

    @property
    def strength_mod(self) -> int | None:
        if self.has_required_fields(["ability_scores"]):
            return self.ability_scores.strength_modifier

    @property
    def strength_save(self) -> int | None:
        if self.ability_scores is None:
            return None
        if self._is_proficient_in_saving_throw(Ability.STRENGTH):
            return self.strength_mod + self.proficiency_bonus
        return self.strength_mod

    @property
    def dex(self) -> int | None:
        if self.ability_scores is None:
            return None
        return self.ability_scores.scores[Ability.DEXTERITY]

    @property
    def dex_mod(self) -> int | None:
        if self.ability_scores is None:
            return None
        return self.ability_scores.dexterity_modifier

    @property
    def dex_save(self) -> int | None:
        if self.ability_scores is None:
            return None
        if self._is_proficient_in_saving_throw(Ability.DEXTERITY):
            return self.dex_mod + self.proficiency_bonus
        return self.dex_mod

    @property
    def con(self) -> int | None:
        if self.ability_scores is None:
            return None
        return self.ability_scores.scores[Ability.CONSTITUTION]

    @property
    def con_mod(self) -> int | None:
        if self.ability_scores is None:
            return None
        return self.ability_scores.constitution_modifier

    @property
    def con_save(self) -> int | None:
        if self.ability_scores is None:
            return None
        if self._is_proficient_in_saving_throw(Ability.CONSTITUTION):
            return self.con_mod + self.proficiency_bonus
        return self.con_mod

    @property
    def intelligence(self) -> int | None:
        if self.ability_scores is None:
            return None
        return self.ability_scores.scores[Ability.INTELLIGENCE]

    @property
    def intelligence_mod(self) -> int | None:
        if self.ability_scores is None:
            return None
        return self.ability_scores.intelligence_modifier

    @property
    def intelligence_save(self) -> int | None:
        if self.ability_scores is None:
            return None
        if self._is_proficient_in_saving_throw(Ability.INTELLIGENCE):
            return self.intelligence_mod + self.proficiency_bonus
        return self.intelligence_mod

    @property
    def wis(self) -> int | None:
        if self.ability_scores is None:
            return None
        return self.ability_scores.scores[Ability.WISDOM]

    @property
    def wis_mod(self) -> int | None:
        if self.ability_scores is None:
            return None
        return self.ability_scores.wisdom_modifier

    @property
    def wis_save(self) -> int | None:
        if self.ability_scores is None:
            return None
        if self._is_proficient_in_saving_throw(Ability.WISDOM):
            return self.wis_mod + self.proficiency_bonus
        return self.wis_mod

    @property
    def cha(self) -> int | None:
        if self.ability_scores is None:
            return None
        return self.ability_scores.scores[Ability.CHARISMA]

    @property
    def cha_mod(self) -> int | None:
        if self.ability_scores is None:
            return None
        return self.ability_scores.charisma_modifier

    @property
    def cha_save(self) -> int | None:
        if self.ability_scores is None:
            return None
        if self._is_proficient_in_saving_throw(Ability.CHARISMA):
            return self.cha_mod + self.proficiency_bonus
        return self.cha_mod

    @property
    def proficiency_bonus(self) -> int | None:
        if self.challenge_rating is None:
            return None
        return self.challenge_rating.proficiency_bonus

    @property
    def passive_perception(self) -> int | None:
        if self._is_proficient_in_skill(Skill.PERCEPTION):
            return (
                10 + self.ability_scores.wisdom_modifier + self.proficiency_bonus
                if self.proficiency_bonus
                else None
            )
        return 10 + self.ability_scores.wisdom_modifier

    @property
    def initiative(self) -> str:
        return (
            f"+{self.dex_mod} ({self.dex})"
            if self.dex >= 10
            else f"-{self.dex_mod} ({self.dex})"
        )

    @property
    def ac_tied_to_cr(self) -> bool:
        return getattr(self, "_ac_tied_to_cr")

    @ac_tied_to_cr.setter
    def ac_tied_to_cr(self, value: bool) -> None:
        setattr(self, "_ac_tied_to_cr", value)

    @property
    def hp_tied_to_cr(self) -> bool:
        return getattr(self, "_hp_tied_to_cr")

    @hp_tied_to_cr.setter
    def hp_tied_to_cr(self, value: bool) -> None:
        setattr(self, "_hp_tied_to_cr", value)

    @property
    def ac(self) -> int | None:
        if self.ac_tied_to_cr:
            if not self.has_required_fields(["challenge_rating"]):
                return None
            return self.challenge_rating.armor_class
        return getattr(self, "_ac")

    @ac.setter
    def ac(self, value: int) -> None:
        if self.ac_tied_to_cr:
            return
        setattr(self, "_ac", value)

    @property
    def hp(self) -> str | None:
        if self.hp_tied_to_cr:
            if not self.has_required_fields(
                ["challenge_rating", "ability_scores", "size"]
            ):
                return None
            return self.challenge_rating.hit_points(self.ability_scores, self.size)
        return getattr(self, "_hp")

    @hp.setter
    def hp(self, value: str) -> None:
        if self.hp_tied_to_cr:
            return
        setattr(self, "_hp", value)

    def _is_proficient_in_skill(self, skill: Skill) -> bool:
        return (skill, Proficiency.PROFICIENT) in self.skills

    def _has_expertise_in_skill(self, skill: Skill) -> bool:
        return (skill, Proficiency.EXPERTISE) in self.skills

    def _is_proficient_in_saving_throw(self, ability: Ability) -> bool:
        saving_throw_proficiency = self.saving_throws.get(ability, None)
        if saving_throw_proficiency is None:
            return False
        return saving_throw_proficiency == Proficiency.PROFICIENT

    def _has_expertise_in_saving_throw(self, ability: Ability) -> bool:
        saving_throw_expertise = self.saving_throws.get(ability, None)
        if saving_throw_expertise is None:
            return False
        return saving_throw_expertise == Proficiency.EXPERTISE

    @property
    def speed_display(self) -> str:
        retval = ""
        walk_speed = f"{self.speed[SpeedType.WALKING]} ft."
        additional_speeds = []
        alphabetical_types = sorted(
            [s for s in SpeedType if s != SpeedType.WALKING],
            key=lambda x: x.name.lower(),
        )
        for speed_type in alphabetical_types:
            if self.speed.get(speed_type, 0) != 0:
                additional_speeds.append(
                    f"{speed_type.name.capitalize()} {self.speed.get(speed_type, 0)} ft."
                )
        if additional_speeds:
            additional_speeds.insert(0, walk_speed)
            retval = ", ".join(additional_speeds)
        else:
            retval = walk_speed
        return retval

    @property
    def skills_display(self) -> str:
        if not self.has_required_fields(["ability_scores", "challenge_rating"]):
            return ""
        retval = []
        ab_sc = self.ability_scores
        for skill, proficiency in sorted(
            self.skills.items(), key=lambda x: x[0].display_name
        ):
            skill_mod = ab_sc._calculate_modifier(
                ab_sc.scores[skill.associated_ability]
            )
            pb = self.challenge_rating.proficiency_bonus
            match proficiency:
                case Proficiency.NORMAL:
                    total_bonus = skill_mod
                case Proficiency.PROFICIENT:
                    total_bonus = skill_mod + pb
                case Proficiency.EXPERTISE:
                    total_bonus = skill_mod + (2 * pb)
                case _:
                    raise NotImplementedError
            retval.append(f"{skill.display_name} +{total_bonus}")
        skills = ", ".join(retval)
        return f"**Skills** :: {skills}\n" if skills else ""

    @property
    def resistances_display(self) -> str:
        dmg_resistances = sorted(
            [
                dt.display_name
                for dt, res in self.damage_resistances.items()
                if res == Resistance.RESISTANT
            ],
            key=lambda x: x.lower(),
        )
        return (
            f"**Resistances** :: {', '.join(dmg_resistances)}\n"
            if dmg_resistances
            else ""
        )

    @property
    def senses_display(self) -> str:
        alphabetical_senses = sorted(
            [
                f"{sense.display_name} {range} ft."
                for sense, range in self.senses.items()
                if range
            ],
            key=lambda x: x.lower(),
        )
        senses = (
            ", ".join(alphabetical_senses)
            + "; "
            + f"Passive Perception {self.passive_perception}"
        )
        return f"**Senses** :: {senses}\n"

    @property
    def immunities_display(self) -> str:
        dmg_immunities = sorted(
            [
                dt.display_name
                for dt, res in self.damage_resistances.items()
                if res == Resistance.IMMUNE
            ],
            key=lambda x: x.lower(),
        )
        condition_immunities = sorted(
            [
                condition.display_name
                for condition, resistance in self.condition_resistances.items()
                if resistance == Resistance.IMMUNE
            ],
            key=lambda x: x.lower(),
        )
        if dmg_immunities and condition_immunities:
            immunities = (
                ", ".join(dmg_immunities) + "; " + ", ".join(condition_immunities)
            )
        elif dmg_immunities:
            immunities = ", ".join(dmg_immunities)
        elif condition_immunities:
            immunities = ", ".join(condition_immunities)
        else:
            immunities = ""
        return (
            f"**Immunities** :: {immunities}\n"
            if dmg_immunities or condition_immunities
            else ""
        )

    @property
    def vulnerabilities_display(self) -> str:
        dmg_vulnerabilities = sorted(
            [
                dt.display_name
                for dt, res in self.damage_resistances.items()
                if res == Resistance.VULNERABLE
            ],
            key=lambda x: x.lower(),
        )
        condition_immunities = sorted(
            [
                condition.display_name
                for condition, resistance in self.condition_resistances.items()
                if resistance == Resistance.IMMUNE
            ],
            key=lambda x: x.lower(),
        )
        if dmg_vulnerabilities:
            vulns = ", ".join(dmg_vulnerabilities)
        else:
            vulns = ""
        return f"**Vulnerabilities** :: {vulns}\n" if dmg_vulnerabilities else ""

    @property
    def languages_display(self) -> str:
        return (
            (
                f"**Languages** :: {', '.join(sorted([l.display_name for l in self.languages]))}\n"
            )
            if self.languages
            else "**Languages** :: —"
        )

    @property
    def traits_display(self) -> str:
        alphabetical_traits = sorted(
            self.traits.values(), key=lambda trait: trait.title.lower()
        )
        if alphabetical_traits:
            traits_str = "\n:\n".join(
                [trait.homebrewery_v3_2024_markdown for trait in alphabetical_traits]
            )
            return f"### Traits\n{traits_str}\n"
        return "\n"

    @property
    def actions_display(self) -> str:
        alphabetical_actions = sorted(
            self.actions.values(), key=lambda action: action.title.lower()
        )
        multiattack_action = next(
            (
                action
                for action in alphabetical_actions
                if action.title == "Multiattack"
            ),
            None,
        )
        if multiattack_action is not None:
            alphabetical_actions.remove(multiattack_action)
            alphabetical_actions.insert(0, multiattack_action)
        if alphabetical_actions:
            actions_str = "\n:\n".join(
                [action.homebrewery_v3_2024_markdown for action in alphabetical_actions]
            )
            return f"### Actions\n{actions_str}\n"
        return "\n"

    @property
    def bonus_actions_display(self) -> str:
        alphabetical_bonus_actions = sorted(
            self.bonus_actions.values(),
            key=lambda bonus_action: bonus_action.title.lower(),
        )
        if alphabetical_bonus_actions:
            bonus_actions_str = "\n:\n".join(
                [
                    bonus_action.homebrewery_v3_2024_markdown
                    for bonus_action in alphabetical_bonus_actions
                ]
            )
            return f"### Bonus Actions\n{bonus_actions_str}\n"
        return "\n"

    @property
    def reactions_display(self) -> str:
        alphabetical_reactions = sorted(
            self.reactions.values(), key=lambda reaction: reaction.title.lower()
        )
        if alphabetical_reactions:
            reactions_str = "\n:\n".join(
                [
                    reaction.homebrewery_v3_2024_markdown
                    for reaction in alphabetical_reactions
                ]
            )
            return f"### Reactions\n{reactions_str}\n"
        return "\n"

    @property
    def legendary_actions_display(self) -> str:
        alphabetical_legendary_actions = sorted(
            self.legendary_actions.values(),
            key=lambda legendary_action: legendary_action.title.lower(),
        )
        if alphabetical_legendary_actions:
            legendary_actions_str = "\n:\n".join(
                [
                    legendary_action.homebrewery_v3_2024_markdown
                    for legendary_action in alphabetical_legendary_actions
                ]
            )
            return f"### Legendary Actions\n{legendary_actions_str}\n"
        return "\n"

    @property
    def tags_display(self) -> str:
        if self.tags:
            return f" ({', '.join(self.tags)})"
        return ""

    @property
    def all_available_prompt_info(self) -> str:
        strs = []
        for lbl, value in {
            "name": self.name,
            "description": self.description,
            "habitat": self.habitat,
            "creature type": self.creature_type.display_name or None,
            "alignment": self.alignment.display_name or None,
            "size": self.size.display_name or None,
            "ability scores": self.ability_scores.display_str or None,
        }.items():
            if value is not None:
                strs.append(f"The monster's {lbl} is: {value}")
        return ". ".join(strs)

    def has_required_fields(self, required_fields: list[str]) -> bool:
        return not any(
            (
                getattr(self, required_field, None) is None
                for required_field in required_fields
            )
        )

    def as_homebrewery_v3_markdown_2014(self, wide_statblock: bool = False) -> str:
        return ""

    def as_homebrewery_v3_markdown_2024(self, wide_statblock: bool = False) -> str:
        return (
            f"{{{{monster,frame{',wide' if wide_statblock else ''}\n"
            f"## {self.name}\n"
            f"*{self.size.display_name} {self.creature_type.display_name}{self.tags_display}, {self.alignment.display_name}*\n"
            "\n"
            f"**AC** :: {self.ac}\n"
            f"**HP** :: {self.hp}\n"
            f"**Speed** :: {self.speed_display}\n"
            "\n"
            f"**Initiative** :: {self.initiative}\n"
            "\n"
            "|   |   |  MOD | SAVE |   |   |  MOD | SAVE |   |   |  MOD | SAVE |\n"
            "|:--|:-:|:----:|:----:|:--|:-:|:----:|:----:|:--|:-:|:----:|:----:|\n"
            f"|Str| {self.strength}|  {self._stat_display(self.strength_mod)}  |  {self._stat_display(self.strength_save)}  |Dex| {self.dex}|  {self._stat_display(self.dex_mod)}  |  {self._stat_display(self.dex_save)} |Con| {self.con}|  {self._stat_display(self.con_mod)}  |  {self._stat_display(self.con_save)}  |\n"
            f"|Int| {self.intelligence}| {self._stat_display(self.intelligence_mod)}  | {self._stat_display(self.intelligence_save)}  |Wis| {self.wis}|  {self._stat_display(self.wis_mod)}  |  {self._stat_display(self.wis_save)}  |Cha|  {self.cha}| {self._stat_display(self.cha_mod)}  | {self._stat_display(self.cha_save)}  |\n"
            "\n"
            f"{self.skills_display}"
            f"{self.resistances_display}"
            f"{self.immunities_display}"
            f"{self.vulnerabilities_display}"
            f"{self.senses_display}"
            f"{self.languages_display}"
            f"**CR** :: {self.challenge_rating.display}\n"
            "\n"
            f"{self.traits_display}"
            f"{self.actions_display}"
            f"{self.bonus_actions_display}"
            f"{self.reactions_display}"
            f"{self.legendary_actions_display}"
            "}}\n"
        )

    def as_homebrewery_v3_markdown_2024_OLD(self, wide_statblock: bool = False) -> str:
        return (
            f"{{{{monster,frame{',wide' if wide_statblock else ''}\n"
            f"## {self.name}\n"
            f"*{self.size.display_name} {self.creature_type.display_name}{self.tags_display}, {self.alignment.display_name}*\n"
            "\n"
            f"**AC** :: {self.ac}\n"
            f"**HP** :: {self.hp}\n"
            f"**Speed** :: {self.speed_display}\n"
            "\column\n"
            f"**Initiative** :: {self.initiative}\n"
            "}}\n"
            "\n"
            "{{tables\n"
            "|   |   | MOD  | SAVE |\n"
            "|:--|:-:|:----:|:----:|\n"
            f"|Str| {self.strength} | {self._stat_display(self.strength_mod)} | {self._stat_display(self.strength_save)} |\n"
            f"|Int| {self.intelligence} | {self._stat_display(self.intelligence_mod)} | {self._stat_display(self.intelligence_save)} |\n"
            "\n"
            "|   |   | MOD  | SAVE |\n"
            "|:--|:-:|:----:|:----:|\n"
            f"|Dex| {self.dex} | {self._stat_display(self.dex_mod)} | {self._stat_display(self.dex_save)} |\n"
            f"|Wis| {self.wis} | {self._stat_display(self.wis_mod)} | {self._stat_display(self.wis_save)} |\n"
            "\n"
            "|   |   | MOD  | SAVE |\n"
            "|:--|:-:|:----:|:----:|\n"
            f"|Con| {self.con} | {self._stat_display(self.con_mod)} | {self._stat_display(self.con_save)} |\n"
            f"|Cha| {self.cha} | {self._stat_display(self.cha_mod)} | {self._stat_display(self.cha_save)} |\n"
            "}}\n"
            "\n"
            f"{self.skills_display}"
            f"{self.resistances_display}"
            f"{self.immunities_display}"
            f"{self.vulnerabilities_display}"
            f"{self.senses_display}"
            f"{self.languages_display}"
            f"**CR** :: {self.challenge_rating.display}\n"
            "}}\n"
            "\n"
            f"{self.traits_display}"
            f"{self.actions_display}"
            f"{self.bonus_actions_display}"
            f"{self.reactions_display}"
            f"{self.legendary_actions_display}"
            "}}\n"
        )
