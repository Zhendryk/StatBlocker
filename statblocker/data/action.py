from typing import Final
from enum import Enum, auto
from collections.abc import Sequence
from functools import cached_property
from dataclasses import dataclass, field
from statblocker.data.ability_scores import AbilityScores
from statblocker.data.enums import Ability, Proficiency, LimitedUsageType
from statblocker.data.macros import format_keyword_phrases, resolve_all_macros

# TODO: Probably need to do serde work in all of these classes


class CharacteristicType(Enum):
    TRAIT = auto()
    ACTION = auto()
    BONUS_ACTION = auto()
    REACTION = auto()
    LEGENDARY_ACTION = auto()


@dataclass
class CombatCharacteristic:
    monster_name: str
    ability_scores: AbilityScores
    proficiency_bonus: int
    saving_throws: dict[Ability, Proficiency]
    has_lair: bool
    title: str
    description: str
    ctype: CharacteristicType

    def __post_init__(self) -> None:
        self.monster_name = " ".join(
            [c.capitalize() for c in self.monster_name.split(" ")]
        )

    @property
    def resolved_description(self) -> str:
        desc = self.description.strip().rstrip(".")
        desc = format_keyword_phrases(desc)
        return resolve_all_macros(
            desc, self.monster_name, self.ability_scores, self.proficiency_bonus
        )

    @property
    def hb_v3_markdown(self) -> str:
        resolved_desc = self.resolved_description
        return f"***{self.title}.*** {resolved_desc}{'.' if not resolved_desc.endswith('.') else ''}"


@dataclass
class Trait(CombatCharacteristic):
    ctype: CharacteristicType = field(default=CharacteristicType.TRAIT)
    limited_use_type: LimitedUsageType = field(default=LimitedUsageType.UNLIMITED)
    limited_use_charges: dict[str, int] = field(default_factory=dict)
    lair_charge_bonuses: dict[str, int] = field(default_factory=dict)


@dataclass
class Action(CombatCharacteristic):
    ctype: CharacteristicType = field(default=CharacteristicType.ACTION)


@dataclass
class BonusAction(CombatCharacteristic):
    ctype: CharacteristicType = field(default=CharacteristicType.BONUS_ACTION)


@dataclass
class Reaction(CombatCharacteristic):
    ctype: CharacteristicType = field(default=CharacteristicType.REACTION)


@dataclass
class LegendaryAction(CombatCharacteristic):
    ctype: CharacteristicType = field(default=CharacteristicType.LEGENDARY_ACTION)


@dataclass(kw_only=True)
class CharacteristicTemplate:
    ctype: CharacteristicType
    label: str
    name: str
    description: str

    @cached_property
    def characteristic_cls(self) -> type[CombatCharacteristic]:
        return {
            CharacteristicType.TRAIT: Trait,
            CharacteristicType.ACTION: Action,
            CharacteristicType.BONUS_ACTION: BonusAction,
            CharacteristicType.REACTION: Reaction,
            CharacteristicType.LEGENDARY_ACTION: LegendaryAction,
        }[self.ctype]


@dataclass(kw_only=True)
class TraitTemplate(CharacteristicTemplate):
    ctype: CharacteristicType = field(default=CharacteristicType.TRAIT)


@dataclass(kw_only=True)
class MeleeAttackRollTemplate(CharacteristicTemplate):
    ability: Ability
    label: str = field(default="")
    name: str = field(default="")
    description: str = field(default="")

    def __post_init__(self) -> None:
        if not self.name:
            self.name = f"Melee Attack Roll ({self.ability.abbreviation})"
        if not self.label:
            self.label = self.name
        if not self.description:
            self.description = f"_Melee Attack Roll:_ [{self.ability.abbreviation} ATK], reach ??? ft. _Hit:_ [{self.ability.abbreviation} ???D???] ??? damage."


