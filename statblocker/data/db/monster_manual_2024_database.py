from __future__ import annotations
import pandas as pd
from pathlib import Path
from enum import Enum, auto
from statblocker.data.enums import Size, CreatureType
from collections.abc import Sequence

MonsterDataType = str | float | int | bool | Size | CreatureType


class MM2024DBColumn(Enum):
    MONSTER_NAME = auto()
    CR = auto()
    AC = auto()
    MIN_HP = auto()
    MAX_HP = auto()
    AVG_HP = auto()
    NUMBER_OF_ATTACKS = auto()
    SIZE = auto()
    CREATURE_TYPE = auto()
    STR = auto()
    DEX = auto()
    CON = auto()
    INT = auto()
    WIS = auto()
    CHA = auto()
    LEGENDARY = auto()
    SWARM = auto()

    @staticmethod
    def from_column_str(column_str: str) -> MM2024DBColumn:
        ctype = next((ct for ct in MM2024DBColumn if ct.column_str == column_str), None)
        if ctype is None:
            raise ValueError
        return ctype

    @property
    def column_str(self) -> str:
        match self:
            case MM2024DBColumn.MONSTER_NAME:
                return "Monster Name"
            case MM2024DBColumn.CR:
                return "CR"
            case MM2024DBColumn.AC:
                return "AC"
            case MM2024DBColumn.MIN_HP:
                return "Min HP"
            case MM2024DBColumn.MAX_HP:
                return "Max HP"
            case MM2024DBColumn.AVG_HP:
                return "Avg HP"
            case MM2024DBColumn.NUMBER_OF_ATTACKS:
                return "Number of Attacks"
            case MM2024DBColumn.SIZE:
                return "Size"
            case MM2024DBColumn.CREATURE_TYPE:
                return "Creature Type"
            case MM2024DBColumn.STR:
                return "STR"
            case MM2024DBColumn.DEX:
                return "DEX"
            case MM2024DBColumn.CON:
                return "CON"
            case MM2024DBColumn.INT:
                return "INT"
            case MM2024DBColumn.WIS:
                return "WIS"
            case MM2024DBColumn.CHA:
                return "CHA"
            case MM2024DBColumn.LEGENDARY:
                return "Legendary"
            case MM2024DBColumn.SWARM:
                return "Swarm"
            case _:
                raise NotImplementedError


class OperationType(Enum):
    MEAN = auto()
    MEDIAN = auto()
    MODE = auto()
    MIN = auto()
    MAX = auto()

    @property
    def display_name(self) -> str:
        return " ".join([token.capitalize() for token in self.name.split("_")])

    @classmethod
    def from_display_name(cls, name: str) -> OperationType:
        for e in cls:
            if e.name.lower() == "_".join([c for c in name.split(" ")]).lower():
                return e
        raise ValueError(f"Invalid {cls.__name__}: {name}")


class MonsterManual2024Database:
    def __init__(self) -> None:
        self._filepath = Path(__file__).resolve().parent / "mm_2024_stats.csv"
        self._column_names = [
            "Monster Name",
            "CR",
            "AC",
            "Min HP",
            "Max HP",
            "Avg HP",
            "Number of Attacks",
            "Size",
            "Creature Type",
            "STR",
            "DEX",
            "CON",
            "INT",
            "WIS",
            "CHA",
            "Legendary",
            "Swarm",
        ]
        self._df = self._read_monster_csv(self._filepath)
        if self._df is None:
            raise RuntimeError

    def _read_monster_csv(self, file_path: str) -> pd.DataFrame | None:
        """
        Reads a CSV file containing monster data and ensures correct data types.

        :param file_path: Path to the CSV file.
        :return: Pandas DataFrame with the correctly typed monster data.
        """
        try:
            df = pd.read_csv(
                file_path,
                dtype={column_name: "string" for column_name in self._column_names},
            )

            # Convert to correct types manually to handle errors
            for column in self._column_names:
                match column:
                    case "Monster Name":
                        df[column] = df[column].astype(str)
                    case "CR":
                        df[column] = df[column].astype(float)
                    case "AC":
                        df[column] = df[column].astype(int)
                    case (
                        "Min HP"
                        | "Max HP"
                        | "Avg HP"
                        | "Number of Attacks"
                        | "STR"
                        | "DEX"
                        | "CON"
                        | "INT"
                        | "WIS"
                        | "CHA"
                    ):
                        df[column] = df[column].astype(int)
                    case "Legendary" | "Swarm":
                        df[column] = (
                            df[column]
                            .astype(str)
                            .str.lower()
                            .map({"1": True, "0": False})
                        )
                    case "Size":
                        df[column] = df[column].apply(
                            lambda cell: [
                                Size.from_display_name(s.strip())
                                for s in cell.split(",")
                            ]
                        )
                    case "Creature Type":
                        df[column] = df[column].apply(
                            lambda cell: [
                                CreatureType.from_display_name(ct.strip())
                                for ct in cell.split(",")
                            ]
                        )
                    case _:
                        raise NotImplementedError
            return df
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return None

    def query(
        self,
        filters: dict[str | MM2024DBColumn, MonsterDataType],
        aggregate_column_name: str,
        operation: OperationType = OperationType.MEAN,
    ) -> tuple[float, int]:
        query_df = self._df.copy()
        filters = {
            (k if isinstance(k, str) else k.column_str): v for k, v in filters.items()
        }
        groupby_list = [col for col in filters]
        # Explode any entries in the queried columns if they belong to multiple values
        for col in groupby_list:
            query_df[col] = query_df[col].apply(
                lambda v: v if isinstance(v, list) else [v]
            )
        for col in groupby_list:
            query_df = query_df.explode(col)
        aggregate_column_name = (
            aggregate_column_name
            if isinstance(aggregate_column_name, str)
            else aggregate_column_name.column_str
        )
        aggregation = query_df.groupby(groupby_list)[aggregate_column_name]
        calculated = getattr(aggregation, operation.name.lower())()
        sample_size = calculated.count()
        # Ensure filter values match the actual types in the grouped index
        index_values = []
        for col in groupby_list:
            col_dtype = query_df[col].explode().dropna().infer_objects().dtype
            val = filters[col]
            if pd.api.types.is_numeric_dtype(col_dtype):
                val = float(val)
            else:
                val = str(val)
            index_values.append(val)
        index_key = tuple(index_values)
        if index_key in calculated.index:
            return calculated.loc[index_key], sample_size
        else:
            raise KeyError(
                f"No data found for filters {filters}. Tried index {index_key}"
            )

    @property
    def column_names(self) -> Sequence[str]:
        return self._column_names


db = MonsterManual2024Database()
