import re
from typing import Final
from functools import partial
from copy import copy
from statblocker.data.dice import Dice
from statblocker.data.enums import (
    ActionType,
    Die,
    Ability,
    Condition,
    Sense,
    DamageType,
    Skill,
    Size,
    CreatureType,
    DamageArea,
    Hazard,
    CoverType,
    LightingCondition,
    ObscurityLevel,
)
from statblocker.data.ability_scores import AbilityScores, calculate_ability_modifier

# [XDY] - computes a roll of X dY dice
PATTERN_DICE_ROLL: Final[re.Pattern] = re.compile(r"\[(\d+)([dD](?:4|6|8|10|12|20))\]")
CG_DICE_ROLL_NUM_DICE: Final[int] = 1
CG_DICE_ROLL_DIE_TYPE: Final[int] = 2

# [MON] - show monster name
PATTERN_MONSTER_NAME: Final[re.Pattern] = re.compile(r"\[MON\]")

# [<STAT>] - show stat modifier
PATTERN_STAT_MODIFIER: Final[re.Pattern] = re.compile(r"\[(STR|DEX|CON|INT|WIS|CHA)\]")
CG_STAT_MODIFIER_STAT: Final[int] = 1

# [<STAT> ATK] - calculates modifier to attack roll for a <STAT> based attack
PATTERN_STAT_ATK_ROLL: Final[re.Pattern] = re.compile(
    r"\[(STR|DEX|CON|INT|WIS|CHA)\sATK\]"
)
CG_STAT_ATK_ROLL_STAT: Final[int] = 1

# [<STAT> XDY] - calculates the damage roll for a <STAT> based attack with XdY damage dice
PATTERN_STAT_DMG_ROLL: Final[re.Pattern] = re.compile(
    r"\[(STR|DEX|CON|INT|WIS|CHA)\s(\d+)([dD](?:4|6|8|10|12|20))\]"
)
CG_STAT_DMG_ROLL_STAT: Final[int] = 1
CG_STAT_DMG_ROLL_NUM_DICE: Final[int] = 2
CG_STAT_DMG_ROLL_DIE_TYPE: Final[int] = 3

# [<STAT> SAVE] - calculates the save DC vs the monster's <STAT>
PATTERN_STAT_SAVE_DC: Final[re.Pattern] = re.compile(
    r"\[(STR|DEX|CON|INT|WIS|CHA)\sSAVE\]"
)
CG_STAT_SAVE_DC_STAT: Final[int] = 1


# [XDY +- Z], [<STAT> ATK +- Z], [<STAT> SAVE +- Z] - Adds a static modifier to the given values
PATTERN_MODIFIED_DICE_ROLL: Final[re.Pattern] = re.compile(
    r"\[(\d+)([dD](?:4|6|8|10|12|20))\s?(\+|-)\s?(\d+)\]"
)
CG_MODIFIED_DICE_ROLL_NUM_DICE: Final[int] = 1
CG_MODIFIED_DICE_ROLL_DIE_TYPE: Final[int] = 2
CG_MODIFIED_DICE_ROLL_SIGN: Final[int] = 3
CG_MODIFIED_DICE_ROLL_MODIFIER: Final[int] = 4


PATTERN_MODIFIED_STAT_ATK_ROLL: Final[re.Pattern] = re.compile(
    r"\[(STR|DEX|CON|INT|WIS|CHA)\sATK\s?(\+|-)\s?(\d+)\]"
)
CG_MODIFIED_STAT_ATK_ROLL_STAT: Final[int] = 1
CG_MODIFIED_STAT_ATK_ROLL_SIGN: Final[int] = 2
CG_MODIFIED_STAT_ATK_ROLL_MODIFIER: Final[int] = 3


PATTERN_MODIFIED_STAT_DMG_ROLL: Final[re.Pattern] = re.compile(
    r"\[(STR|DEX|CON|INT|WIS|CHA)\s(\d+)([dD](?:4|6|8|10|12|20))\s?(\+|-)\s?(\d+)\]"
)
CG_MODIFIED_STAT_DMG_ROLL_STAT: Final[int] = 1
CG_MODIFIED_STAT_DMG_ROLL_NUM_DICE: Final[int] = 2
CG_MODIFIED_STAT_DMG_ROLL_DIE_TYPE: Final[int] = 3
CG_MODIFIED_STAT_DMG_ROLL_SIGN: Final[int] = 4
CG_MODIFIED_STAT_DMG_ROLL_MODIFIER: Final[int] = 5


