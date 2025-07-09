from __future__ import annotations
import math
from random import randint
from enum import Enum, auto
from statblocker.data.bases import StatblockEnum


class Habitat(StatblockEnum):
    ANY = auto()
    UNDERDARK = auto()
    URBAN = auto()
    FOREST = auto()
    GRASSLAND = auto()
    ARCTIC = auto()
    HILL = auto()
    MOUNTAIN = auto()
    UNDERWATER = auto()
    SWAMP = auto()
    COASTAL = auto()
    DESERT = auto()
    PLANAR_ABYSS = auto()
    PLANAR_NINE_HELLS = auto()
    PLANAR_UPPER_PLANES = auto()
    PLANAR_LOWER_PLANES = auto()
    PLANAR_OUTER_PLANES = auto()
    PLANAR_LIMBO = auto()
    PLANAR_FEYWILD = auto()
    PLANAR_ASTRAL_PLANE = auto()
    PLANAR_ELEMENTAL_CHAOS = auto()
    PLANAR_ELEMENTAL_PLANE_OF_FIRE = auto()
    PLANAR_ELEMENTAL_PLANE_OF_AIR = auto()
    PLANAR_ELEMENTAL_PLANE_OF_WATER = auto()
    PLANAR_ELEMENTAL_PLANE_OF_EARTH = auto()


class Treasure(StatblockEnum):
    NONE = auto()
    ANY = auto()
    ARCANA = auto()
    ARMAMENTS = auto()
    IMPLEMENTS = auto()
    INDIVIDUAL = auto()
    RELICS = auto()


class Ability(StatblockEnum):
    STRENGTH = auto()
    DEXTERITY = auto()
    CONSTITUTION = auto()
    INTELLIGENCE = auto()
    WISDOM = auto()
    CHARISMA = auto()

    @property
    def abbreviation(self) -> str:
        return self.name.upper()[:3]

    @staticmethod
    def from_abbreviation(abbreviation: str) -> Ability:
        for a in Ability:
            if abbreviation.upper() == a.abbreviation:
                return a
        raise ValueError(f"Invalid Ability abbreviation: {abbreviation}")


class ActionType(StatblockEnum):
    ACTION = auto()
    BONUS_ACTION = auto()
    REACTION = auto()
    LEGENDARY_ACTION = auto()


class ActionSubtype(StatblockEnum):
    MELEE_ATTACK_ROLL = auto()
    RANGED_ATTACK_ROLL = auto()
    MELEE_OR_RANGED_ATTACK_ROLL = auto()
    STRENGTH_SAVING_THROW = auto()
    DEXTERITY_SAVING_THROW = auto()
    CONSTITUTION_SAVING_THROW = auto()
    INTELLIGENCE_SAVING_THROW = auto()
    WISDOM_SAVING_THROW = auto()
    CHARISMA_SAVING_THROW = auto()


class Alignment(StatblockEnum):
    UNALIGNED = auto()
    LAWFUL_GOOD = auto()
    NEUTRAL_GOOD = auto()
    CHAOTIC_GOOD = auto()
    LAWFUL_NEUTRAL = auto()
    NEUTRAL = auto()
    CHAOTIC_NEUTRAL = auto()
    LAWFUL_EVIL = auto()
    NEUTRAL_EVIL = auto()
    CHAOTIC_EVIL = auto()


class Condition(StatblockEnum):
    BLINDED = auto()
    CHARMED = auto()
    DEAFENED = auto()
    EXHAUSTION = auto()
    FRIGHTENED = auto()
    GRAPPLED = auto()
    INCAPACITATED = auto()
    INVISIBLE = auto()
    PARALYZED = auto()
    PETRIFIED = auto()
    POISONED = auto()
    PRONE = auto()
    RESTRAINED = auto()
    STUNNED = auto()
    UNCONSCIOUS = auto()


class CreatureType(StatblockEnum):
    ABERRATION = auto()
    BEAST = auto()
    CELESTIAL = auto()
    CONSTRUCT = auto()
    DRAGON = auto()
    ELEMENTAL = auto()
    FEY = auto()
    FIEND = auto()
    GIANT = auto()
    HUMANOID = auto()
    MONSTROSITY = auto()
    OOZE = auto()
    PLANT = auto()
    UNDEAD = auto()


