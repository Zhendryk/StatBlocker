import re
from typing import Final
from statblocker.data.dice import Dice
from statblocker.data.enums import (
    Condition,
    DamageType,
    Sense,
    Skill,
    Ability,
    Size,
    CreatureType,
    Die,
)

PATTERN_DICE_ROLL: Final[re.Pattern] = re.compile(
    r"\[(\d{1,2})([dD][4,6,8,10,12,20])(?:\s?([\+-])\s?(\d{1,2}))?\]"
)
PATTERN_DICE_ROLL_CG_NUM_DICE: Final[int] = 1
PATTERN_DICE_ROLL_CG_DIE_TYPE: Final[int] = 2
PATTERN_DICE_ROLL_CG_SIGN: Final[int] = 3
PATTERN_DICE_ROLL_CG_BONUS: Final[int] = 4

PATTERN_STAT_OPERATION: Final[re.Pattern] = re.compile(
    r"\[(STR|DEX|CON|INT|WIS|CHA)\s(ATK|SAVE|SPELLSAVE)(?:\s?([+\-])\s?(\d+))?\]"
)
PATTERN_STAT_OPERATION_CG_STAT: Final[int] = 1
PATTERN_STAT_OPERATION_CG_OPERATION: Final[int] = 2
PATTERN_STAT_OPERATION_CG_SIGN: Final[int] = 3
PATTERN_STAT_OPERATION_CG_BONUS: Final[int] = 4

PATTERN_STAT_ATTACK: Final[re.Pattern] = re.compile(
    r"\[(STR|DEX|CON|INT|WIS|CHA)\s?(\d+)\s?([dD]\s?(?:4|6|8|10|12|20))\s?(\+|-)?\s?(\d+)?\]"
)
PATTERN_STAT_ATTACK_CG_STAT: Final[int] = 1
PATTERN_STAT_ATTACK_CG_NUM_DICE: Final[int] = 2
PATTERN_STAT_ATTACK_CG_DIE_TYPE: Final[int] = 3
PATTERN_STAT_ATTACK_CG_SIGN: Final[int] = 4
PATTERN_STAT_ATTACK_CG_BONUS: Final[int] = 5

MACRO_MONSTER_NAME: Final[str] = "[MON]"
MACRO_STR_MOD: Final[str] = "[STR]"
MACRO_DEX_MOD: Final[str] = "[DEX]"
MACRO_CON_MOD: Final[str] = "[CON]"
MACRO_INT_MOD: Final[str] = "[INT]"
MACRO_WIS_MOD: Final[str] = "[WIS]"
MACRO_CHA_MOD: Final[str] = "[CHA]"

PHRASES_TO_CAPITALIZE: Final[list[str]] = (
    [c.display_name for c in Condition]
    + [dt.display_name for dt in DamageType]
    + [s.display_name for s in Sense]
    + [s.display_name for s in Skill]
    + [a.display_name for a in Ability]
    + [s.display_name for s in Size]
    + [ct.display_name for ct in CreatureType]
)

CR_EXPERIENCE_POINTS: dict[int | float, int] = {
    0: 10,
    1 / 8: 25,
    1 / 4: 50,
    1 / 2: 100,
    1: 200,
    2: 450,
    3: 700,
    4: 1100,
    5: 1800,
    6: 2300,
    7: 2900,
    8: 3900,
    9: 5000,
    10: 5900,
    11: 7200,
    12: 8400,
    13: 10000,
    14: 11500,
    15: 13000,
    16: 15000,
    17: 18000,
    18: 20000,
    19: 22000,
    20: 25000,
    21: 33000,
    22: 41000,
    23: 50000,
    24: 62000,
    25: 75000,
    26: 90000,
    27: 105000,
    28: 120000,
    29: 135000,
    30: 155000,
}
CR_AC: dict[int | float, int] = {
    0: 10,
    1 / 8: 11,
    1 / 4: 11,
    1 / 2: 12,
    1: 12,
    2: 13,
    3: 13,
    4: 14,
    5: 15,
    6: 15,
    7: 15,
    8: 15,
    9: 16,
    10: 17,
    11: 17,
    12: 17,
    13: 18,
    14: 19,
    15: 19,
    16: 19,
    17: 20,
    18: 21,
    19: 21,
    20: 21,
    21: 22,
    22: 23,
    23: 23,
    24: 23,
    25: 24,
    26: 25,
    27: 25,
    28: 25,
    29: 26,
    30: 27,
}

CR_DPR: dict[int | float, int] = {
    0: 2,
    1 / 8: 3,
    1 / 4: 5,
    1 / 2: 10,
    1: 12,
    2: 17,
    3: 23,
    4: 29,
    5: 35,
    6: 41,
    7: 47,
    8: 53,
    9: 59,
    10: 65,
    11: 71,
    12: 77,
    13: 83,
    14: 89,
    15: 95,
    16: 101,
    17: 107,
    18: 113,
    19: 119,
    20: 132,
    21: 150,
    22: 168,
    23: 186,
    24: 204,
    25: 222,
    26: 240,
    27: 258,
    28: 276,
    29: 294,
    30: 312,
}

SPELL_DMG_BY_LEVEL_SINGLE_TARGET: dict[int, Dice] = {
    0: Dice({Die.D10: 1}),
    1: Dice({Die.D10: 2}),
    2: Dice({Die.D10: 3}),
    3: Dice({Die.D10: 5}),
    4: Dice({Die.D10: 6}),
    5: Dice({Die.D10: 7}),
    6: Dice({Die.D10: 10}),
    7: Dice({Die.D10: 11}),
    8: Dice({Die.D10: 12}),
    9: Dice({Die.D10: 15}),
}
SPELL_DMG_BY_LEVEL_MULTI_TARGET: dict[int, Dice] = {
    0: Dice({Die.D6: 1}),
    1: Dice({Die.D6: 2}),
    2: Dice({Die.D6: 3}),
    3: Dice({Die.D6: 6}),
    4: Dice({Die.D6: 7}),
    5: Dice({Die.D6: 8}),
    6: Dice({Die.D6: 11}),
    7: Dice({Die.D6: 12}),
    8: Dice({Die.D6: 13}),
    9: Dice({Die.D6: 16}),
}