PATTERN_MODIFIED_STAT_SAVE_DC: Final[re.Pattern] = re.compile(
    r"\[(STR|DEX|CON|INT|WIS|CHA)\sSAVE\s?(\+|-)\s?(\d+)\]"
)
CG_MODIFIED_STAT_SAVE_DC_STAT: Final[int] = 1
CG_MODIFIED_STAT_SAVE_DC_SIGN: Final[int] = 2
CG_MODIFIED_STAT_SAVE_DC_MODIFIER: Final[int] = 3

KEYWORD_PHRASES: Final[list[str]] = (
    [at.display_name for at in ActionType]
    + [c.display_name for c in Condition]
    + [dt.display_name for dt in DamageType]
    + [s.display_name for s in Sense]
    + [s.display_name for s in Skill]
    + [a.display_name for a in Ability]
    + [s.display_name for s in Size]
    + [ct.display_name for ct in CreatureType]
    + [da.display_name for da in DamageArea]
    + [h.display_name for h in Hazard]
    + [ct.display_name for ct in CoverType]
    + [lc.display_name for lc in LightingCondition]
    + [ol.display_name for ol in ObscurityLevel]
    + ["Hit Points", "Hit Point", "Difficult Terrain", "Advantage", "Disadvantage"]
)


def _calculate_modifier(sign: str, modifier: int) -> int:
    match sign:
        case "+":
            return abs(modifier)
        case "-":
            return -abs(modifier)
        case "natural":
            return modifier
        case _:
            raise NotImplementedError


def _substitute_dice_roll(match: re.Match) -> str:
    num_dice = int(match.group(CG_DICE_ROLL_NUM_DICE))
    die_type = Die.from_name(match.group(CG_DICE_ROLL_DIE_TYPE))
    dice = Dice({die_type: num_dice})
    return f"{dice.average_value} ({num_dice}{die_type.name.lower()})"


def _substitute_stat_modifier(ability_scores: AbilityScores, match: re.Match) -> str:
    stat = Ability.from_abbreviation(match.group(CG_STAT_MODIFIER_STAT))
    ability_modifier = calculate_ability_modifier(ability_scores.scores[stat])
    return str(ability_modifier)


def _substitute_stat_atk_roll(
    ability_scores: AbilityScores, proficiency_bonus: int, match: re.Match
) -> str:
    stat = Ability.from_abbreviation(match.group(CG_STAT_ATK_ROLL_STAT))
    ability_modifier = calculate_ability_modifier(ability_scores.scores[stat])
    total_atk_bonus = ability_modifier + proficiency_bonus
    return f"+{total_atk_bonus}" if total_atk_bonus >= 0 else str(total_atk_bonus)


def _substitute_stat_dmg_roll(ability_scores: AbilityScores, match: re.Match) -> str:
    stat = Ability.from_abbreviation(match.group(CG_STAT_DMG_ROLL_STAT))
    num_dice = int(match.group(CG_STAT_DMG_ROLL_NUM_DICE))
    die_type = Die.from_name(match.group(CG_STAT_DMG_ROLL_DIE_TYPE))
    dice = Dice({die_type: num_dice})
    ability_modifier = calculate_ability_modifier(ability_scores.scores[stat])
    total_avg_damage = dice.average_value + ability_modifier
    modifier_str = ""
    if ability_modifier > 0:
        modifier_str = f" + {ability_modifier}"
    elif ability_modifier < 0:
        modifier_str = f" - {abs(ability_modifier)}"
    return f"{total_avg_damage} ({num_dice}{die_type.name.lower()}{modifier_str})"


def _substitute_stat_save_dc(
    ability_scores: AbilityScores, proficiency_bonus: int, match: re.Match
) -> str:
    stat = Ability.from_abbreviation(match.group(CG_STAT_SAVE_DC_STAT))
    ability_modifier = _calculate_modifier("natural", ability_scores.scores[stat])
    save_dc = 8 + proficiency_bonus + ability_modifier
    return str(save_dc)


def _substitute_modified_dice_roll(match: re.Match) -> str:
    num_dice = int(match.group(CG_MODIFIED_DICE_ROLL_NUM_DICE))
    die_type = Die.from_name(match.group(CG_MODIFIED_DICE_ROLL_DIE_TYPE))
    sign = match.group(CG_MODIFIED_DICE_ROLL_SIGN)
    modifier = int(match.group(CG_MODIFIED_DICE_ROLL_MODIFIER))
    calculated_modifier = _calculate_modifier(sign, modifier)
    dice = Dice({die_type: num_dice})
    total_roll_value = dice.average_value + calculated_modifier
    return f"{total_roll_value} ({num_dice}{die_type.name.lower()} {sign} {modifier})"