class CoverType(StatblockEnum):
    HALF_COVER = auto()
    THREE_QUARTERS_COVER = auto()
    FULL_COVER = auto()


class DamageArea(StatblockEnum):
    CONE = auto()
    SPHERE = auto()
    LINE = auto()
    EMANATION = auto()


class DamageType(StatblockEnum):
    ACID = auto()
    COLD = auto()
    FIRE = auto()
    FORCE = auto()
    LIGHTNING = auto()
    NECROTIC = auto()
    POISON = auto()
    PSYCHIC = auto()
    RADIANT = auto()
    THUNDER = auto()
    BLUDGEONING = auto()
    SLASHING = auto()
    PIERCING = auto()


class RollType(Enum):
    NORMAL = auto()
    AVERAGE = auto()
    MIN = auto()
    MAX = auto()


class Die(StatblockEnum):
    D4 = 4
    D6 = 6
    D8 = 8
    D10 = 10
    D12 = 12
    D20 = 20

    @property
    def avg_value(self) -> float:
        return float((self.value + 1) / 2)

    @property
    def max_value(self) -> int:
        return self.value

    @property
    def min_value(self) -> int:
        return 1

    def roll(self, num_dice: int, roll_type: RollType = RollType.NORMAL) -> int:
        match roll_type:
            case RollType.NORMAL:
                return sum(
                    [randint(self.min_value, self.max_value) for _ in range(num_dice)]
                )
            case RollType.MIN:
                return sum([self.min_value for _ in range(num_dice)])
            case RollType.MAX:
                return sum([self.max_value for _ in range(num_dice)])
            case RollType.AVERAGE:
                return math.floor(self.avg_value * num_dice)
            case _:
                raise NotImplementedError


class Hazard(StatblockEnum):
    BURNING = auto()
    DEHYDRATION = auto()
    FALLING = auto()
    MALNUTRITION = auto()
    SUFFOCATION = auto()


class LanguageProficiency(StatblockEnum):
    UNDERSTANDS = auto()
    SPEAKS = auto()


class Language(StatblockEnum):
    COMMON = auto()
    COMMON_PLUS_ONE_OTHER_LANGUAGE = auto()
    COMMON_PLUS_TWO_OTHER_LANGUAGES = auto()
    COMMON_PLUS_THREE_OTHER_LANGUAGES = auto()
    COMMON_PLUS_FOUR_OTHER_LANGUAGES = auto()
    COMMON_PLUS_FIVE_OTHER_LANGUAGES = auto()
    DWARVISH = auto()
    ELVISH = auto()
    GIANT = auto()
    GNOMISH = auto()
    GOBLIN = auto()
    HALFLING = auto()
    ORC = auto()
    DRACONIC = auto()
    COMMON_SIGN_LANGUAGE = auto()
    ABYSSAL = auto()
    CELESTIAL = auto()
    INFERNAL = auto()
    DEEP_SPEECH = auto()
    PRIMORDIAL = auto()
    SYLVAN = auto()
    UNDERCOMMON = auto()

    @property
    def is_rare(self) -> bool:
        match self:
            case (
                Language.ABYSSAL
                | Language.CELESTIAL
                | Language.INFERNAL
                | Language.DEEP_SPEECH
                | Language.PRIMORDIAL
                | Language.SYLVAN
                | Language.UNDERCOMMON
            ):
                return True
            case _:
                return False

    @property
    def display_name(self) -> str:
        match self:
            case (
                Language.COMMON_PLUS_ONE_OTHER_LANGUAGE
                | Language.COMMON_PLUS_TWO_OTHER_LANGUAGES
                | Language.COMMON_PLUS_THREE_OTHER_LANGUAGES
                | Language.COMMON_PLUS_FOUR_OTHER_LANGUAGES
                | Language.COMMON_PLUS_FIVE_OTHER_LANGUAGES
            ):
                return " ".join(self.name.split("_")).capitalize()
            case _:
                return super().display_name