@dataclass(kw_only=True)
class RangedAttackRollTemplate(CharacteristicTemplate):
    ability: Ability
    label: str = field(default="")
    name: str = field(default="")
    description: str = field(default="")

    def __post_init__(self) -> None:
        if not self.name:
            self.name = f"Ranged Attack Roll ({self.ability.abbreviation})"
        if not self.label:
            self.label = self.name
        if not self.description:
            self.description = f"_Ranged Attack Roll:_ [{self.ability.abbreviation} ATK], range ??? ft. _Hit:_ [{self.ability.abbreviation} ???D???] ??? damage."


@dataclass(kw_only=True)
class MeleeOrRangedAttackRollTemplate(CharacteristicTemplate):
    ability: Ability
    label: str = field(default="")
    name: str = field(default="")
    description: str = field(default="")

    def __post_init__(self) -> None:
        if not self.name:
            self.name = f"Melee or Ranged Attack Roll ({self.ability.abbreviation})"
        if not self.label:
            self.label = self.name
        if not self.description:
            self.description = (
                f"_Melee or Ranged Attack Roll:_ [{self.ability.abbreviation} ATK], reach ??? ft. or range ??? ft. _Hit:_ [{self.ability.abbreviation} ???D???] ??? damage.",
            )


@dataclass(kw_only=True)
class SpellcastingTemplate(CharacteristicTemplate):
    ability: Ability
    name: str = field(default="Spellcasting")
    description: str = field(default="")

    def __post_init__(self) -> None:
        if not self.description:
            self.description = f"The [MON] casts one of the following spells, requiring no Material components and using {self.ability.name.capitalize()} as the spellcasting ability (spell save DC [{self.ability.abbreviation} SPELLSAVE], [{self.ability.abbreviation} ATK] to hit with spell attacks):\n:\n***At Will:*** _???_ (level ??? version)\n:\n***3/Day Each:*** _???_ (level ??? version)\n:\n***1/Day Each:*** _???_ (level ??? version)"


@dataclass(kw_only=True)
class SavingThrowTemplate(CharacteristicTemplate):
    ability: Ability
    label: str = field(default="")
    name: str = field(default="")
    description: str = field(default="")
    targeted: bool = field(default=False)

    def __post_init__(self) -> None:
        if self.targeted:
            self.name = f"{self.ability.name.capitalize()} Saving Throw (Targeted)"
            self.label = self.name
            self.description = f"_{self.ability.name.capitalize()} Saving Throw:_ DC [{self.ability.abbreviation} SAVE], one creature that ???. _Failure:_ ???. _Success:_ ???. _Failure or Success:_ ???."
        else:
            self.name = f"{self.ability.name.capitalize()} Saving Throw"
            self.label = self.name
            self.description = f"_{self.ability.name.capitalize()} Saving Throw:_ DC [{self.ability.abbreviation} SAVE]. _Failure:_ ???. _Success:_ ???. _Failure or Success:_ ???."


@dataclass(kw_only=True)
class MultiattackTemplate(CharacteristicTemplate):
    ctype: CharacteristicType = field(default=CharacteristicType.ACTION)
    label: str = field(default="Multiattack (Action)")
    name: str = field(default="Multiattack")
    description: str = field(default="The [MON] makes ??? ??? attacks.")


@dataclass(kw_only=True)
class BonusActionTemplate(CharacteristicTemplate):
    ctype: CharacteristicType = field(default=CharacteristicType.BONUS_ACTION)


@dataclass(kw_only=True)
class ReactionTemplate(CharacteristicTemplate):
    ctype: CharacteristicType = field(default=CharacteristicType.REACTION)