def _substitute_modified_stat_atk_roll(
    ability_scores: AbilityScores, proficiency_bonus: int, match: re.Match
) -> str:
    stat = Ability.from_abbreviation(match.group(CG_MODIFIED_STAT_ATK_ROLL_STAT))
    sign = match.group(CG_MODIFIED_STAT_ATK_ROLL_SIGN)
    modifier = int(match.group(CG_MODIFIED_STAT_ATK_ROLL_MODIFIER))
    ability_modifier = calculate_ability_modifier(ability_scores.scores[stat])
    calculated_modifer = _calculate_modifier(sign, modifier)
    total_atk_bonus = ability_modifier + proficiency_bonus + calculated_modifer
    return f"+{total_atk_bonus}" if total_atk_bonus >= 0 else str(total_atk_bonus)


def _substitute_modified_stat_dmg_roll(
    ability_scores: AbilityScores, match: re.Match
) -> str:
    stat = Ability.from_abbreviation(match.group(CG_MODIFIED_STAT_DMG_ROLL_STAT))
    num_dice = int(match.group(CG_MODIFIED_STAT_DMG_ROLL_NUM_DICE))
    die_type = Die.from_name(match.group(CG_MODIFIED_DICE_ROLL_DIE_TYPE))
    sign = match.group(CG_MODIFIED_STAT_DMG_ROLL_SIGN)
    modifier = int(match.group(CG_MODIFIED_STAT_DMG_ROLL_MODIFIER))
    ability_modifier = calculate_ability_modifier(ability_scores.scores[stat])
    dice = Dice({die_type: num_dice})
    calculated_modifier = _calculate_modifier(sign, modifier)
    total_modifier = ability_modifier + calculated_modifier
    total_avg_damage = dice.average_value + total_modifier
    modifier_str = ""
    if total_modifier > 0:
        modifier_str = f" + {total_modifier}"
    elif ability_modifier < 0:
        modifier_str = f" - {abs(total_modifier)}"
    return f"{total_avg_damage} ({num_dice}{die_type.name.lower()}{modifier_str})"


def _substitute_modified_stat_save_dc(
    ability_scores: AbilityScores, proficiency_bonus: int, match: re.Match
) -> str:
    stat = Ability.from_abbreviation(match.group(CG_MODIFIED_STAT_SAVE_DC_STAT))
    sign = match.group(CG_MODIFIED_STAT_SAVE_DC_SIGN)
    modifier = int(match.group(CG_MODIFIED_STAT_SAVE_DC_MODIFIER))
    ability_modifier = calculate_ability_modifier(ability_scores.scores[stat])
    calculated_modifier = _calculate_modifier(sign, modifier)
    save_dc = 8 + proficiency_bonus + ability_modifier + calculated_modifier
    return str(save_dc)


def _replace_case_insensitive(text: str, old_phrase: str, new_phrase: str) -> str:
    return re.sub(re.escape(old_phrase), new_phrase, text, flags=re.IGNORECASE)


def format_keyword_phrases(text: str) -> str:
    new_text = copy(text)
    for keyword_phrase in KEYWORD_PHRASES:
        new_text = _replace_case_insensitive(new_text, keyword_phrase, keyword_phrase)
    return new_text


def resolve_all_macros(
    text: str, monster_name: str, ability_scores: AbilityScores, proficiency_bonus: int
) -> str:
    resolved_text = PATTERN_DICE_ROLL.sub(_substitute_dice_roll, text)
    resolved_text = PATTERN_MONSTER_NAME.sub(monster_name, resolved_text)
    resolved_text = PATTERN_STAT_MODIFIER.sub(
        partial(_substitute_stat_modifier, ability_scores), resolved_text
    )
    resolved_text = PATTERN_STAT_ATK_ROLL.sub(
        partial(_substitute_stat_atk_roll, ability_scores, proficiency_bonus),
        resolved_text,
    )
    resolved_text = PATTERN_STAT_DMG_ROLL.sub(
        partial(_substitute_stat_dmg_roll, ability_scores), resolved_text
    )
    resolved_text = PATTERN_STAT_SAVE_DC.sub(
        partial(_substitute_stat_save_dc, ability_scores, proficiency_bonus),
        resolved_text,
    )
    resolved_text = PATTERN_MODIFIED_DICE_ROLL.sub(
        _substitute_modified_dice_roll, resolved_text
    )
    resolved_text = PATTERN_MODIFIED_STAT_ATK_ROLL.sub(
        partial(_substitute_modified_stat_atk_roll, ability_scores, proficiency_bonus),
        resolved_text,
    )
    resolved_text = PATTERN_MODIFIED_STAT_DMG_ROLL.sub(
        partial(_substitute_modified_stat_dmg_roll, ability_scores), resolved_text
    )
    resolved_text = PATTERN_MODIFIED_STAT_SAVE_DC.sub(
        partial(_substitute_modified_stat_save_dc, ability_scores, proficiency_bonus),
        resolved_text,
    )
    return resolved_text