class LightingCondition(StatblockEnum):
    BRIGHT_LIGHT = auto()
    DIM_LIGHT = auto()
    DARKNESS = auto()


class LimitedUsageType(StatblockEnum):
    UNLIMITED = auto()
    X_PER_DAY = auto()
    RECHARGE_X_Y = auto()
    RECHARGE_AFTER_SHORT_REST = auto()
    RECHARGE_AFTER_LONG_REST = auto()
    RECHARGE_AFTER_SHORT_OR_LONG_REST = auto()


class ObscurityLevel(StatblockEnum):
    LIGHTLY_OBSCURED = auto()
    HEAVILY_OBSCURED = auto()


class Proficiency(StatblockEnum):
    NORMAL = auto()
    PROFICIENT = auto()
    EXPERTISE = auto()


class Resistance(StatblockEnum):
    NORMAL = auto()
    VULNERABLE = auto()
    RESISTANT = auto()
    IMMUNE = auto()


class Sense(StatblockEnum):
    BLINDSIGHT = auto()
    DARKVISION = auto()
    TREMORSENSE = auto()
    TRUESIGHT = auto()


class Size(StatblockEnum):
    TINY = auto()
    SMALL = auto()
    MEDIUM = auto()
    LARGE = auto()
    HUGE = auto()
    GARGANTUAN = auto()

    @property
    def hit_die(self) -> Die:
        match self:
            case Size.TINY:
                return Die.D4
            case Size.SMALL:
                return Die.D6
            case Size.MEDIUM:
                return Die.D8
            case Size.LARGE:
                return Die.D10
            case Size.HUGE:
                return Die.D12
            case Size.GARGANTUAN:
                return Die.D20
            case _:
                raise NotImplementedError


class Skill(StatblockEnum):
    # Strength
    ATHLETICS = auto()

    # Dexterity
    ACROBATICS = auto()
    SLEIGHT_OF_HAND = auto()
    STEALTH = auto()

    # Intelligence
    ARCANA = auto()
    HISTORY = auto()
    INVESTIGATION = auto()
    NATURE = auto()
    RELIGION = auto()

    # Wisdom
    ANIMAL_HANDLING = auto()
    INSIGHT = auto()
    MEDICINE = auto()
    PERCEPTION = auto()
    SURVIVAL = auto()

    # Charisma
    DECEPTION = auto()
    INTIMIDATION = auto()
    PERFORMANCE = auto()
    PERSUASION = auto()

    @property
    def associated_ability(self) -> Ability:
        match self:
            case Skill.ATHLETICS:
                return Ability.STRENGTH
            case Skill.ACROBATICS | Skill.SLEIGHT_OF_HAND | Skill.STEALTH:
                return Ability.DEXTERITY
            case (
                Skill.ARCANA
                | Skill.HISTORY
                | Skill.INVESTIGATION
                | Skill.NATURE
                | Skill.RELIGION
            ):
                return Ability.INTELLIGENCE
            case (
                Skill.ANIMAL_HANDLING
                | Skill.INSIGHT
                | Skill.MEDICINE
                | Skill.PERCEPTION
                | Skill.SURVIVAL
            ):
                return Ability.WISDOM
            case (
                Skill.DECEPTION
                | Skill.INTIMIDATION
                | Skill.PERFORMANCE
                | Skill.PERSUASION
            ):
                return Ability.CHARISMA
            case _:
                raise NotImplementedError


class SpeedType(StatblockEnum):
    WALK = auto()
    BURROW = auto()
    CLIMB = auto()
    FLY = auto()
    FLY_HOVER = auto()
    SWIM = auto()

    def display_str(self, value: int) -> str:
        match self:
            case SpeedType.WALK:
                return f"{value} ft."
            case SpeedType.BURROW | SpeedType.CLIMB | SpeedType.FLY | SpeedType.SWIM:
                return f"{self.name.capitalize()} {value} ft." if value else ""
            case SpeedType.FLY_HOVER:
                return f"Fly {value} ft. (hover)" if value else ""
            case _:
                raise NotImplementedError