ALL_CHARACTERISTIC_TEMPLATES: Final[Sequence[CharacteristicTemplate]] = [
    # Traits
    TraitTemplate(
        label="Amphibious",
        name="Amphibious",
        description="The [MON] can breathe air and water.",
    ),
    TraitTemplate(
        label="Aversion to Fire",
        name="Aversion to Fire",
        description="If the [MON] takes Fire damage, it has Disadvantage on attack rolls and ability checks until the end of its next turn.",
    ),
    TraitTemplate(
        label="Battle Ready",
        name="Battle Ready",
        description="The [MON] has advantage on Initiative rolls.",
    ),
    TraitTemplate(
        label="Beast Whisperer",
        name="Beast Whisperer",
        description="The [MON] can communicate with Beasts as if they shared a common language.",
    ),
    TraitTemplate(
        label="Death Burst",
        name="Death Burst",
        description="The [MON] explodes when it dies. _Dexterity Saving Throw:_ DC [DEX SAVE], each creature in a 5-foot Emanation originating from the [MON]. _Failure:_ [???D???] ??? damage. _Success:_ Half damage.",
    ),
    TraitTemplate(
        label="Death Jinx",
        name="Death Jinx",
        description="When the [MON] dies, one random creature within 10 feet of the dead [MON] is targeted by a _Bane_ spell (save DC 13), which lasts for its full duration.",
    ),
    TraitTemplate(
        label="Demonic Restoration",
        name="Demonic Restoration",
        description="If the [MON] dies outside the Abyss, its body dissolves into ichor, and it gains a new body instantly, reviving with all of its Hit Points somewhere in the Abyss.",
    ),
    TraitTemplate(
        label="Dimensional Disruption",
        name="Dimensional Disruption",
        description="Disruptive energy extends from the [MON] in a 30-foot Emanation. Other creatures can't teleport to or from a space in that area. Any attempt to do so is wasted.",
    ),
    TraitTemplate(
        label="Disciple of the Nine Hells",
        name="Disciple of the Nine Hells",
        description="When the [MON] dies, its body disgorges a Hostile *Imp* in the same space.",
    ),
    TraitTemplate(
        label="Disintegration",
        name="Disintegration",
        description="When the [MON] dies, its body and nonmagical possessions turn to dust. Any magic items it possessed are left behind in its space.",
    ),
    TraitTemplate(
        label="Emissary of Juiblex",
        name="Emissary of Juiblex",
        description="When the [MON] dies, its body disgorges a Hostile *Ochre Jelly* in the same space.",
    ),
    TraitTemplate(
        label="Fey Ancestry",
        name="Fey Ancestry",
        description="The [MON] has Advantage on saving throws it makes to avoid or end the Charmed condition, and magic can't put it to sleep.",
    ),
    TraitTemplate(
        label="Flyby",
        name="Flyby",
        description="The [MON] doesn't provoke an Opportunity Attack when it flies out of an enemy's reach.",
    ),
    TraitTemplate(
        label="Forbiddance",
        name="Forbiddance",
        description="The [MON] can't enter a residence without an invitation from one of its occupants.",
    ),
    TraitTemplate(
        label="Gloom Shroud",
        name="Gloom Shroud",
        description="Imperceptible energy channeled from the Shadowfell extends from the creature in a 20-foot Emanation. Other creatures in that area have Disadvantage on Charisma checks and Charisma saving throws.",
    ),
    TraitTemplate(
        label="Incorporeal Movement",
        name="Incorporeal Movement",
        description="The [MON] can move through others creatures and objects as if they were Difficult Terrain. It takes [1D10] Force damage if it ends its turn inside an object.",
    ),
    TraitTemplate(
        label="Light",
        name="Light",
        description="The [MON] sheds Bright Light in a 10-foot radius and Dim Light for an additional 10 feet. As a Bonus Action, the creature can suppress this light or cause it to return. The light winks out if the [MON] dies.",
    ),
    TraitTemplate(
        label="Magic Resistance",
        name="Magic Resistance",
        description="The [MON] has Advantage on saving throws against spells and other magical effects.",
    ),
    TraitTemplate(
        label="Mimicry",
        name="Mimicry",
        description="The [MON] can mimic Beast sounds and Humanoid voices. A creature that hears the sounds can tell they are imitations with a successful DC [WIS SAVE] Wisdom (Insight) check.",
    ),
    TraitTemplate(
        label="Pack Tactics",
        name="Pack Tactics",
        description="The [MON] has Advantage on an attack roll against a creature if at least one of the [MON]'s allies is within 5 feet of the creature and the ally doesn't have the Incapacitated condition.",
    ),
    TraitTemplate(
        label="Poison Tolerant",
        name="Poison Tolerant",
        description="The [MON] has Advantage on saving throws it makes to avoid or end the Poisoned condition.",
    ),
    TraitTemplate(
        label="Regeneration",
        name="Regeneration",
        description="The [MON] regains ??? Hit Points at the start of each of its turns. If the [MON] takes ??? damage, this trait doesn't function on the [MON]'s next turn. The [MON] dies only if it starts its turn with 0 Hit Points and doesn't regenerate.",
    ),
    TraitTemplate(
        label="Resonant Connection",
        name="Resonant Connection",
        description="The [MON] has a supernatural connection to another creature or an object and knows the most direct route to it, provided the two are within 1 mile of each other.",
    ),
    TraitTemplate(
        label="Siege Monster",
        name="Siege Monster",
        description="The [MON] deals double damage to objects and structures.",
    ),
    TraitTemplate(
        label="Slaad Host",
        name="Slaad Host",
        description="When the [MON] dies, a Hostile *Slaad Tadpole* bursts from its innards in the same space.",
    ),
    TraitTemplate(
        label="Steadfast",
        name="Steadfast",
        description="The [MON] has Immunity to the Frightened condition while it can see an ally within 30 feet of itself.",
    ),
    TraitTemplate(
        label="Sunlight Sensitivity",
        name="Sunlight Sensitivity",
        description="While in sunlight, the [MON] has Disadvantage on ability checks and attack rolls.",
    ),
    TraitTemplate(
        label="Swarm",
        name="Swarm",
        description="The swarm can occupy another creature's space and vice versa, and the swarm can move through any opening large enough for a Tiny ???. The swarm can't regain Hit Points or gain Temporary Hit Points.",
    ),
    TraitTemplate(
        label="Telepathic Bond",
        name="Telepathic Bond",
        description="The [MON] is linked psychically to another creature. While both are on the same plane of existence, they can communicate telepathically with each other.",
    ),
    TraitTemplate(
        label="Telepathic Shroud",
        name="Telepathic Shroud",
        description="The [MON] is immune to any effect that would sense its emotions or read its thoughts, as well as to spells from the school of Divination. As a Bonus Action, the creature can suppress this trait or reactivate it.",
    ),
    TraitTemplate(
        label="Ventriloquism",
        name="Ventriloquism",
        description="Whenever the [MON] speaks, it can choose a point within 30 feet of itself; its voice emanates from that point.",
    ),
    TraitTemplate(
        label="Warrior's Wrath",
        name="Warrior's Wrath",
        description="The [MON] has Advantage on melee attack rolls against any Bloodied creature.",
    ),
    TraitTemplate(
        label="Wild Talent",
        name="Wild Talent",
        description="Choose one cantrip; the creature can cast that cantrip without spell components, using Intelligence, Wisdom or Charisma as the spellcasting ability.",
    ),
    # Actions
    MultiattackTemplate(),
    MeleeAttackRollTemplate(ctype=CharacteristicType.ACTION, ability=Ability.STRENGTH),
    MeleeAttackRollTemplate(ctype=CharacteristicType.ACTION, ability=Ability.DEXTERITY),
    RangedAttackRollTemplate(ctype=CharacteristicType.ACTION, ability=Ability.STRENGTH),
    RangedAttackRollTemplate(
        ctype=CharacteristicType.ACTION, ability=Ability.DEXTERITY
    ),
    MeleeOrRangedAttackRollTemplate(
        ctype=CharacteristicType.ACTION, ability=Ability.STRENGTH
    ),
    MeleeOrRangedAttackRollTemplate(
        ctype=CharacteristicType.ACTION, ability=Ability.DEXTERITY
    ),
    SpellcastingTemplate(
        ctype=CharacteristicType.ACTION,
        label=f"Spellcasting (INT)",
        ability=Ability.INTELLIGENCE,
    ),
    SpellcastingTemplate(
        ctype=CharacteristicType.ACTION,
        label=f"Spellcasting (WIS)",
        ability=Ability.WISDOM,
    ),
    SpellcastingTemplate(
        ctype=CharacteristicType.ACTION,
        label=f"Spellcasting (CHA)",
        ability=Ability.CHARISMA,
    ),
    SavingThrowTemplate(ctype=CharacteristicType.ACTION, ability=Ability.STRENGTH),
    SavingThrowTemplate(
        ctype=CharacteristicType.ACTION, ability=Ability.STRENGTH, targeted=True
    ),
    SavingThrowTemplate(ctype=CharacteristicType.ACTION, ability=Ability.DEXTERITY),
    SavingThrowTemplate(
        ctype=CharacteristicType.ACTION, ability=Ability.DEXTERITY, targeted=True
    ),
    SavingThrowTemplate(ctype=CharacteristicType.ACTION, ability=Ability.CONSTITUTION),
    SavingThrowTemplate(
        ctype=CharacteristicType.ACTION, ability=Ability.CONSTITUTION, targeted=True
    ),
    SavingThrowTemplate(ctype=CharacteristicType.ACTION, ability=Ability.INTELLIGENCE),
    SavingThrowTemplate(
        ctype=CharacteristicType.ACTION, ability=Ability.INTELLIGENCE, targeted=True
    ),
    SavingThrowTemplate(ctype=CharacteristicType.ACTION, ability=Ability.WISDOM),
    SavingThrowTemplate(
        ctype=CharacteristicType.ACTION, ability=Ability.WISDOM, targeted=True
    ),
    SavingThrowTemplate(ctype=CharacteristicType.ACTION, ability=Ability.CHARISMA),
    SavingThrowTemplate(
        ctype=CharacteristicType.ACTION, ability=Ability.CHARISMA, targeted=True
    ),
    MeleeOrRangedAttackRollTemplate(
        ctype=CharacteristicType.ACTION,
        label="Dagger",
        name="Dagger",
        description="_Melee or Ranged Attack Roll:_ [DEX ATK], reach 5 ft. or range 20/60 ft. _Hit:_ [DEX 1D4] Piercing damage.",
        ability=Ability.DEXTERITY,
    ),
    MeleeAttackRollTemplate(
        ctype=CharacteristicType.ACTION,
        label="Greatsword",
        name="Greatsword",
        description="_Melee Attack Roll:_ [STR ATK], reach 5 ft. _Hit:_ [STR 2D6] Slashing damage.",
        ability=Ability.STRENGTH,
    ),
    MeleeAttackRollTemplate(
        ctype=CharacteristicType.ACTION,
        label="Shortsword",
        name="Shortsword",
        description="_Melee Attack Roll:_ [STR ATK], reach 5 ft. _Hit:_ [STR 1D6] Piercing damage.",
        ability=Ability.STRENGTH,
    ),
    MeleeAttackRollTemplate(
        ctype=CharacteristicType.ACTION,
        label="Longsword",
        name="Longsword",
        description="_Melee Attack Roll:_ [STR ATK], reach 5 ft. _Hit:_ [STR 1D8] Slashing damage.",
        ability=Ability.STRENGTH,
    ),
    MeleeAttackRollTemplate(
        ctype=CharacteristicType.ACTION,
        label="Club",
        name="Club",
        description="_Melee Attack Roll:_ [STR ATK], reach 5 ft. _Hit:_ [STR 1D4] Bludgeoning damage.",
        ability=Ability.STRENGTH,
    ),
    MeleeAttackRollTemplate(
        ctype=CharacteristicType.ACTION,
        label="Mace",
        name="Mace",
        description="_Melee Attack Roll:_ [STR ATK], reach 5 ft. _Hit:_ [STR 1D6] Bludgeoning damage.",
        ability=Ability.STRENGTH,
    ),
    MeleeAttackRollTemplate(
        ctype=CharacteristicType.ACTION,
        label="Handaxe",
        name="Handaxe",
        description="_Melee Attack Roll:_ [STR ATK], reach 5 ft. _Hit:_ [STR 1D6] Slashing damage.",
        ability=Ability.STRENGTH,
    ),
    MeleeAttackRollTemplate(
        ctype=CharacteristicType.ACTION,
        label="Greataxe",
        name="Greataxe",
        description="_Melee Attack Roll:_ [STR ATK], reach 5 ft. _Hit:_ [STR 1D12] Slashing damage.",
        ability=Ability.STRENGTH,
    ),
    MeleeAttackRollTemplate(
        ctype=CharacteristicType.ACTION,
        label="Warhammer",
        name="Warhammer",
        description="_Melee Attack Roll:_ [STR ATK], reach 5 ft. _Hit:_ [STR 1D8] Bludgeoning damage.",
        ability=Ability.STRENGTH,
    ),
    MeleeAttackRollTemplate(
        ctype=CharacteristicType.ACTION,
        label="Maul",
        name="Maul",
        description="_Melee Attack Roll:_ [STR ATK], reach 5 ft. _Hit:_ [STR 2D6] Bludgeoning damage.",
        ability=Ability.STRENGTH,
    ),
    MeleeAttackRollTemplate(
        ctype=CharacteristicType.ACTION,
        label="Glaive",
        name="Glaive",
        description="_Melee Attack Roll:_ [STR ATK], reach 5 ft. _Hit:_ [STR 1D10] Slashing damage.",
        ability=Ability.STRENGTH,
    ),
    MeleeAttackRollTemplate(
        ctype=CharacteristicType.ACTION,
        label="Rapier",
        name="Rapier",
        description="_Melee Attack Roll:_ [DEX ATK], reach 5 ft. _Hit:_ [DEX 1D8] Piercing damage.",
        ability=Ability.DEXTERITY,
    ),
    MeleeAttackRollTemplate(
        ctype=CharacteristicType.ACTION,
        label="Bite",
        name="Bite",
        description="_Melee Attack Roll:_ [DEX ATK], reach 5 ft. _Hit:_ [DEX 2D4] Piercing damage.",
        ability=Ability.DEXTERITY,
    ),
    MeleeAttackRollTemplate(
        ctype=CharacteristicType.ACTION,
        label="Bites (Swarm)",
        name="Bites",
        description="_Melee Attack Roll:_ [DEX ATK], reach 5 ft. _Hit:_ [DEX 2D4] Piercing damage, or [DEX 1D4] Piercing damage if the swarm is Bloodied.",
        ability=Ability.DEXTERITY,
    ),
    MeleeAttackRollTemplate(
        ctype=CharacteristicType.ACTION,
        label="Claw",
        name="Claw",
        description="_Melee Attack Roll:_ [STR ATK], reach 5 ft. _Hit:_ [STR 1D6] Slashing damage. If the target is a Large or smaller creature, it has the Grappled condition (escape DC [STR SAVE]) from one of two claws.",
        ability=Ability.STRENGTH,
    ),
    MeleeAttackRollTemplate(
        ctype=CharacteristicType.ACTION,
        label="Gore",
        name="Gore",
        description="_Melee Attack Roll:_ [STR ATK], reach 5 ft. _Hit:_ [STR 2D8] Piercing damage. If the target is a Large or smaller creature and the [MON] moved 20+ feet straight toward it immediately before the hit, the target takes an extra [2D8] Piercing damage and has the Prone condition.",
        ability=Ability.STRENGTH,
    ),
    MeleeAttackRollTemplate(
        ctype=CharacteristicType.ACTION,
        label="Hooves",
        name="Hooves",
        description="_Melee Attack Roll:_ [STR ATK], reach 5 ft. _Hit:_ [STR 1D8] Bludgeoning damage.",
        ability=Ability.STRENGTH,
    ),
    MeleeAttackRollTemplate(
        ctype=CharacteristicType.ACTION,
        label="Slam",
        name="Slam",
        description="_Melee Attack Roll:_ [STR ATK], reach 5 ft. _Hit:_ [STR 1D8] Bludgeoning damage.",
        ability=Ability.STRENGTH,
    ),
    MeleeAttackRollTemplate(
        ctype=CharacteristicType.ACTION,
        label="Tentacles",
        name="Tentacles",
        description="_Melee Attack Roll:_ [DEX ATK], reach 5 ft. _Hit:_ [DEX 1D6] Bludgeoning damage.",
        ability=Ability.DEXTERITY,
    ),
    MeleeAttackRollTemplate(
        ctype=CharacteristicType.ACTION,
        label="Rend",
        name="Rend",
        description="_Melee Attack Roll:_ [STR ATK], reach 5 ft. _Hit:_ [STR 2D6] Slashing damage. If the target is a Large or smaller creature, it has the Prone condition.",
        ability=Ability.STRENGTH,
    ),
    RangedAttackRollTemplate(
        ctype=CharacteristicType.ACTION,
        label="Longbow",
        name="Longbow",
        description="_Ranged Attack Roll:_ [DEX ATK], range 150/600 ft. _Hit:_ [DEX 1D8] Piercing damage.",
        ability=Ability.DEXTERITY,
    ),
    RangedAttackRollTemplate(
        ctype=CharacteristicType.ACTION,
        label="Shortbow",
        name="Shortbow",
        description="_Ranged Attack Roll:_ [DEX ATK], range 80/320 ft. _Hit:_ [DEX 1D6] Piercing damage.",
        ability=Ability.DEXTERITY,
    ),
    RangedAttackRollTemplate(
        ctype=CharacteristicType.ACTION,
        label="Heavy Crossbow",
        name="Heavy Crossbow",
        description="_Ranged Attack Roll:_ [DEX ATK], range 100/400 ft. _Hit:_ [DEX 1D10] Piercing damage.",
        ability=Ability.DEXTERITY,
    ),
    RangedAttackRollTemplate(
        ctype=CharacteristicType.ACTION,
        label="Light Crossbow",
        name="Light Crossbow",
        description="_Ranged Attack Roll:_ [DEX ATK], range 80/320 ft. _Hit:_ [DEX 1D8] Piercing damage.",
        ability=Ability.DEXTERITY,
    ),
    RangedAttackRollTemplate(
        ctype=CharacteristicType.ACTION,
        label="Hand Crossbow",
        name="Hand Crossbow",
        description="_Ranged Attack Roll:_ [DEX ATK], range 30/120 ft. _Hit:_ [DEX 1D6] Piercing damage.",
        ability=Ability.DEXTERITY,
    ),
    # Bonus Actions
    BonusActionTemplate(
        label="Leap",
        name="Leap",
        description="The [MON] jumps up to 30 feet by spending 10 feet of movement.",
    ),
    # Reactions
    ReactionTemplate(
        label="Parry",
        name="Parry",
        description="_Trigger:_ The [MON] is hit by a melee attack roll while holding a weapon. _Response:_ The [MON] adds 2 to its AC against that attack, possibly causing it to miss.",
    ),
    # Legendary Actions
    TraitTemplate(
        label="Legendary Resistance (???/Day, or ???/Day in Lair)",
        name="Legendary Resistance (???/Day, or ???/Day in Lair)",
        description="If the [MON] fails a saving throw, it can choose to succeed instead.",
    ),
    # CharacteristicTemplate(CharacteristicType.LEGENDARY_ACTION, "Blah", "Blah"),
]

CUSTOM_TEMPLATES: Final[Sequence[CharacteristicTemplate]] = [
    # Traits
    TraitTemplate(
        label="Corrupting Presence",
        name="Corrupting Presence",
        description="Healing spells cast within a 30-foot Emanation from the [MON] restore only half the usual amount of Hit Points.",
    ),
    TraitTemplate(
        label="Dreadful Clarity",
        name="Dreadful Clarity",
        description="The [MON] has Advantage on all attacks against any creature that is Frightened by it.",
    ),
    TraitTemplate(
        label="Night Veil",
        name="Night Veil",
        description="While in Dim Light or Darkness, the [MON] gains Resistance to Bludgeoning, Piercing and Slashing damage.",
    ),
    TraitTemplate(
        label="Grisly Rebirth",
        name="Grisly Rebirth",
        description="When the [MON] dies, roll 1d6. On a result of 5 or higher, at the start of its next turn, it horrifically reanimates with half of its maximum Hit Points. If killed again, this trait does not trigger again.",
    ),
    TraitTemplate(
        label="Eldritch Reflection",
        name="Eldritch Reflection",
        description="Once per round, when the [MON] successfully saves against a targeted spell or spell attack by 5 or more, it can immediately reflect the spell back at the caster. The caster must succeed on the original saving throw or be affected by their own spell.",
    ),
    TraitTemplate(
        label="Parasitic Horror",
        name="Parasitic Horror",
        description="When the [MON] grapples a creature, that creature must succeed on a DC [CON SAVE] Constitution saving throw or be implanted with a parasite. This parasite will grow for [1D10] days until it transforms its host into a [MON], unless the creature is cured with a Lesser Restoration spell or otherwise has the parasite removed.",
    ),
    TraitTemplate(
        label="Weeping Wounds",
        name="Weeping Wounds",
        description="When the [MON] deals damage with a melee attack, the target suffers from deep, bleeding wounds. At the start of the wounded creature's turn, it takes [1D4] Necrotic damage and it cannot regain Hit Points until it or another creature spends an action to staunch the wound, ending this effect.",
    ),
    TraitTemplate(
        label="Blighted Ground",
        name="Blighted Ground",
        description="The terrain within 15 feet of the [MON] is considered Difficult Terrain. Creatures who start their turn within this radius must succeed on a DC [CON SAVE] Constitution saving throw or take [1d6] Poison damage and have their speed reduced by 10 feet until the start of their next turn.",
    ),
    TraitTemplate(
        label="Duskrot Carrier",
        name="Duskrot Carrier",
        description="The [MON] is a carrier of the Duskrot plague. Creatures hit by the [MON]'s melee attacks must succeed on a DC [CON SAVE] Constitution saving throw or become infected with Duskrot, if it is not already (per Stahltrom's setting-specific disease mechanics).",
    ),
    TraitTemplate(
        label="Stygian Symbiosis",
        name="Stygian Symbiosis",
        description="While within 10 feet of another creature with this trait, both creatures gain +2 to their AC as their corrupted flesh briefly knits together.",
    ),
    TraitTemplate(
        label="Skinwalker's Guise",
        name="Skinwalker's Guise",
        description="The [MON] can perfectly replicate the appearance, voice and general mannerisms of any creature it has killed within the last 24 hours. A successful DC [WIS SAVE] Insight check reveals its true nature.",
    ),
    TraitTemplate(
        label="Aura of Agony",
        name="Aura of Agony",
        description="Whenever a creature within 5 feet of the [MON] deals damage to it with a melee attack, that attacker takes [1D8] Psychic damage as the pain rebounds onto them.",
    ),
    TraitTemplate(
        label="Veinburst",
        name="Veinburst",
        description="When the [MON] is first reduced below half of its maximum Hit Points, its veins violently rupture, spraying tainted blood. Each creature within a 10-foot Emanation from the [MON] must succeed on a DC [DEX SAVE] Dexterity saving throw or have the Poisoned condition for 1 minute.",
    ),
    # Actions
    # Bonus Actions
    # Reactions
    ReactionTemplate(
        label="Ghastly Imitation",
        name="Ghastly Imitation",
        description="_Trigger:_ The [MON] is the target of any enemy attack roll. _Response:_ The [MON] briefly takes on the visage of the attacker's loved one or ally. The attacker must succeed on a DC [WIS SAVE] saving throw or suffer Disadvantage on that attack.",
    ),
    # Legendary Actions
]


def get_all_templates() -> dict[str, CharacteristicTemplate]:
    return {
        template.label: template
        for template in ALL_CHARACTERISTIC_TEMPLATES + CUSTOM_TEMPLATES
    }
